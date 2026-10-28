import contextlib
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from compare_models import compare
from merge_classes import generate


class ComparisonTests(unittest.TestCase):
    def test_partial_runs_use_identical_shared_cohort(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            runs = [base/'a', base/'b']
            for run, records in zip(runs, [
                [('shared', 'None', 'None'), ('a-only', 'Basic', 'Basic')],
                [('shared', 'None', 'Basic'), ('b-only', 'Basic', 'Basic')],
            ]):
                run.mkdir()
                (run/'manifest.json').write_text(json.dumps(dict(model=run.name, source_sha256='source', prompt_sha256='prompt')))
                (run/'metrics.json').write_text(json.dumps(dict(successfully_labeled=2, total_documents=3)))
                with (run/'comparisons.csv').open('w', newline='') as handle:
                    writer = csv.DictWriter(handle, fieldnames=['id','human_labels','llm_label','included_in_primary'])
                    writer.writeheader()
                    for id_, human, label in records:
                        writer.writerow(dict(id=id_, human_labels=json.dumps([human]), llm_label=label, included_in_primary=True))
            with contextlib.redirect_stdout(io.StringIO()):
                result = compare(runs, base/'out')
            self.assertEqual(result['shared_primary_documents'], 1)
            self.assertEqual(result['models'][0]['common_cohort']['accuracy'], 1)
            self.assertEqual(result['models'][1]['common_cohort']['accuracy'], 0)
            manifest = json.loads((runs[1]/'manifest.json').read_text())
            manifest['prompt_sha256'] = 'changed'
            (runs[1]/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                compare(runs, base/'out')
            with contextlib.redirect_stdout(io.StringIO()):
                changed_prompt = compare(runs, base/'prompt-out', allow_different_prompts=True)
                grouped = generate(runs, base/'grouped', allow_different_prompts=True)
            self.assertTrue(changed_prompt['allow_different_prompts'])
            self.assertEqual(grouped['scored_documents'], 1)
            self.assertIn('different prompt hashes', (base/'prompt-out/comparison.md').read_text())
            manifest['source_sha256'] = 'different-source'
            (runs[1]/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                compare(runs, base/'out', allow_different_prompts=True)
            with self.assertRaises(ValueError):
                generate(runs, base/'grouped', allow_different_prompts=True)


if __name__ == '__main__':
    unittest.main()
