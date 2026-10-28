"""Compare model runs on exactly the same unambiguous human-labeled documents."""
import argparse
import csv
import json
from pathlib import Path

from evaluate import LABELS, metrics


def compare(runs, output, allow_different_prompts=False):
    manifests = [json.loads((run/'manifest.json').read_text()) for run in runs]
    for key in ['source_sha256'] + ([] if allow_different_prompts else ['prompt_sha256']):
        if len({m[key] for m in manifests}) != 1:
            raise ValueError(f'Cannot compare runs with different {key}')
    comparisons = []
    for run in runs:
        with (run/'comparisons.csv').open(encoding='utf-8-sig', newline='') as handle:
            comparisons.append({r['id']: r for r in csv.DictReader(handle) if r['included_in_primary']=='True'})
    shared = set.intersection(*(set(rows) for rows in comparisons))
    for id_ in shared:
        if len({tuple(json.loads(rows[id_]['human_labels'])) for rows in comparisons}) != 1:
            raise ValueError(f'Human labels differ for {id_}')
    result = dict(shared_primary_documents=len(shared), allow_different_prompts=allow_different_prompts, models=[])
    for run, manifest, rows in zip(runs, manifests, comparisons):
        original = json.loads((run/'metrics.json').read_text())
        pairs = [(json.loads(rows[id_]['human_labels'])[0], rows[id_]['llm_label']) for id_ in sorted(shared)]
        result['models'].append(dict(model=manifest['model'], run=str(run), prompt_sha256=manifest['prompt_sha256'],
                                    successful_documents=original['successfully_labeled'],
                                    total_documents=original['total_documents'],
                                    primary_available=len(rows), common_cohort=metrics(pairs)))
    title = '# Prompt comparison' if allow_different_prompts else '# Model comparison with unchanged prompt'
    provenance = 'Source hashes match; different prompt hashes are explicitly allowed.' if allow_different_prompts else 'Source and prompt hashes match across runs.'
    lines = [title, '',
             f'All metrics below use the same **{len(shared):,} documents** with one distinct human label and a successful prediction from every model. {provenance}', '',
             '| Model | Successful / total | Accuracy | Macro precision | Macro recall | Macro F1 | Kappa |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for model in result['models']:
        m = model['common_cohort']
        if not shared:
            raise ValueError('No shared scoreable documents')
        kappa = f'{m["cohens_kappa"]:.4f}' if m['cohens_kappa'] is not None else 'N/A'
        lines.append(f'| {model["model"]} ({Path(model["run"]).name}) | {model["successful_documents"]}/{model["total_documents"]} | {m["accuracy"]:.2%} | {m["macro_precision"]:.2%} | {m["macro_recall"]:.2%} | {m["macro_f1"]:.2%} | {kappa} |')
    for model in result['models']:
        lines += ['', f'## {model["model"]} ({Path(model["run"]).name})', '',
                  '| Human class | Support | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |',
                  '|---|---:|---:|---:|---:|---:|']
        for label in LABELS:
            m = model['common_cohort']['per_class'][label]
            lines.append(f'| {label} | {m["support"]} | {m["precision"]:.2%} | {m["recall"]:.2%} | {m["f1"]:.2%} | {m["one_vs_rest_accuracy"]:.2%} |')
        lines += ['', f'Run: `{model["run"]}`. The run report also contains the confusion matrix and metrics on all its own successful documents.']
    lines += ['', 'Accuracy equals micro precision for this single-label task. Macro metrics average all six classes with undefined precision/recall/F1 scored as zero. Agreement is measured against the supplied human labels. Any incomplete coverage is shown above; restricting to the shared cohort can change results relative to the individual run reports.']
    output.mkdir(parents=True, exist_ok=True)
    (output/'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path, nargs='+')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent/'reports/models')
    parser.add_argument('--allow-different-prompts', action='store_true')
    args = parser.parse_args()
    if len(args.runs) < 2:
        parser.error('Supply at least two model run directories')
    compare(args.runs, args.output_dir, args.allow_different_prompts)
