import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pyarrow as pa
import pipeline

from text_utils import ReferenceGuard, canonical, fast_markdown, url_key, visible_markdown


class MappingTests(unittest.TestCase):
    def test_quarantine_closes_over_late_discovered_url_id_and_hash_links(self):
        def candidate(key,id_,url,hashed):
            return dict(key=key,id=id_,url=url,url_key=url_key(url),hash=hashed)
        rows=[candidate('safe','safe','https://example.test/safe','safe'),
              candidate('indirect','later','https://example.test/later','new'),
              candidate('url','later','http://example.test/reference','changed'),
              candidate('hash','other','https://mirror.test/copy','reference')]
        excluded=[dict(id='gold',url='https://example.test/reference',canonical_sha256='reference',reference_ids=['ref'])]
        kept,removed=pipeline.quarantine(rows,excluded)
        self.assertEqual([r['key'] for r in kept],['safe'])
        self.assertEqual({r['key'] for r in removed},{'indirect','url','hash'})
        kept_reversed,_=pipeline.quarantine(list(reversed(rows)),excluded)
        self.assertEqual([r['key'] for r in kept_reversed],['safe'])

    def test_scan_excludes_reference_urls_and_copies_and_does_not_accept_url_alone(self):
        policy=json.loads(Path(__file__).with_name('policy.json').read_text())
        reference=canonical('Reference document contains unique educational explanations and many distinctive scientific details.')
        original='A useful guide explains knowledge with practical examples and detailed teaching.'
        near=' '.join(f'word{i}' for i in range(100))
        fw_rows=[('aaa_other_snapshot','https://site.test/good','Different older content.'),('good','https://site.test/good',original),('changed','https://site.test/changed',original),('near','https://site.test/near',near)]
        crawl=[
            dict(id='reference-url',url='https://site.test/reference',text='Completely changed content',source='test'),
            dict(id='reference-copy',url='https://mirror.test/copy',text=reference,source='test'),
            dict(id='good',url='http://site.test/good',text='A **useful** [guide](https://link.test) explains knowledge with practical examples and detailed teaching.',source='test'),
            dict(id='changed',url='https://site.test/changed',text='An entirely different page about unrelated events.',source='test'),
            dict(id='near',url='https://site.test/near',text=near.replace('word50','changed50'),source='test'),
            dict(id='unknown',url='https://site.test/unknown',text=original,source='test'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory); (base/'data').mkdir()
            db=sqlite3.connect(base/'data/fineweb.sqlite')
            db.execute('CREATE TABLE fw (key TEXT,id TEXT,url TEXT,url_key TEXT,partition TEXT,hash TEXT,length INTEGER,payload BLOB)')
            for key,url,text in fw_rows:
                value=canonical(text)
                db.execute('INSERT INTO fw VALUES (?,?,?,?,?,?,?,?)',(key,key,url,url_key(url),'retained',pipeline.digest(value),len(value),pipeline.packed(dict(id=key,url=url,text=text))))
            db.commit();db.close()
            state=dict(variants=[['ref',reference]],urls={url_key('https://site.test/reference'):['ref']})
            (base/'data/guard.json.zlib').write_bytes(pipeline.packed(state))
            def batches(*args,**kwargs):
                yield 0,pa.RecordBatch.from_pylist(crawl)
            with patch.object(pipeline,'BASE',base),patch.object(pipeline,'remote_batches',side_effect=batches):
                result=pipeline.scan_file(({'path':'data/shard.parquet'},policy))
                self.assertEqual(result['rows'],6)
                self.assertEqual(result['statuses']['excluded_reference_or_test'],2)
                self.assertEqual(result['statuses']['exact_visible_tokens'],1)
                self.assertEqual(result['statuses']['near_requires_review'],1)
                self.assertEqual(result['statuses']['url_content_mismatch'],1)
                self.assertEqual(result['statuses']['no_fineweb_url_candidate'],1)
            with patch.object(pipeline,'BASE',base),patch.object(pipeline,'remote_batches') as remote:
                self.assertEqual(pipeline.scan_file(({'path':'data/shard.parquet'},policy)),result)
                remote.assert_not_called()

    def test_url_aliases_preserve_meaningful_distinctions(self):
        self.assertEqual(url_key('HTTP://Example.COM:80/a#top'), url_key('https://example.com/a'))
        self.assertEqual(url_key('https://example.com/сәлам'), url_key('https://example.com/%D1%81%D3%99%D0%BB%D0%B0%D0%BC'))
        self.assertNotEqual(url_key('https://example.com/a%2Fb'), url_key('https://example.com/a/b'))
        self.assertNotEqual(url_key('https://example.com/A'), url_key('https://example.com/a'))
        self.assertNotEqual(url_key('https://example.com/?id=1'), url_key('https://example.com/?id=2'))
        self.assertIsNone(url_key('not a URL'))

    def test_markdown_visible_text_preserves_content(self):
        markdown = '# Title\n\nA **useful** [guide](https://example.com).\n\n- First\n- Second'
        self.assertEqual(visible_markdown(markdown), canonical('Title A useful guide. First Second'))
        table = '| Name | Value |\n|---|---|\n| A | 12 |'
        self.assertEqual(visible_markdown(table), canonical('Name Value A 12'))
        self.assertEqual(visible_markdown('<script>bad()</script><p>Good &amp; useful</p>'), canonical('Good & useful'))
        self.assertNotEqual(visible_markdown(markdown), canonical('Title A useless guide First Second'))
        self.assertEqual(visible_markdown('1. First\n2. Second'),canonical('First Second'))
        self.assertEqual(visible_markdown('Plain paragraphs.\n\nWith 12 facts.'),canonical('Plain paragraphs. With 12 facts.'))
        self.assertEqual(visible_markdown('pre**fix**suffix'),canonical('prefixsuffix'))
        self.assertEqual(visible_markdown('<span>foo</span><span>bar</span>'),canonical('foobar'))

    def test_reference_guard_detects_exact_near_and_contained_text(self):
        text=canonical('Distinctive reference document about science and education with explanations and examples.')
        p=dict(reference_anchor_chars=12,reference_anchor_count=4,reference_near_similarity=.9)
        guard=ReferenceGuard([('reference',text)],p)
        self.assertEqual(guard.matches(text),['reference'])
        self.assertEqual(guard.matches('prefix '+text+' suffix'),['reference'])
        self.assertEqual(guard.matches(text.replace('science','physics')),['reference'])
        self.assertEqual(guard.matches(canonical('An entirely different document.')),[])
        self.assertEqual(guard.matches(fast_markdown('**'+text+'**')),['reference'])


if __name__=='__main__':
    unittest.main()
