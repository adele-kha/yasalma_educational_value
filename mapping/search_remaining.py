"""Focused lexical-only recovery of golden documents missing crawl candidates.

No embeddings, semantic models, LLM calls, label transfer or annotation sampling.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import heapq
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import parse_qs, unquote, urlencode, urlsplit

import ahocorasick
import pyarrow as pa
import pyarrow.parquet as pq
from rapidfuzz.fuzz import partial_ratio, ratio

from pipeline import BASE, connect, packed, read_json, remote_batches, unpacked, write_json
from text_utils import canonical, fast_markdown, url_key, visible_markdown


def url_aliases(url):
    """Broad retrieval aliases only: never proof of content equivalence."""
    if not isinstance(url,str): return set()
    result=set()
    try:
        parsed=urlsplit(url.strip())
        host=(parsed.hostname or '').casefold().removeprefix('www.').rstrip('.')
        if not host:return result
        path=unquote(unquote(parsed.path)).rstrip('/') or '/'
        query=parse_qs(parsed.query,keep_blank_values=True)
        meaningful={k:v for k,v in query.items() if not k.casefold().startswith('utm_')
                    and k.casefold() not in {'fbclid','gclid','yclid','ref','referrer'} }
        result.add('generic:'+host+path.casefold()+'?'+urlencode(sorted((k,v) for k,vs in meaningful.items() for v in vs)))
        if host.endswith('.wikipedia.org'):
            host=host.replace('.m.wikipedia.org','.wikipedia.org')
            title=path[6:] if path.startswith('/wiki/') else query.get('title',[''])[0]
            if title:
                title=' '.join(title.replace('_',' ').split()).casefold()
                result.add('wiki:'+host+':'+title)
        node=re.search(r'(?:^|/)node/(\d+)(?:/|$)',path)
        if not node:
            node=re.search(r'(?:^|/)node/(\d+)(?:/|$)',query.get('q',[''])[0])
        if node:result.add('drupal:'+host+':'+node[1])
        for name in ('url','u','target','redirect'):
            for value in query.get(name,[]):
                if value.startswith(('http://','https://')):
                    key=url_key(value)
                    if key:result.add('wrapped:'+key)
        key=url_key(url)
        if key:result.add('wrapped:'+key)
    except (ValueError,UnicodeError):
        return set()
    return result


def prepare(output,policy):
    baseline=BASE/'data/reference_pairs.parquet'
    linked=set(pq.read_table(baseline,columns=['reference_id'])['reference_id'].to_pylist())
    references=pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist()
    targets={r['id']:dict(reference_id=r['id'],text=r['text'],human_labels=r['educational_value_labels'],
                         urls=sorted({r[k] for k in ('source_url','fineweb2_url') if r[k]}))
             for r in references if r['id'] not in linked}
    for row in pq.read_table(BASE/'data/reference_candidate_audit.parquet').to_pylist():
        if row['reference_id'] in targets and row['original_annotation_canonical_exact'] and row['url']:
            targets[row['reference_id']]['urls'].append(row['url'])
    for target in targets.values():target['urls']=sorted(set(target['urls']))
    wiki_file=BASE/'data/golden_wiki_identity.json'
    wiki=read_json(wiki_file)['references'] if wiki_file.exists() else {}
    for key,target in targets.items():
        target['original_urls']=list(target['urls'])
        target['wikipedia_page_ids']=[]
        if key in wiki and not wiki[key]['missing']:
            target['urls']=sorted(set(target['urls']+[wiki[key]['current_url']]))
            target['wikipedia_page_ids']=[wiki[key]['page_id']]
    inputs=read_json(BASE/'data/manifest.json')
    manifest=dict(policy=policy,targets=sorted(targets),baseline_linked=len(linked),
                  crawl=inputs['repositories']['crawl'],
                  input_sha256={name:hashlib.sha256((BASE/'data'/name).read_bytes()).hexdigest()
                                for name in ['reference_pairs.parquet','reference_metadata.parquet','reference_candidate_audit.parquet']},
                  implementation_sha256={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                                         for name in ['search_remaining.py','text_utils.py']})
    if wiki_file.exists():manifest['input_sha256']['golden_wiki_identity.json']=hashlib.sha256(wiki_file.read_bytes()).hexdigest()
    output.mkdir(parents=True,exist_ok=True)
    path=output/'manifest.json'
    if path.exists() and read_json(path)!=manifest:
        raise ValueError('Search inputs/code/policy changed; choose another --output-dir')
    write_json(path,manifest)
    write_json(output/'targets.json',[targets[k] for k in sorted(targets)])
    return manifest


class LexicalSearch:
    def __init__(self,targets,policy):
        self.policy=policy;self.targets={r['reference_id']:r for r in targets}
        self.normal={key:canonical(r['text']) for key,r in self.targets.items()}
        self.compact={key:text.replace(' ','') for key,text in self.normal.items()}
        self.counts={key:Counter(text.split()) for key,text in self.normal.items()}
        self.urls=defaultdict(set)
        self.page_ids=defaultdict(set)
        for key,r in self.targets.items():
            for page_id in r.get('wikipedia_page_ids',[]):self.page_ids['ttwiki/'+str(page_id)].add(key)
            for url in r['urls']:
                for alias in url_aliases(url):self.urls[alias].add(key)
        anchors=defaultdict(set); token_refs=defaultdict(set)
        width=policy['anchor_chars'];stride=policy['anchor_stride']
        for key,text in self.compact.items():
            for start in range(0,max(1,len(text)-width+1),stride):
                anchor=text[start:start+width]
                if len(anchor)==width:anchors[anchor].add(key)
        for key,counts in self.counts.items():
            for token in counts:
                if len(token)>=policy['rare_token_min_chars'] and not token.isdigit():token_refs[token].add(key)
        self.keywords=defaultdict(set)
        for key,counts in self.counts.items():
            eligible=[word for word in counts if word in token_refs and len(token_refs[word])<=policy['max_rare_token_reference_frequency']]
            for word in sorted(eligible,key=lambda word:(-len(word),word))[:policy['rare_token_limit']]:
                self.keywords[word].add(key)
        self.anchor_counts=Counter();self.automaton=ahocorasick.Automaton()
        for index,(anchor,ids) in enumerate(sorted(anchors.items())):
            if len(ids)>policy['max_anchor_reference_frequency']:continue
            self.automaton.add_word(anchor,(index,tuple(sorted(ids))))
            self.anchor_counts.update(ids)
        self.automaton.make_automaton()

    def retrieve(self,raw,url,crawl_id=None):
        cheap=fast_markdown(raw);compact=cheap.replace(' ','')
        anchor_hits=defaultdict(set)
        representations={compact,canonical(raw).replace(' ','')}
        for representation in representations:
            if len(self.automaton):
                for _,(anchor,ids) in self.automaton.iter(representation):
                    for key in ids:anchor_hits[key].add(anchor)
        rare_hits=Counter()
        for word in set(cheap.split()):rare_hits.update(self.keywords.get(word,()))
        urls=set()
        for alias in url_aliases(url):urls.update(self.urls.get(alias,()))
        candidates=urls | {key for key,hits in anchor_hits.items() if len(hits)>=self.policy['min_anchor_hits']}
        candidates|={key for key,n in rare_hits.items() if n>=self.policy['min_rare_token_hits']}
        identity=set(self.page_ids.get(crawl_id,()))
        candidates.update(identity)
        return candidates,urls,anchor_hits,rare_hits,identity

    def score(self,raw,url,crawl_id=None):
        candidates,url_hits,anchor_hits,rare_hits,identity_hits=self.retrieve(raw,url,crawl_id)
        if not candidates:return [],url_hits
        visible=visible_markdown(raw);compact=visible.replace(' ','');doc_counts=Counter(visible.split())
        result=[];p=self.policy
        for key in sorted(candidates):
            normal=self.normal[key];ref_compact=self.compact[key]
            shared=sum((doc_counts & self.counts[key]).values())
            ref_tokens=sum(self.counts[key].values());doc_tokens=sum(doc_counts.values())
            ref_coverage=shared/max(1,ref_tokens);doc_coverage=shared/max(1,doc_tokens)
            dice=2*shared/max(1,ref_tokens+doc_tokens)
            anchor_coverage=len(anchor_hits[key])/max(1,self.anchor_counts[key])
            if key not in url_hits and key not in identity_hits and ref_coverage<p['weak_token_coverage'] and anchor_coverage<p['partial_min_anchor_coverage'] and ref_compact!=compact:
                continue
            cutoff=0 if key in url_hits or key in identity_hits else p['weak_character_similarity']*100
            char_score=ratio(normal,visible,score_cutoff=cutoff)/100
            compact_score=ratio(ref_compact,compact,score_cutoff=cutoff)/100
            contained=bool(ref_compact) and ref_compact in compact
            partial=None
            if not contained and compact!=ref_compact and (key in url_hits or (ref_coverage>=p['partial_reference_token_coverage'] and anchor_coverage>=p['partial_min_anchor_coverage'])) and max(len(normal),len(visible))<=p['max_partial_metric_chars']:
                partial=partial_ratio(normal,visible,score_cutoff=p['partial_metric_score_cutoff']*100)/100
            if normal==visible and normal: tier='exact_visible';rank=6
            elif ref_compact==compact and ref_compact:tier='exact_compact';rank=5
            elif key in identity_hits:tier='wikipedia_page_identity_review';rank=5
            elif contained and len(ref_compact)>=p['anchor_chars']*3:tier='reference_contained';rank=4
            elif max(char_score,compact_score)>=p['high_character_similarity'] and dice>=p['high_token_dice']:
                tier='high_lexical';rank=4
            elif max(char_score,compact_score)>=p['near_character_similarity'] and dice>=p['near_token_dice']:
                tier='near_lexical_review';rank=3
            elif dice>=p['reordered_token_dice'] and anchor_coverage>=p['reordered_anchor_coverage']:
                tier='reordered_lexical_review';rank=3
            elif partial is not None and partial>=p['partial_similarity'] and ref_coverage>=p['partial_reference_token_coverage'] and anchor_coverage>=p['partial_min_anchor_coverage']:
                tier='partial_lexical_review';rank=3
            elif key in url_hits:tier='url_alias_content_review';rank=2
            elif max(char_score,compact_score)>=p['weak_character_similarity'] and ref_coverage>=p['weak_token_coverage']:
                tier='weak_lexical_candidate';rank=1
            else:continue
            evidence=dict(tier=tier,tier_rank=rank,character_similarity=char_score,compact_similarity=compact_score,
                          token_dice=dice,reference_token_coverage=ref_coverage,document_token_coverage=doc_coverage,
                          distinct_anchor_hits=len(anchor_hits[key]),reference_anchor_coverage=anchor_coverage,
                          rare_token_hits=rare_hits[key],url_alias_match=key in url_hits,
                          wikipedia_page_id_match=key in identity_hits,
                          reference_contained=contained,partial_similarity=partial,
                          partial_metric_censored_below=p['partial_metric_score_cutoff'] if partial==0 else None,
                          normalization='NFKC/casefold/visible words; compact additionally removes word boundaries')
            quality=max(char_score,compact_score)
            if contained:quality=max(quality,ref_coverage)
            if tier=='partial_lexical_review':quality=max(quality,partial or 0)
            result.append((key,(rank,quality,dice,anchor_coverage,int(key in url_hits)),evidence))
        return result,url_hits


def create_database(path):
    db=connect(path)
    db.executescript('''
      CREATE TABLE IF NOT EXISTS docs (key TEXT PRIMARY KEY,payload BLOB);
      CREATE TABLE IF NOT EXISTS candidates (reference_id TEXT,key TEXT,rank TEXT,evidence TEXT,
        PRIMARY KEY(reference_id,key));
      CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY,next_row INTEGER,complete INTEGER,summary TEXT);
    ''')
    return db


def search_records(db,searcher,records,summary,top_k):
    heaps=defaultdict(list)
    for ref,key,ranking in db.execute('SELECT reference_id,key,rank FROM candidates'):
        heapq.heappush(heaps[ref],(tuple(json.loads(ranking)),key))
    url_counts=Counter(summary.get('url_alias_hits',{}));tiers=Counter(summary.get('candidate_tiers',{}))
    for key,record in records:
        summary['rows']+=1
        raw=record.get('text')
        if not isinstance(raw,str) or not raw.strip():continue
        scored,url_hits=searcher.score(raw,record.get('url'),record.get('id'))
        url_counts.update(url_hits)
        for ref,ranking,evidence in scored:
            tiers[evidence['tier']]+=1
            heap=heaps[ref];entry=(ranking,key)
            if len(heap)>=top_k and entry<=heap[0]:continue
            if any(existing_key==key for _,existing_key in heap):continue
            if len(heap)>=top_k:
                _,removed=heapq.heappop(heap)
                db.execute('DELETE FROM candidates WHERE reference_id=? AND key=?',(ref,removed))
            heapq.heappush(heap,entry)
            db.execute('INSERT OR REPLACE INTO docs VALUES (?,?)',(key,packed(record)))
            db.execute('INSERT OR REPLACE INTO candidates VALUES (?,?,?,?)',(ref,key,json.dumps(ranking),json.dumps(evidence)))
    summary['url_alias_hits']=dict(url_counts);summary['candidate_tiers']=dict(tiers)


def scan_one(task):
    file,output,policy,manifest=task
    path=file['path'];out=Path(output)
    db=create_database(out/'shards'/(Path(path).stem+'.sqlite'))
    checkpoint=db.execute('SELECT next_row,complete,summary FROM checkpoint WHERE id=1').fetchone()
    if checkpoint and checkpoint[1]:db.close();return json.loads(checkpoint[2])
    resume=checkpoint[0] if checkpoint else 0
    summary=json.loads(checkpoint[2]) if checkpoint else dict(path=path,rows=0,url_alias_hits={},candidate_tiers={})
    searcher=LexicalSearch(read_json(out/'targets.json'),policy)
    for offset,batch in remote_batches(manifest['crawl']['repo'],manifest['crawl']['revision'],path,policy['batch_size'],columns=['id','url','text','source']):
        if offset+len(batch)<=resume:continue
        rows=((path+':'+str(offset+i),row) for i,row in enumerate(batch.to_pylist()) if offset+i>=resume)
        search_records(db,searcher,rows,summary,policy['top_candidates_per_reference_per_shard'])
        db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1,?,0,?)',(offset+len(batch),json.dumps(summary)))
        db.commit()
        if offset//100000!=(offset+len(batch))//100000:
            print(f'{Path(path).stem}: {offset+len(batch):,} rows',flush=True)
    db.execute('DELETE FROM docs WHERE key NOT IN (SELECT key FROM candidates)')
    db.execute('UPDATE checkpoint SET complete=1 WHERE id=1');db.commit();db.close()
    print(f'Completed {Path(path).stem}: {summary["rows"]:,} rows',flush=True)
    return summary


def cached_search(output,policy):
    searcher=LexicalSearch(read_json(output/'targets.json'),policy)
    db=create_database(output/'cached.sqlite')
    existing=db.execute('SELECT complete FROM checkpoint WHERE id=1').fetchone()
    if existing and existing[0]:return
    summary=dict(path='previous_mapping_cache',rows=0,url_alias_hits={},candidate_tiers={})
    for shard in sorted((BASE/'data/crawl_shards').glob('*.sqlite')):
        source=sqlite3.connect(shard)
        for table,column in [('pairs','markdown'),('excluded','markdown')]:
            records=((key,unpacked(blob)) for key,blob in source.execute(f'SELECT key,{column} FROM {table}'))
            search_records(db,searcher,records,summary,policy['top_candidates_per_reference_per_shard'])
        source.close();db.commit()
    db.execute('DELETE FROM docs WHERE key NOT IN (SELECT key FROM candidates)')
    db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1,?,1,?)',(summary['rows'],json.dumps(summary)))
    db.commit();db.close()
    print('Cached records searched:',summary['rows'],flush=True)


def report(output,policy,manifest):
    targets={r['reference_id']:r for r in read_json(output/'targets.json')}
    paths=sorted((output/'shards').glob('*.sqlite'))
    summaries=[]; candidates=defaultdict(dict)
    if (output/'cached.sqlite').exists():paths=[output/'cached.sqlite',*paths]
    for path in paths:
        db=sqlite3.connect(path)
        checkpoint=db.execute('SELECT complete,summary FROM checkpoint WHERE id=1').fetchone()
        if not checkpoint or not checkpoint[0]:raise ValueError(f'Incomplete search: {path.name}')
        if path.name!='cached.sqlite':summaries.append(json.loads(checkpoint[1]))
        for ref,key,ranking,evidence,blob in db.execute('SELECT c.reference_id,c.key,c.rank,c.evidence,d.payload FROM candidates c JOIN docs d ON c.key=d.key'):
            ranking=tuple(json.loads(ranking))
            previous=candidates[ref].get(key)
            if previous is None or ranking>previous[0]:candidates[ref][key]=(ranking,json.loads(evidence),blob)
        db.close()
    exported=[]; statuses=[]
    visible_cache={}
    for ref,target in targets.items():
        ordered=sorted(candidates[ref].items(),key=lambda item:(item[1][0],item[0]),reverse=True)[:policy['top_candidates_per_reference_per_shard']]
        # Retrieval uses score cutoffs for speed; exported full-text ratios are
        # recalculated without cutoffs for the retained candidates only.
        for key,(ranking,evidence,blob) in ordered:
            if key not in visible_cache:visible_cache[key]=visible_markdown(unpacked(blob)['text'])
            normal=canonical(target['text']);visible=visible_cache[key]
            evidence['character_similarity']=ratio(normal,visible)/100
            evidence['compact_similarity']=ratio(normal.replace(' ',''),visible.replace(' ',''))/100
            if evidence['partial_similarity']==0:evidence['partial_similarity']=None
        best=ordered[0][1] if ordered else None
        top_tier=best[1]['tier'] if best else 'no_candidate'
        strong=bool(best and best[0][0]>=4)
        statuses.append(dict(reference_id=ref,best_tier=top_tier,strong_nonsemantic_candidate=strong,
                             candidate_count=len(ordered),best_crawl_key=ordered[0][0] if ordered else None,
                             best_compact_similarity=best[1]['compact_similarity'] if best else None,
                             best_reference_token_coverage=best[1]['reference_token_coverage'] if best else None))
        for key,(ranking,evidence,blob) in ordered:
            document=unpacked(blob);file,position=key.rsplit(':',1)
            exported.append(dict(reference_id=ref,crawl_key=key,crawl_res_id=document.get('id'),url=document.get('url'),
                                 source=document.get('source'),reference_urls=target.get('original_urls',target['urls']),
                                 searched_url_aliases=target['urls'],reference_text=target['text'],
                                 text_markdown=document['text'],human_labels=target['human_labels'],
                                 crawl_file=file,crawl_row=int(position),**evidence,
                                 label_transfer_allowed=evidence['tier']=='exact_visible',
                                 review_required=evidence['tier']!='exact_visible'))
    if exported:pq.write_table(pa.Table.from_pylist(exported),output/'candidates.parquet',compression='zstd')
    pq.write_table(pa.Table.from_pylist(statuses),output/'status.parquet',compression='zstd')
    full=len(summaries)==len(manifest['crawl']['files'])
    result=dict(created_at=datetime.now(timezone.utc).isoformat(),scope='Previously unmatched golden IDs only; lexical methods, no semantic similarity',
                targets=len(targets),full_corpus_scan_complete=full,crawl_rows_scanned=sum(r['rows'] for r in summaries),
                best_tiers=dict(Counter(r['best_tier'] for r in statuses)),
                strong_nonsemantic_candidate_ids=[r['reference_id'] for r in statuses if r['strong_nonsemantic_candidate']],
                not_strongly_matched_ids=[r['reference_id'] for r in statuses if not r['strong_nonsemantic_candidate']],
                baseline_candidate_ids=manifest['baseline_linked'],policy=policy,
                limitations=['A lexical candidate is not independent confirmation of document identity or human-label applicability.',
                             'Only exact visible-word equality permits automatic label transfer under the unchanged policy.',
                             'Shared passages may be quotations, boilerplate or partial copies. Multiple candidates are retained.',
                             'The partial-ratio metric is skipped for very long pairs; other full-text metrics still apply. No text is truncated.'])
    write_json(output/'summary.json',result)
    report_dir=BASE/'reports/golden_remaining';report_dir.mkdir(exist_ok=True)
    write_json(report_dir/'summary.json',result)
    lines=['# Focused nonsemantic search for remaining golden documents','',
           f'Targets: **{len(targets)}**. Full crawl scan complete: **{full}**. Rows searched: **{result["crawl_rows_scanned"]:,}**.','',
           '| Best candidate category | Reference documents |','|---|---:|']
    lines += [f'| {tier} | {count} |' for tier,count in sorted(result['best_tiers'].items())]
    lines += ['', 'URL aliases, Wikipedia redirect/page-ID metadata, many compact character passages, rare literal tokens, edit similarity, token overlap and partial string matching are used. No embeddings or LLM inference.','',
              'Candidate tables retain full original texts, human labels, locators and lexical evidence. Baseline alignment and labels are unchanged. No training set is selected.','']
    lines += ['- '+item for item in result['limitations']]
    (report_dir/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({key:result[key] for key in ['targets','full_corpus_scan_complete','crawl_rows_scanned','best_tiers']},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['cached','scan','report','all'])
    parser.add_argument('--policy',type=Path,default=BASE/'golden_search_policy.json')
    parser.add_argument('--output-dir',type=Path,default=BASE/'data/golden_remaining_v2')
    args=parser.parse_args();policy=read_json(args.policy)
    manifest=prepare(args.output_dir,policy)
    (args.output_dir/'shards').mkdir(exist_ok=True)
    print(f'Searching {len(manifest["targets"])} previously unmatched golden IDs',flush=True)
    if args.stage in ('cached','all'):cached_search(args.output_dir,policy)
    if args.stage in ('scan','all'):
        with ProcessPoolExecutor(max_workers=policy['workers']) as executor:
            futures=[executor.submit(scan_one,(file,str(args.output_dir),policy,manifest)) for file in manifest['crawl']['files']]
            for future in as_completed(futures):future.result()
    report(args.output_dir,policy,manifest)


if __name__=='__main__':
    main()
