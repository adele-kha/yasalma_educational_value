"""Pinned, resumable reference recovery and FineWeb/plain–crawl/Markdown pairing.

Stages never call an LLM. Large documents and checkpoints live under data/.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib

from huggingface_hub import HfApi, HfFileSystem, hf_hub_download
import pyarrow as pa
import pyarrow.parquet as pq
from rapidfuzz.fuzz import ratio

from text_utils import ReferenceGuard, canonical, digest, fast_markdown, url_key, visible_markdown

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


def packed(value):
    return zlib.compress(json.dumps(value, ensure_ascii=False).encode(), level=1)


def unpacked(value):
    return json.loads(zlib.decompress(value))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)


def read_json(path):
    return json.loads(path.read_text())


def connect(path):
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=NORMAL')
    return db


def remote_batches(repo, revision, path, batch_size, columns=None):
    # Range reads and bounded Arrow batches, not load_dataset(..., streaming=False).
    fs = HfFileSystem()
    with fs.open(f'datasets/{repo}@{revision}/{path}', 'rb', block_size=2**20) as handle:
        pf = pq.ParquetFile(handle)
        offset = 0
        for batch in pf.iter_batches(batch_size=batch_size, columns=columns):
            yield offset, batch
            offset += batch.num_rows


def discover(policy):
    data = BASE/'data'
    data.mkdir(exist_ok=True)
    reference = pq.read_table(ROOT/policy['reference_path']).to_pylist()
    refs = {r['id']: r for r in reference}
    if len(refs) != len(reference):
        raise ValueError('Reference IDs are not unique')
    api = HfApi()
    repositories = {}
    for key in ('reference', 'fineweb', 'crawl'):
        info = api.dataset_info(policy[key+'_repo'], revision=policy[key+'_revision'], files_metadata=True)
        repositories[key] = dict(repo=info.id, revision=info.sha,
                                 files=[dict(path=f.rfilename, bytes=f.size) for f in info.siblings
                                        if (key == 'crawl' and f.rfilename.endswith('.parquet'))
                                        or (key == 'fineweb' and f.rfilename in policy['fineweb_paths'])
                                        or (key == 'reference' and f.rfilename in (policy['metadata_path'], 'metadata/source-manifest.json', 'metadata/README.md'))])
    source_hash = hashlib.sha256((ROOT/policy['reference_path']).read_bytes()).hexdigest()
    manifest = dict(policy=policy, reference_sha256=source_hash, reference_rows=len(refs), repositories=repositories)
    existing = data/'manifest.json'
    if existing.exists() and read_json(existing) != manifest:
        raise ValueError('Inputs/policy differ from checkpoint; use a separate mapping folder or restore the recorded policy')
    write_json(existing, manifest)
    metadata_file = hf_hub_download(policy['reference_repo'], policy['metadata_path'],
                                    repo_type='dataset', revision=policy['reference_revision'])
    selected = []
    pf = pq.ParquetFile(metadata_file)
    for batch in pf.iter_batches(batch_size=policy['batch_size']):
        for row in batch.to_pylist():
            if row['id'] not in refs:
                continue
            original = refs[row['id']]
            for field in ('text', 'educational_value_labels', 'annotator_ids'):
                if original[field] != row[field]:
                    raise ValueError(f'Upstream reference changed: {row["id"]}, {field}')
            selected.append(row)
    if {row['id'] for row in selected} != set(refs):
        raise ValueError('Enriched export does not cover every local reference ID')
    pq.write_table(pa.Table.from_pylist(selected, schema=pf.schema_arrow), data/'reference_metadata.parquet')
    for filename in ('metadata/README.md', 'metadata/source-manifest.json', 'metadata/columns.md'):
        file = hf_hub_download(policy['reference_repo'], filename, repo_type='dataset', revision=policy['reference_revision'])
        (data/Path(filename).name).write_bytes(Path(file).read_bytes())
    summary = dict(reference_rows=len(refs), reference_sha256=source_hash,
                   upstream_join_status=dict(Counter(r['join_status'] for r in selected)),
                   upstream_full_fineweb_status=dict(Counter(r['fineweb2_status'] for r in selected)),
                   historical_source_datasets=sorted({r['metadata_dataset'] for r in selected if r['metadata_dataset']}),
                   known_source_text_changes=sum(r['metadata_quote_matches_annotation'] is False for r in selected),
                   known_full_corpus_text_changes=sum(r['fineweb2_quote_matches_annotation'] is False for r in selected),
                   repositories=repositories)
    write_json(BASE/'reports/discovery.json', summary)
    print('Discovery:', json.dumps({k:v for k,v in summary.items() if k != 'repositories'}), flush=True)


def reference_inputs():
    rows = pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist()
    variants = set()
    urls = defaultdict(set)
    for row in rows:
        for field in ('text', 'source_text', 'fineweb2_text'):
            if row.get(field):
                variants.add((row['id'], canonical(row[field])))
        for field in ('source_url', 'fineweb2_url'):
            key = url_key(row.get(field))
            if key:
                urls[key].add(row['id'])
    return rows, sorted(variants), urls


def index_fineweb(policy):
    db = connect(BASE/'data/fineweb.sqlite')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS fw (key TEXT PRIMARY KEY, id TEXT, url TEXT, url_key TEXT,
        partition TEXT, hash TEXT, length INTEGER, payload BLOB);
      CREATE TABLE IF NOT EXISTS progress (file TEXT PRIMARY KEY, next_row INTEGER, complete INTEGER);
      CREATE TABLE IF NOT EXISTS ref_candidates (reference_id TEXT, fw_key TEXT, method TEXT,
        PRIMARY KEY(reference_id, fw_key));
    ''')
    _, variants, _ = reference_inputs()
    guard = ReferenceGuard(variants, policy)
    for path in policy['fineweb_paths']:
        progress = db.execute('SELECT next_row,complete FROM progress WHERE file=?', (path,)).fetchone()
        if progress and progress[1]:
            print('FineWeb already indexed:', path, flush=True)
            continue
        resume = progress[0] if progress else 0
        partition = 'test' if '/test/' in path else 'removed' if '_removed/' in path else 'retained'
        for offset, batch in remote_batches(policy['fineweb_repo'], policy['fineweb_revision'], path, policy['batch_size']):
            if offset + len(batch) <= resume:
                continue
            inserts, links = [], []
            for position, record in enumerate(batch.to_pylist()):
                row_number = offset + position
                if row_number < resume:
                    continue
                text = canonical(record.get('text') or '')
                key = path+':'+str(row_number)
                record['_parquet_path'] = path
                record['_row_number'] = row_number
                inserts.append((key, record['id'], record.get('url'), url_key(record.get('url')),
                                partition, digest(text), len(text), packed(record)))
                hits = guard.matches(text)
                for reference_id in hits:
                    method = 'canonical_exact' if reference_id in guard.hashes.get(digest(text), ()) else 'near_candidate_for_exclusion'
                    links.append((reference_id, key, method))
            db.executemany('INSERT OR REPLACE INTO fw VALUES (?,?,?,?,?,?,?,?)', inserts)
            db.executemany('INSERT OR REPLACE INTO ref_candidates VALUES (?,?,?)', links)
            db.execute('INSERT OR REPLACE INTO progress VALUES (?,?,0)', (path, offset+len(batch)))
            db.commit()
            if offset // 10000 != (offset+len(batch)) // 10000:
                print(f'FineWeb {partition}: {offset+len(batch):,} rows indexed', flush=True)
        db.execute('UPDATE progress SET complete=1 WHERE file=?', (path,))
        db.commit()
    db.executescript('CREATE INDEX IF NOT EXISTS fw_url ON fw(url_key); CREATE INDEX IF NOT EXISTS fw_hash ON fw(hash);')
    db.commit()
    _, variants, urls = reference_inputs()
    # Expanded source variants protect changed later versions as well as original labels.
    for ref, blob in db.execute('SELECT r.reference_id,f.payload FROM ref_candidates r JOIN fw f ON f.key=r.fw_key'):
        row = unpacked(blob)
        variants.append((ref, canonical(row['text'])))
        key = url_key(row.get('url'))
        if key:
            urls[key].add(ref)
    if policy['reserve_fineweb_test']:
        for id_, key, blob in db.execute("SELECT id,url_key,payload FROM fw WHERE partition='test'"):
            marker = '__fineweb_test__:'+id_
            variants.append((marker, canonical(unpacked(blob)['text'])))
            if key:
                urls[key].add(marker)
    state = dict(variants=sorted(set(variants)), urls={key:sorted(value) for key,value in urls.items()})
    (BASE/'data/guard.json.zlib').write_bytes(packed(state))
    print('FineWeb indexed:', dict(db.execute('SELECT partition,count(*) FROM fw GROUP BY partition')), flush=True)
    db.close()


def scan_file(task):
    file, policy = task
    path = file['path']
    stem = Path(path).stem
    output = BASE/'data/crawl_shards'/f'{stem}.sqlite'
    output.parent.mkdir(exist_ok=True)
    db = connect(output)
    db.executescript('''
      CREATE TABLE IF NOT EXISTS pairs (key TEXT PRIMARY KEY, id TEXT, url TEXT, url_key TEXT,
        source TEXT, length INTEGER, hash TEXT, fw_key TEXT, status TEXT, evidence TEXT, markdown BLOB, priority TEXT);
      CREATE TABLE IF NOT EXISTS excluded (key TEXT PRIMARY KEY, id TEXT, url TEXT, reference_ids TEXT,
        reasons TEXT, markdown BLOB);
      CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY, next_row INTEGER, complete INTEGER, summary TEXT);
    ''')
    checkpoint = db.execute('SELECT next_row,complete,summary FROM checkpoint WHERE id=1').fetchone()
    if checkpoint and checkpoint[1]:
        db.close()
        return json.loads(checkpoint[2])
    resume = checkpoint[0] if checkpoint else 0
    summary = json.loads(checkpoint[2]) if checkpoint else dict(path=path, rows=0, statuses={}, sources={}, lengths={})
    statuses = Counter(summary['statuses']); sources = Counter(summary['sources']); lengths = Counter(summary['lengths'])
    fw = sqlite3.connect(f'file:{BASE}/data/fineweb.sqlite?mode=ro', uri=True)
    fw_urls = {row[0] for row in fw.execute('SELECT DISTINCT url_key FROM fw WHERE url_key IS NOT NULL')}
    state = unpacked((BASE/'data/guard.json.zlib').read_bytes())
    guard = ReferenceGuard(state['variants'], policy)
    protected_urls = state['urls']
    for offset, batch in remote_batches(policy['crawl_repo'], policy['crawl_revision'], path, policy['batch_size']):
        if offset+len(batch) <= resume:
            continue
        inserts, exclusions = [], []
        for position, record in enumerate(batch.to_pylist()):
            row_number = offset+position
            if row_number < resume:
                continue
            summary['rows'] += 1
            source = record.get('source') or '<missing>'
            sources[source] += 1
            key = path+':'+str(row_number)
            text = record.get('text')
            if not isinstance(text, str) or not text.strip():
                statuses['invalid_text'] += 1
                continue
            cheap = fast_markdown(text)
            length_group = '<500' if len(cheap)<500 else '500–1999' if len(cheap)<2000 else '2000–7999' if len(cheap)<8000 else '8000+'
            lengths[length_group] += 1
            normalized_url = url_key(record.get('url'))
            text_hits = guard.matches(cheap)
            hits = set(protected_urls.get(normalized_url, ())) | set(text_hits)
            reasons = []
            if protected_urls.get(normalized_url): reasons.append('protected_reference_or_fineweb_test_url')
            if text_hits: reasons.append('reference_or_test_text_exact_or_anchor_near')
            if hits:
                statuses['excluded_reference_or_test'] += 1
                exclusions.append((key, record.get('id'), record.get('url'), json.dumps(sorted(hits)), json.dumps(reasons), packed(record)))
                continue
            if not normalized_url or normalized_url not in fw_urls:
                statuses['no_fineweb_url_candidate'] += 1
                continue
            candidates = fw.execute('SELECT key,hash,length,payload FROM fw WHERE url_key=? ORDER BY key', (normalized_url,)).fetchall()
            visible = visible_markdown(text)
            strict_hits = guard.matches(visible)
            if strict_hits:
                statuses['excluded_reference_or_test'] += 1
                exclusions.append((key, record.get('id'), record.get('url'), json.dumps(strict_hits), json.dumps(['parsed_markdown_reference_or_test_text']), packed(record)))
                continue
            hashed = digest(visible)
            exact = [candidate for candidate in candidates if candidate[1] == hashed and visible]
            best_score = 0
            best = None
            if exact:
                status = 'exact_visible_tokens'
                best = exact[0]
                evidence = dict(method=status, similarity=1.0, equivalent_fineweb_records=len(exact), url_candidates=len(candidates))
            else:
                for candidate in candidates:
                    if not visible or min(len(visible),candidate[2])/max(len(visible),candidate[2],1) < policy['review_length_ratio']:
                        continue
                    score = ratio(visible, canonical(unpacked(candidate[3])['text']), score_cutoff=policy['review_similarity']*100)/100
                    if score > best_score:
                        best_score, best = score, candidate
                status = 'near_requires_review' if best is not None else 'url_content_mismatch'
                evidence = dict(method=status, similarity=best_score, url_candidates=len(candidates))
            statuses[status] += 1
            if status == 'exact_visible_tokens' or statuses[status] <= policy['audit_per_status_per_file']:
                record['_parquet_path'] = path; record['_row_number'] = row_number
                priority = digest(f'{policy["seed"]}|{hashed}|{normalized_url}')
                inserts.append((key, record.get('id'), record.get('url'), normalized_url, source, len(visible), hashed,
                                best[0] if best else candidates[0][0], status, json.dumps(evidence), packed(record), priority))
        db.executemany('INSERT OR REPLACE INTO pairs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', inserts)
        db.executemany('INSERT OR REPLACE INTO excluded VALUES (?,?,?,?,?,?)', exclusions)
        summary.update(statuses=dict(statuses), sources=dict(sources), lengths=dict(lengths))
        db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1,?,0,?)', (offset+len(batch), json.dumps(summary)))
        db.commit()
        if offset//50000 != (offset+len(batch))//50000:
            print(f'Crawl {stem}: {offset+len(batch):,} rows; {statuses["exact_visible_tokens"]:,} eligible pairs', flush=True)
    db.execute('UPDATE checkpoint SET complete=1 WHERE id=1'); db.commit()
    write_json(output.with_suffix('.json'), summary)
    db.close(); fw.close()
    print(f'Completed {stem}: {summary["rows"]:,} rows; {statuses["exact_visible_tokens"]:,} eligible pairs', flush=True)
    return summary


def scan_crawl(policy):
    manifest = read_json(BASE/'data/manifest.json')
    db = sqlite3.connect(BASE/'data/fineweb.sqlite')
    complete = {row[0] for row in db.execute('SELECT file FROM progress WHERE complete=1')}
    db.close()
    if complete != set(policy['fineweb_paths']):
        raise ValueError('FineWeb index is incomplete; finish the index stage first')
    files = manifest['repositories']['crawl']['files']
    with ProcessPoolExecutor(max_workers=policy['workers']) as executor:
        futures = [executor.submit(scan_file, (file,policy)) for file in files]
        for future in as_completed(futures):
            future.result()


def quarantine(rows, exclusions):
    """Transitive quarantine over candidate IDs, URLs and canonical content hashes."""
    protected_ids = defaultdict(set); protected_urls = defaultdict(set); protected_hashes = defaultdict(set)
    def protect(id_, url, hashed, references):
        if id_: protected_ids[id_].update(references)
        normalized = url_key(url)
        if normalized: protected_urls[normalized].update(references)
        protected_hashes[hashed].update(references)
    for row in exclusions:
        protect(row['id'], row['url'], row['canonical_sha256'], row['reference_ids'])
    pending = rows
    added = []
    while True:
        kept = []
        changed = False
        for row in pending:
            hits = set(protected_ids.get(row['id'], ())) | set(protected_urls.get(row['url_key'], ())) | set(protected_hashes.get(row['hash'], ()))
            if not hits:
                kept.append(row)
                continue
            changed = True
            protect(row['id'], row['url'], row['hash'], hits)
            added.append(dict(key=row['key'], id=row['id'], url=row['url'], reference_ids=sorted(hits),
                              reasons=['post_scan_id_url_or_exact_content_quarantine'], canonical_sha256=row['hash']))
        if not changed:
            return kept, added
        pending = kept


def finalize(policy):
    shards = sorted((BASE/'data/crawl_shards').glob('*.sqlite'))
    expected = len(read_json(BASE/'data/manifest.json')['repositories']['crawl']['files'])
    if len(shards) != expected:
        raise ValueError('Crawl scan incomplete')
    all_rows = []; reports = []; exclusions = []; audits = []; ref_pairs = []
    refs = {r['id']: r for r in pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist()}
    for shard in shards:
        db = sqlite3.connect(shard); db.row_factory = sqlite3.Row
        progress = db.execute('SELECT complete,summary FROM checkpoint WHERE id=1').fetchone()
        if not progress or not progress['complete']:
            raise ValueError(f'Incomplete shard: {shard.name}')
        reports.append(json.loads(progress['summary']))
        for row in db.execute("SELECT key,id,url,url_key,source,length,hash,fw_key,priority FROM pairs WHERE status='exact_visible_tokens'"):
            all_rows.append(dict(row, shard=str(shard)))
        for row in db.execute('SELECT key,id,url,reference_ids,reasons,markdown FROM excluded'):
            item = dict(row)
            original = unpacked(item.pop('markdown'))
            item['canonical_sha256'] = digest(visible_markdown(original['text']))
            item['reference_ids'] = json.loads(item['reference_ids']); item['reasons'] = json.loads(item['reasons'])
            exclusions.append(item)
        for row in db.execute("SELECT key,id,url,fw_key,status,evidence FROM pairs WHERE status!='exact_visible_tokens'"):
            audits.append(dict(row, shard=str(shard)))
        db.close()
    # Close over the entire scan before selection: an overlap discovered late in
    # one shard also quarantines earlier records sharing its ID, URL or content.
    before_quarantine = len(all_rows)
    all_rows, additional_exclusions = quarantine(all_rows, exclusions)
    exclusions.extend(additional_exclusions)
    all_rows.sort(key=lambda row:(row['hash'],row['url_key'],row['key']))
    unique = {}; duplicates = 0
    for row in all_rows:
        if row['hash'] in unique:
            duplicates += 1
        else:
            unique[row['hash']] = row
    pool = list(unique.values())
    fw = sqlite3.connect(BASE/'data/fineweb.sqlite')
    inventory = []
    for row in pool:
        fineweb_id,partition = fw.execute('SELECT id,partition FROM fw WHERE key=?',(row['fw_key'],)).fetchone()
        crawl_file,crawl_row=row['key'].rsplit(':',1)
        inventory.append(dict(crawl_res_id=row['id'],fineweb_id=fineweb_id,url=row['url'],url_key=row['url_key'],
                              source=row['source'],canonical_length=row['length'],canonical_text_sha256=row['hash'],
                              fineweb_key=row['fw_key'],fineweb_partition=partition,
                              crawl_file=crawl_file,crawl_row=int(crawl_row),
                              match_method='exact_visible_tokens'))
    if inventory:
        pq.write_table(pa.Table.from_pylist(inventory),BASE/'data/eligible_pairs.parquet',compression='zstd')
    if exclusions:
        pq.write_table(pa.Table.from_pylist(exclusions),BASE/'data/exclusions.parquet',compression='zstd')
    if audits:
        pq.write_table(pa.Table.from_pylist(audits),BASE/'data/pair_audit.parquet',compression='zstd')
    for shard in shards:
        db=sqlite3.connect(shard)
        for key,id_,url,reference_ids,blob in db.execute('SELECT key,id,url,reference_ids,markdown FROM excluded'):
            markdown=unpacked(blob)
            for ref in json.loads(reference_ids):
                if ref not in refs: continue
                original=refs[ref]
                exact=canonical(original['text'])==visible_markdown(markdown['text'])
                ref_pairs.append(dict(reference_id=ref,crawl_res_id=id_,url=url,reference_text=original['text'],
                                      text_markdown=markdown['text'],human_labels=original['educational_value_labels'],
                                      content_equivalent=exact,label_transfer_allowed=exact,
                                      canonical_similarity=ratio(canonical(original['text']),visible_markdown(markdown['text']))/100,
                                      crawl_locator=key,split='reference_evaluation'))
        db.close()
    if ref_pairs:
        pq.write_table(pa.Table.from_pylist(ref_pairs),BASE/'data/reference_pairs.parquet',compression='zstd')
    ref_mapping=[]
    for ref,row in refs.items():
        candidates=[dict(fineweb_key=k,method=m) for k,m in fw.execute('SELECT fw_key,method FROM ref_candidates WHERE reference_id=?',(ref,))]
        ref_mapping.append(dict(reference_id=ref,upstream_join_status=row['join_status'],upstream_method=row['join_method'],
                                source_id=row['source_id'],source_url=row['source_url'],source_dataset=row['metadata_dataset'],
                                source_revision=row['metadata_revision'],source_file=row['metadata_parquet_path'],source_row=row['metadata_row_number'],
                                source_text_matches=canonical(row['text'])==canonical(row['source_text']) if row['source_text'] else None,
                                fineweb2_status=row['fineweb2_status'],fineweb2_id=row['fineweb2_source_id'],fineweb2_url=row['fineweb2_url'],
                                fineweb2_revision=row['fineweb2_revision'],fineweb2_file=row['fineweb2_parquet_path'],fineweb2_row=row['fineweb2_row_number'],
                                checked_candidates=candidates))
    pq.write_table(pa.Table.from_pylist(ref_mapping),BASE/'data/reference_mapping.parquet',compression='zstd')
    totals=Counter(); source_counts=Counter(); length_counts=Counter()
    for report in reports:
        totals.update(report['statuses']);source_counts.update(report['sources']);length_counts.update(report['lengths'])
    def fixed_length_group(length):
        return '<500' if length<500 else '500–1999' if length<2000 else '2000–7999' if length<8000 else '8000+'
    summary=dict(created_at=datetime.now(timezone.utc).isoformat(),manifest=read_json(BASE/'data/manifest.json'),
                 crawl_rows=sum(r['rows'] for r in reports),pair_status_counts=dict(totals),
                 crawl_sources=dict(source_counts),crawl_canonical_length_groups=dict(length_counts),
                 unique_exact_canonical_length_groups=dict(Counter(fixed_length_group(r['length']) for r in pool)),
                 exact_pair_sources=dict(Counter(r['source'] for r in all_rows)),unique_exact_pair_sources=dict(Counter(r['source'] for r in pool)),
                 exact_pair_rows=len(all_rows),unique_exact_content_pairs=len(pool),duplicate_pair_rows=duplicates,
                 exact_pair_rows_before_quarantine=before_quarantine,post_scan_quarantine_rows=before_quarantine-len(all_rows),
                 exclusions=len(exclusions),reference_documents_with_crawl_hits=len({r['reference_id'] for r in ref_pairs}),
                 reference_documents_with_equivalent_markdown=len({r['reference_id'] for r in ref_pairs if r['content_equivalent']}),
                 reference_rows=len(refs),reference_upstream_unresolved=sum(r['join_status']!='matched' for r in refs.values()),
                 annotation_selection_status='not_selected_awaiting_user_policy',
                 limitations=[
                   'Only Tatar Cyrillic retained/train, retained/test and removed/train in the pinned FineWeb release were searched; historical recovery uses the pinned upstream metadata export.',
                   'Training acceptance requires identical normalized visible word/number sequences, not just a URL match. Punctuation/casing/Unicode presentation are normalized; images and their semantics are not evaluated.',
                   'Near-equivalent pairs are audit candidates only and are not included in the exact-pair inventory.',
                   'Reference near-duplicate screening uses a finite anchor set and similarity threshold; it is approximate and cannot prove absence of every transformed duplicate.',
                   'The inventory groups exact canonical-content duplicates only; near-duplicate and sampling policies between candidates have not been chosen.',
                   'The exact-pair inventory is an intersection, not a representative sample of crawl-res. No annotation subset has been selected.',
                   'All-crawl length bands use the cheap Markdown screen; paired/sample bands use fully parsed visible text. The bands are approximate screening diagnostics, not tokenizer lengths.',
                   'The existing reference set has informed model/prompt development; it is a development benchmark, not a pristine final test set.',
                   'No annotation set was selected and no LLM labels were generated.'
                 ])
    write_json(BASE/'reports/summary.json',summary)
    lines=['# FineWeb ↔ crawl-res mapping', '',
           f'Crawl rows scanned: **{summary["crawl_rows"]:,}**. Reference documents: **{len(refs):,}**.',
           f'Eligible exact-content inventory: **{len(pool):,} unique normalized texts**. No annotation subset is selected.',
           f'Excluded reference/test-related crawl records: **{len(exclusions):,}**.',
           f'Reference documents linked to crawl records: **{summary["reference_documents_with_crawl_hits"]:,}**; with equivalent Markdown: **{summary["reference_documents_with_equivalent_markdown"]:,}**.', '',
           '## Pair decisions', '', '| Status | Crawl rows |','|---|---:|']
    lines += [f'| {k} | {v:,} |' for k,v in sorted(totals.items())]
    lines += ['', '## Source coverage / selection bias', '', '| Source | All crawl rows | Unique exact paired texts |','|---|---:|---:|']
    lines += [f'| {s} | {source_counts[s]:,} | {summary["unique_exact_pair_sources"].get(s,0):,} |' for s in sorted(source_counts)]
    lines += ['', '## Canonical character-length coverage', '', '| Length band | All crawl rows (screen) | Unique exact paired texts |','|---|---:|---:|']
    lines += [f'| {band} | {length_counts[band]:,} | {summary["unique_exact_canonical_length_groups"].get(band,0):,} |' for band in ['<500','500–1999','2000–7999','8000+']]
    lines += ['', '## Limitations', ''] + ['- '+item for item in summary['limitations']]
    lines += ['', 'Raw text, pair tables, exclusions, audit candidates and resumable SQLite checkpoints are in ignored `mapping/data/`. Full policy, pinned revisions, reference SHA-256 and aggregate counts are in `summary.json`.']
    (BASE/'reports/report.md').write_text('\n'.join(lines)+'\n')
    fw.close()
    print(json.dumps({k:summary[k] for k in ['crawl_rows','unique_exact_content_pairs','annotation_selection_status','exclusions','reference_documents_with_crawl_hits','reference_documents_with_equivalent_markdown']}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['discover','index','scan','finalize','all'])
    parser.add_argument('--policy',type=Path,default=BASE/'policy.json')
    args=parser.parse_args(); policy=read_json(args.policy)
    if policy['workers']<=0:
        parser.error('workers must be positive')
    (BASE/'data').mkdir(exist_ok=True); (BASE/'reports').mkdir(exist_ok=True)
    if args.stage!='discover' and (BASE/'data/manifest.json').exists():
        if read_json(BASE/'data/manifest.json')['policy']!=policy:
            parser.error('Policy differs from pinned checkpoint')
    for stage,function in [('discover',discover),('index',index_fineweb),('scan',scan_crawl),('finalize',finalize)]:
        if args.stage in (stage,'all'):
            function(policy)


if __name__=='__main__':
    main()
