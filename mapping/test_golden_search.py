import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from search_remaining import LexicalSearch, create_database, search_records, url_aliases


class GoldenSearchTests(unittest.TestCase):
    def policy(self):
        return json.loads(Path(__file__).with_name('golden_search_policy.json').read_text())

    def target(self):
        return dict(reference_id='gold',urls=['https://tt.wikipedia.org/wiki/Some_Page'],
                    text=' '.join('DistinctiveScientificToken'+str(i) for i in range(35)),human_labels=['Basic'])

    def test_url_aliases_cover_wikipedia_and_drupal_variants(self):
        self.assertTrue(url_aliases('https://tt.wikipedia.org/wiki/Some_Page') &
                        url_aliases('http://tt.m.wikipedia.org/w/index.php?title=Some%20Page'))
        self.assertTrue(url_aliases('https://www.belem.ru/node/7995/') &
                        url_aliases('http://belem.ru/?q=node/7995'))
        self.assertFalse(url_aliases('https://belem.ru/node/1') & url_aliases('https://belem.ru/node/2'))

    def test_split_words_recovered_without_same_url(self):
        target=self.target();search=LexicalSearch([target],self.policy())
        split=' '.join(word[:8]+'\n'+word[8:] for word in target['text'].split())
        rows,_=search.score(split,'https://mirror.test/article')
        self.assertEqual(rows[0][2]['tier'],'exact_compact')
        self.assertFalse(rows[0][2]['url_alias_match'])

    def test_url_alias_does_not_establish_text_identity(self):
        search=LexicalSearch([self.target()],self.policy())
        rows,_=search.score('A completely unrelated page.','http://tt.m.wikipedia.org/w/index.php?title=Some%20Page')
        self.assertEqual(rows[0][2]['tier'],'url_alias_content_review')
        self.assertLess(rows[0][1][0],4)

    def test_page_id_is_metadata_evidence_not_label_equivalence(self):
        target=self.target();target['wikipedia_page_ids']=[12867]
        search=LexicalSearch([target],self.policy())
        rows,_=search.score('A new version with changed contents.','https://tt.wikipedia.org/wiki/Renamed','ttwiki/12867')
        self.assertEqual(rows[0][2]['tier'],'wikipedia_page_identity_review')
        self.assertTrue(rows[0][2]['wikipedia_page_id_match'])

    def test_shared_whole_reference_and_bounded_candidates(self):
        target=self.target();search=LexicalSearch([target],self.policy())
        rows,_=search.score('An added preface. '+target['text']+' An added footer.','https://mirror.test/one')
        self.assertTrue(rows[0][2]['reference_contained'])
        with tempfile.TemporaryDirectory() as directory:
            db=create_database(Path(directory)/'search.sqlite')
            summary=dict(rows=0)
            records=((str(i),dict(text=target['text'],url='https://mirror.test/'+str(i))) for i in range(12))
            search_records(db,search,records,summary,2)
            self.assertEqual(db.execute('SELECT count(*) FROM candidates').fetchone()[0],2)
            self.assertEqual(summary['rows'],12)
            db.close()


if __name__=='__main__':
    unittest.main()
