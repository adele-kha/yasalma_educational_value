import csv
import json
from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from evaluate import metrics, parse_response, report


class EvaluationTests(unittest.TestCase):
    def test_metrics_against_hand_computed_example(self):
        result = metrics([('None', 'None'), ('Basic', 'None'), ('Basic', 'Basic'),
                          ('Problematic Content', 'Basic')])
        self.assertEqual(result['accuracy'], .5)
        self.assertEqual(result['micro_precision'], .5)
        self.assertEqual(result['per_class']['Basic']['precision'], .5)
        self.assertEqual(result['per_class']['Basic']['recall'], .5)
        self.assertEqual(result['per_class']['Basic']['one_vs_rest_accuracy'], .5)
        self.assertEqual(result['per_class']['Excellent']['f1'], 0)
        self.assertIsNone(metrics([])['accuracy'])

    def test_strict_parser(self):
        self.assertEqual(parse_response('Reason: Useful explanation.\nEducational label: Basic'),
                         ('Basic', 'Useful explanation.'))
        self.assertEqual(parse_response('Reason: '+('word '*101)+'\nEducational label: Good')[0], 'Good')
        for text in ['Educational label: Basic', 'Reason: A\nEducational label: Unknown',
                     'Reason: A\nEducational label: Basic\nExtra text']:
            with self.assertRaises(ValueError):
                parse_response(text)

    def test_dataset_schema_missing_predictions_and_conflicting_humans(self):
        source = pq.read_table(Path(__file__).resolve().parent.parent/'data/tat_Cyrl-train.parquet')
        sample = source.slice(0, 3).to_pylist()
        sample[0]['educational_value_labels'] = ['None']
        sample[1]['educational_value_labels'] = ['Basic', 'None']
        sample[2]['educational_value_labels'] = ['Good']
        table = pa.Table.from_pylist(sample, schema=source.schema)
        predictions = {sample[0]['id']: dict(status='ok', label='Problematic Content', reason='Test', model='test'),
                       sample[1]['id']: dict(status='ok', label='Basic', reason='Test', model='test')}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = report(table, predictions, output)
            self.assertFalse(result['complete'])
            self.assertEqual(result['primary']['n'], 1)
            self.assertEqual(result['all_human_annotations']['n'], 3)
            restored = pq.read_table(output/'llm_annotations.partial.parquet')
            self.assertEqual(restored.schema, table.schema)
            self.assertEqual(restored['text'][0].as_py(), sample[0]['text'])
            self.assertEqual(restored['educational_value_labels'][0].as_py(), ['❗ Problematic Content ❗'])
            self.assertTrue(restored['problematic_content_label_present'][0].as_py())
            self.assertEqual(restored['annotator_ids'][0].as_py(), ['nebius:test'])
            self.assertEqual(json.loads((output/'metrics.json').read_text())['missing_or_failed'], 1)


if __name__ == '__main__':
    unittest.main()
