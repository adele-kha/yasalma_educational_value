"""Resolve missing golden Wikipedia titles using public MediaWiki identity metadata."""
from datetime import datetime, timezone
import json
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

import pyarrow.parquet as pq

from pipeline import BASE, write_json


def main():
    linked=set(pq.read_table(BASE/'data/reference_pairs.parquet',columns=['reference_id'])['reference_id'].to_pylist())
    refs={r['id']:r for r in pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist() if r['id'] not in linked}
    urls={key:set(r[k] for k in ('source_url','fineweb2_url') if r[k]) for key,r in refs.items()}
    for row in pq.read_table(BASE/'data/reference_candidate_audit.parquet').to_pylist():
        if row['reference_id'] in refs and row['original_annotation_canonical_exact'] and row['url']:
            urls[row['reference_id']].add(row['url'])
    titles={}
    for key,values in urls.items():
        for url in values:
            parsed=urlsplit(url)
            if (parsed.hostname or '').replace('.m.wikipedia.org','.wikipedia.org')!='tt.wikipedia.org':continue
            title=unquote(parsed.path[6:]) if parsed.path.startswith('/wiki/') else parse_qs(parsed.query).get('title',[''])[0]
            if title:titles[key]=title.replace('_',' ')
    responses=[];results={};unique=sorted(set(titles.values()))
    for offset in range(0,len(unique),15):
        batch=unique[offset:offset+15]
        endpoint='https://tt.wikipedia.org/w/api.php?'+urlencode(dict(action='query',format='json',redirects=1,converttitles=1,titles='|'.join(batch)))
        req=Request(endpoint,headers={'User-Agent':'YasalmaEducationalValueMapping/0.1 (https://github.com/adele-kha/yasalma_educational_value)'})
        with urlopen(req,timeout=60) as response:body=json.load(response)
        responses.append(dict(endpoint=endpoint,response=body))
        query=body.get('query',{});changes={}
        for field in ('normalized','converted','redirects'):
            changes.update({r['from']:r['to'] for r in query.get(field,[])})
        pages={r['title']:r for r in query.get('pages',{}).values()}
        for title in batch:
            final=title;seen=set()
            while final in changes and final not in seen:
                seen.add(final);final=changes[final]
            page=pages.get(final,{})
            results[title]=dict(original_title=title,resolved_title=final,page_id=page.get('pageid'),
                                namespace=page.get('ns'),missing='missing' in page or not page,
                                current_url='https://tt.wikipedia.org/wiki/'+quote(final.replace(' ','_'),safe=':/'))
        print(f'Wikipedia titles resolved: {min(offset+15,len(unique))}/{len(unique)}',flush=True)
    output=dict(checked_at=datetime.now(timezone.utc).isoformat(),method='MediaWiki normalization/redirect/page-ID metadata; no semantic similarity',
                references={key:results[title] for key,title in titles.items()},responses=responses)
    write_json(BASE/'data/golden_wiki_identity.json',output)
    print(json.dumps({key:sum(bool(r[key]) for r in output['references'].values()) for key in ['missing']},indent=2))


if __name__=='__main__':
    main()
