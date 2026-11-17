"""Validate mapping inventories and build diagnostic-only content-review packs."""
from collections import defaultdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import sqlite3

import pyarrow as pa
import pyarrow.parquet as pq
from rapidfuzz.fuzz import ratio

from pipeline import BASE, ROOT, read_json, unpacked, write_json
from text_utils import ReferenceGuard, canonical, digest, url_key, visible_markdown


def main():
    policy=read_json(BASE/'policy.json')
    manifest=read_json(BASE/'data/manifest.json')
    assert policy==manifest['policy']
    assert hashlib.sha256((ROOT/policy['reference_path']).read_bytes()).hexdigest()==manifest['reference_sha256']
    inventory=pq.read_table(BASE/'data/eligible_pairs.parquet').to_pylist()
    assert not (BASE/'data/annotation_pool.parquet').exists()
    assert len({row['canonical_text_sha256'] for row in inventory})==len(inventory)
    state=unpacked((BASE/'data/guard.json.zlib').read_bytes())
    guard=ReferenceGuard(state['variants'],policy)
    exclusions=pq.read_table(BASE/'data/exclusions.parquet').to_pylist()
    excluded_ids={row['id'] for row in exclusions if row['id']}
    excluded_urls={url_key(row['url']) for row in exclusions if url_key(row['url'])}
    excluded_hashes={row['canonical_sha256'] for row in exclusions}
    fw=sqlite3.connect(BASE/'data/fineweb.sqlite')
    crawl_handles={}
    for row in inventory:
        assert row['crawl_res_id'] not in excluded_ids
        assert row['url_key'] not in excluded_urls
        assert row['canonical_text_sha256'] not in excluded_hashes
        assert row['url_key'] not in state['urls']
        assert row['canonical_text_sha256'] not in guard.hashes
        source_id,source_hash=fw.execute('SELECT id,hash FROM fw WHERE key=?',(row['fineweb_key'],)).fetchone()
        assert source_id==row['fineweb_id'] and source_hash==row['canonical_text_sha256']
        stem=Path(row['crawl_file']).stem
        if stem not in crawl_handles:
            crawl_handles[stem]=sqlite3.connect(BASE/'data/crawl_shards'/f'{stem}.sqlite')
        candidate=crawl_handles[stem].execute('SELECT id,hash,fw_key,status FROM pairs WHERE key=?',
                          (row['crawl_file']+':'+str(row['crawl_row']),)).fetchone()
        assert candidate==(row['crawl_res_id'],row['canonical_text_sha256'],row['fineweb_key'],'exact_visible_tokens')
    rng=random.Random(policy['seed'])
    chosen=rng.sample(inventory,min(20,len(inventory)))
    with (BASE/'data/accepted_review_pack.jsonl').open('w') as handle:
        for row in chosen:
            original=unpacked(fw.execute('SELECT payload FROM fw WHERE key=?',(row['fineweb_key'],)).fetchone()[0])
            db=crawl_handles[Path(row['crawl_file']).stem]
            markdown=unpacked(db.execute('SELECT markdown FROM pairs WHERE key=?',(row['crawl_file']+':'+str(row['crawl_row']),)).fetchone()[0])
            plain=canonical(original['text'])
            assert plain==visible_markdown(markdown['text']) and guard.matches(plain)==[]
            value=dict(row,purpose='mapping_audit_only',text_plain=original['text'],text_markdown=markdown['text'])
            handle.write(json.dumps(value,ensure_ascii=False)+'\n')
    for db in crawl_handles.values():db.close()
    refs={row['id']:row for row in pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist()}
    audit=[]; exact_ids=set(); near_only=set(); original_urls=set(); exact_urls=defaultdict(set)
    for ref,row in refs.items():
        if row['source_url']:original_urls.add(ref)
        for key,method,blob in fw.execute('SELECT r.fw_key,r.method,f.payload FROM ref_candidates r JOIN fw f ON f.key=r.fw_key WHERE r.reference_id=?',(ref,)):
            source=unpacked(blob)
            exact=canonical(row['text'])==canonical(source['text'])
            if exact:
                exact_ids.add(ref)
                exact_urls[ref].add(url_key(source.get('url')))
            else:near_only.add(ref)
            audit.append(dict(reference_id=ref,fineweb_key=key,fineweb_id=source['id'],url=source.get('url'),
                              original_annotation_canonical_exact=exact,retrieval_method=method,
                              original_annotation_raw_exact=row['text']==source['text'],
                              used_for_conservative_exclusion=True,automatic_human_label_transfer_allowed=exact))
    if audit:pq.write_table(pa.Table.from_pylist(audit),BASE/'data/reference_candidate_audit.parquet',compression='zstd')
    newly_exact=exact_ids-original_urls
    summary=dict(verified_inventory_rows=len(inventory),inventory_unique_canonical_content=True,
                 inventory_source_locators_and_hashes_verified=True,
                 inventory_id_url_and_hash_quarantine_passed=True,
                 diagnostic_full_text_pairs_checked=len(chosen),
                 annotation_selection_status='not_selected_awaiting_user_policy',
                 reference_rows=len(refs),upstream_url_recovery=len(original_urls),
                 full_corpus_original_text_exact_recovery=len(exact_ids),
                 additional_exact_recovery_beyond_upstream=sorted(newly_exact),
                 still_without_source_url_or_exact_url_candidates=sorted(set(refs)-original_urls-exact_ids),
                 reference_ids_with_multiple_canonical_exact_urls=sorted(ref for ref,urls in exact_urls.items() if len(urls)>1),
                 reference_ids_with_only_nonidentical_full_corpus_candidates=sorted(near_only-exact_ids),
                 artifact_sha256={name:hashlib.sha256((BASE/'data'/name).read_bytes()).hexdigest()
                                  for name in ['eligible_pairs.parquet','reference_mapping.parquet','reference_pairs.parquet',
                                               'exclusions.parquet','pair_audit.parquet'] if (BASE/'data'/name).exists()},
                 implementation_sha256={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                                        for name in ['pipeline.py','text_utils.py','audit.py','policy.json']},
                 package_versions={name:importlib.metadata.version(name) for name in
                                   ['pyarrow','huggingface-hub','markdown-it-py','rapidfuzz','pyahocorasick']})
    write_json(BASE/'reports/validation.json',summary)
    rejected_path=BASE/'data/pair_audit.parquet'
    if rejected_path.exists():
        rejected=defaultdict(list)
        for row in pq.read_table(rejected_path).to_pylist():rejected[row['status']].append(row)
        with (BASE/'data/rejected_review_pack.jsonl').open('w') as handle:
            for status,rows in sorted(rejected.items()):
                rng.shuffle(rows)
                for row in rows[:10]:
                    db=sqlite3.connect(row['shard'])
                    markdown=unpacked(db.execute('SELECT markdown FROM pairs WHERE key=?',(row['key'],)).fetchone()[0]);db.close()
                    source=unpacked(fw.execute('SELECT payload FROM fw WHERE key=?',(row['fw_key'],)).fetchone()[0])
                    value=dict(crawl_res_id=row['id'],fineweb_id=source['id'],url=row['url'],status=status,
                               evidence=json.loads(row['evidence']),
                               measured_canonical_similarity=ratio(canonical(source['text']),visible_markdown(markdown['text']))/100,
                               text_plain=source['text'],text_markdown=markdown['text'])
                    handle.write(json.dumps(value,ensure_ascii=False)+'\n')
    fw.close()
    print(json.dumps({key:value for key,value in summary.items() if key not in
                      ['implementation_sha256','package_versions','additional_exact_recovery_beyond_upstream',
                       'still_without_source_url_or_exact_url_candidates','reference_ids_with_multiple_canonical_exact_urls',
                       'reference_ids_with_only_nonidentical_full_corpus_candidates']},indent=2))
    print('Additional canonical-exact URL candidate links:',len(newly_exact),'; unresolved:',len(summary['still_without_source_url_or_exact_url_candidates']))


if __name__=='__main__':
    main()
