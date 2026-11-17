import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_human_inspired_models as runner


class HumanInspiredModelsTests(unittest.TestCase):
    def test_incomplete_model_is_not_ranked_with_complete_models(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            runs = [base/'complete', base/'partial']
            for run, complete in zip(runs, [True, False]):
                run.mkdir()
                (run/'manifest.json').write_text(json.dumps(dict(model=run.name, source_sha256='source', prompt_sha256='human')))
                (run/'metrics.json').write_text(json.dumps(dict(complete=complete, successfully_labeled=10 if complete else 1, total_documents=10)))
                (run/'predictions.jsonl').write_text(json.dumps(dict(id='one', status='ok'))+'\n')
            def fake_generate(selected, output):
                output.mkdir(parents=True, exist_ok=True)
                (output/'report.md').write_text('Report\n')
            with patch.object(runner, 'BASE', base), patch.object(runner, 'generate', side_effect=fake_generate) as generate:
                runner.build_reports(runs)
            self.assertEqual(generate.call_args_list[-1].args[0], [runs[0]])
            coverage = json.loads((base/'reports/human_inspired_merged_classes/coverage.json').read_text())
            self.assertEqual([row['complete'] for row in coverage], [True, False])

    def test_full_run_compares_only_human_inspired_runs(self):
        def fake_run(name, model, args):
            return runner.BASE/'runs'/f'{name}-human-inspired'
        with patch('sys.argv', ['runner']), patch.object(runner, 'run_model', side_effect=fake_run), patch.object(runner, 'build_reports') as generate:
            runner.main()
        runs, = generate.call_args.args
        self.assertEqual(len(runs), 4)
        self.assertTrue(all(run.name.endswith('-human-inspired') for run in runs))

    def test_smoke_run_does_not_replace_combined_report(self):
        with patch('sys.argv', ['runner', '--limit', '3']), patch.object(runner, 'run_model'), patch.object(runner, 'build_reports') as generate:
            runner.main()
        generate.assert_not_called()
