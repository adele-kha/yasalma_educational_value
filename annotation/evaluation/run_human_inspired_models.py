"""Run the additional models with the human-inspired prompt and merged scoring."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

from merge_classes import generate

BASE = Path(__file__).resolve().parent
MODELS = {
    'muse-spark-open': 'meta-models/muse-spark-open',
    'qwen35-397b-a17b': 'Qwen/Qwen3.5-397B-A17B',
    'nemotron3-ultra-550b-a55b': 'nvidia/Nemotron-3-Ultra-550b-a55b',
}
PROMPT = BASE/'prompts/prompt_human_annotation_inspired.txt'


def build_reports(runs):
    output = BASE/'reports/human_inspired_merged_classes'
    manifests = [json.loads((run/'manifest.json').read_text()) for run in runs]
    for key in ('source_sha256', 'prompt_sha256'):
        if len({manifest[key] for manifest in manifests}) != 1:
            raise ValueError(f'Runs differ in {key}')
    coverage = []
    complete = []
    for run, manifest in zip(runs, manifests):
        metrics_path = run/'metrics.json'
        m = json.loads(metrics_path.read_text()) if metrics_path.exists() else dict(
            complete=False, successfully_labeled=0,
            total_documents=json.loads((runs[0]/'metrics.json').read_text())['total_documents'])
        checkpoint = run/'predictions.jsonl'
        predictions = {p['id']: p for p in map(json.loads, checkpoint.read_text().splitlines())} if checkpoint.exists() else {}
        errors = sorted({p.get('error', 'Unknown error') for p in predictions.values() if p['status'] != 'ok'})
        if not metrics_path.exists():
            errors.append('Run did not produce metrics; see execution.log for availability errors')
        coverage.append(dict(model=manifest['model'], run=str(run), successful=m['successfully_labeled'],
                             total=m['total_documents'], complete=m['complete'], errors=errors))
        if m['complete']:
            complete.append(run)
        elif m['successfully_labeled']:
            generate([run], output/'partial'/run.name)
    if not complete:
        raise ValueError('No complete model runs for the main comparison')
    generate(complete, output)
    (output/'coverage.json').write_text(json.dumps(coverage, indent=2)+'\n')
    warning = ['## Run coverage', '',
               'The main comparison above includes complete runs only. Incomplete runs are excluded from the ranking; their limited merged-class results are stored under `partial/` and are not comparable to full-cohort results.', '',
               '| Model | Successful / total | Included in main comparison |', '|---|---:|---|']
    warning += [f'| {r["model"]} | {r["successful"]}/{r["total"]} | {r["complete"]} |' for r in coverage]
    warning += ['', 'Recorded API errors and full coverage details: `coverage.json`.']
    with (output/'report.md').open('a') as handle:
        handle.write('\n'+'\n'.join(warning)+'\n')


def run_model(name, model, args):
    output = BASE/'runs'/f'{name}-human-inspired'
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(BASE/'evaluate.py'), '--model', model,
               '--prompt', str(PROMPT), '--output-dir', str(output),
               '--max-tokens', str(args.max_tokens), '--workers', str(args.workers)]
    if args.limit:
        command += ['--limit', str(args.limit)]
    with (output/'execution.log').open('a') as log:
        print(f'Starting {model}', flush=True)
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            (output/'prompt_snapshot.txt').write_bytes(PROMPT.read_bytes())
            print(f'{model}: execution failed; see {output}/execution.log', flush=True)
            return output
        metrics = json.loads((output/'metrics.json').read_text())
        predictions = {p['id']: p for p in map(json.loads, (output/'predictions.jsonl').read_text().splitlines())}
        retryable = any(p['status'] != 'ok' and not p.get('error', '').startswith(('HTTP 400:', 'HTTP 401:', 'HTTP 403:', 'HTTP 404:')) for p in predictions.values())
        if metrics['missing_or_failed'] and retryable and not args.limit:
            result = subprocess.run(command + ['--retry-max-tokens', str(args.retry_max_tokens)],
                                    stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                print(f'{model}: retry could not start; see execution.log', flush=True)
    (output/'prompt_snapshot.txt').write_bytes(PROMPT.read_bytes())
    metrics = json.loads((output/'metrics.json').read_text())
    print(f'{model}: {metrics["successfully_labeled"]}/{metrics["total_documents"]} successful', flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', choices=list(MODELS), default=list(MODELS))
    parser.add_argument('--workers', type=int, default=8, help='Concurrent requests per model')
    parser.add_argument('--max-tokens', type=int, default=4096)
    parser.add_argument('--retry-max-tokens', type=int, default=16384)
    parser.add_argument('--limit', type=int, help='Smoke-test only; skips the combined report')
    parser.add_argument('--report-only', action='store_true', help='Rebuild merged reports from saved runs without API calls')
    args = parser.parse_args()
    if args.workers <= 0 or (args.limit is not None and args.limit <= 0):
        parser.error('workers and limit must be positive')
    if args.report_only:
        runs = [BASE/'runs'/f'{name}-human-inspired' for name in args.models]
    else:
        with ThreadPoolExecutor(max_workers=len(args.models)) as executor:
            runs = list(executor.map(lambda name: run_model(name, MODELS[name], args), args.models))
    if not args.limit:
        build_reports([BASE/'runs/qwen38-27b-human-inspired', *runs])


if __name__ == '__main__':
    main()
