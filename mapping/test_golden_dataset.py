import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from build_golden_dataset import MATCH_LABELS, GROUPS, consensus, load_model, match_evidence


class GoldenDatasetTests(unittest.TestCase):
    policy = dict(near_character_similarity=.85, near_token_dice=.75)

    def test_exact_text_can_match_different_urls(self):
        evidence = match_evidence({'text':'Alpha beta gamma'},
            {'text_markdown':'**Alpha** beta gamma.', 'url':'https://copy.org'},
            {'https://original.org'}, self.policy)
        self.assertEqual(evidence['match_label'], MATCH_LABELS[0])
        self.assertTrue(evidence['label_transfer_allowed'])

    def test_same_page_transfers_labels_despite_changed_text(self):
        evidence = match_evidence({'text':'Original annotated article'},
            {'text_markdown':'Entirely replaced content', 'url':'https://belem.ru/print/6447'},
            {'http://belem.ru/node/6447'}, self.policy)
        self.assertEqual(evidence['match_label'], MATCH_LABELS[1])
        self.assertTrue(evidence['label_transfer_allowed'])
        self.assertFalse(evidence['exact_text_match'])

    def test_embedded_url_is_not_page_identity(self):
        evidence = match_evidence({'text':'Original annotated article'},
            {'text_markdown':'Embed metadata', 'url':'https://site.org/oembed?url=https://site.org/article',
             'tier':'url_alias_content_review'}, {'https://site.org/article'}, self.policy)
        self.assertEqual(evidence['match_label'], MATCH_LABELS[3])

    def test_near_candidate_is_retained_for_review(self):
        text = 'alpha beta gamma delta epsilon zeta eta theta iota kappa lambda'
        evidence = match_evidence({'text':text},
            {'text_markdown':text.replace('kappa', 'sigma'), 'url':'https://copy.org'},
            {'https://original.org'}, self.policy)
        self.assertEqual(evidence['match_label'], MATCH_LABELS[2])
        self.assertTrue(evidence['label_transfer_allowed'])
        self.assertFalse(evidence['exact_text_match'])

    def test_disagreement_preserved_until_merge(self):
        self.assertIsNone(consensus(['Minimal','None']))
        self.assertEqual(consensus(['Minimal','None'],GROUPS['three_classes']),'None–Minimal')
        self.assertIsNone(consensus(['Minimal','None'],GROUPS['four_classes']))
        self.assertEqual(consensus(['❗ Problematic Content ❗']),'Problematic Content')

    def test_model_join_checks_text_not_only_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'model.parquet'
            pq.write_table(pa.Table.from_pylist([dict(id='id',text='Different version',
                educational_value_labels=['Good'])]),path)
            with self.assertRaisesRegex(ValueError,'different text'):
                load_model(path,{'id':dict(text='Original version')})


if __name__ == '__main__':
    unittest.main()
