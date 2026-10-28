"""Re-score saved predictions after merging human and model labels; no API calls."""
import argparse
import csv
import json
from pathlib import Path

from evaluate import metrics, normalize

BASE = Path(__file__).resolve().parent
GROUPS = {
    'Problematic Content': ['Problematic Content'],
    'None–Minimal': ['None', 'Minimal'],
    'Basic–Good–Excellent': ['Basic', 'Good', 'Excellent'],
}
MAPPING = {label: group for group, labels in GROUPS.items() for label in labels}


def merged_human(labels):
    groups = {MAPPING[normalize(label)] for label in labels if label is not None}
    return next(iter(groups)) if len(groups) == 1 else None


def generate(runs, output, allow_different_prompts=False):
    manifests = [json.loads((run/'manifest.json').read_text()) for run in runs]
    for key in ['source_sha256'] + ([] if allow_different_prompts else ['prompt_sha256']):
        if len({m[key] for m in manifests}) != 1:
            raise ValueError(f'Runs differ in {key}')
    records = []
    for run in runs:
        with (run/'comparisons.csv').open(encoding='utf-8-sig', newline='') as handle:
            records.append({row['id']: row for row in csv.DictReader(handle)})
    shared = set.intersection(*(set(rows) for rows in records))
    eligible = []
    for id_ in sorted(shared):
        human_lists = [json.loads(rows[id_]['human_labels']) for rows in records]
        if any(labels != human_lists[0] for labels in human_lists[1:]):
            raise ValueError(f'Human annotations differ for {id_}')
        if merged_human(human_lists[0]) is not None:
            eligible.append(id_)
    if not eligible:
        raise ValueError('No shared unambiguous merged-label documents')
    output.mkdir(parents=True, exist_ok=True)
    summary = dict(groups=GROUPS, allow_different_prompts=allow_different_prompts, shared_successful_documents=len(shared),
                   scored_documents=len(eligible), excluded_after_merging=len(shared)-len(eligible), models=[])
    for run, manifest, rows in zip(runs, manifests, records):
        pairs = [(merged_human(json.loads(rows[id_]['human_labels'])), MAPPING[normalize(rows[id_]['llm_label'])]) for id_ in eligible]
        result = metrics(pairs, list(GROUPS))
        summary['models'].append(dict(model=manifest['model'], run=str(run), prompt_sha256=manifest['prompt_sha256'], metrics=result))
        with (output/(run.name+'_comparisons.csv')).open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['id', 'human_labels', 'human_group', 'llm_label', 'llm_group', 'match'])
            writer.writeheader()
            for id_, (human, predicted) in zip(eligible, pairs):
                writer.writerow(dict(id=id_, human_labels=rows[id_]['human_labels'], human_group=human,
                                     llm_label=rows[id_]['llm_label'], llm_group=predicted, match=human==predicted))
    lines = ['# Agreement with merged classes', '',
             f'Both human and model labels are mapped into {len(GROUPS)} groups before metrics are recalculated. Existing predictions are reused; no additional inference is performed. Each run retains its own recorded prompt.', '']
    if allow_different_prompts:
        lines += ['Source hashes match; this comparison explicitly allows different prompt versions, identified by run folder below.', '']
    lines += [f'- **{group}**: '+', '.join(labels) for group, labels in GROUPS.items()]
    lines += ['', f'Comparison cohort: **{len(eligible):,} documents**, shared across all models, with one distinct human group after merging. The three original None/Minimal human disagreements now fall within the same group and are included. Documents with human labels spanning different groups would remain excluded.', '',
              '| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for model in summary['models']:
        m=model['metrics']
        kappa=f'{m["cohens_kappa"]:.4f}' if m['cohens_kappa'] is not None else 'N/A'
        lines.append(f'| {model["model"]} ({Path(model["run"]).name}) | {m["accuracy"]:.2%} | {m["macro_precision"]:.2%} | {m["macro_recall"]:.2%} | {m["macro_f1"]:.2%} | {m["weighted_f1"]:.2%} | {kappa} |')
    for model in summary['models']:
        m=model['metrics']
        lines += ['', '## '+model['model']+' ('+Path(model['run']).name+')', '',
                  '| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for group, v in m['per_class'].items():
            lines.append(f'| {group} | {v["support"]} | {v["predicted"]} | {v["precision"]:.2%} | {v["recall"]:.2%} | {v["f1"]:.2%} | {v["one_vs_rest_accuracy"]:.2%} |')
        lines += ['', 'Confusion matrix: rows are human groups; columns are model groups.', '',
                  '| Human / LLM | '+' | '.join(GROUPS)+' |', '|---|'+'---:|'*len(GROUPS)]
        for group, counts in m['confusion_matrix'].items():
            lines.append('| '+group+' | '+' | '.join(str(counts[p]) for p in GROUPS)+' |')
    lines += ['', 'Macro metrics average the three groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    (output/'metrics.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print('\n'.join(lines))
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path, nargs='*', default=[BASE/'runs/qwen38-27b-4096', BASE/'runs/gemma3-27b-it'])
    parser.add_argument('--output-dir', type=Path, default=BASE/'reports/merged_classes')
    parser.add_argument('--allow-different-prompts', action='store_true')
    args=parser.parse_args()
    generate(args.runs, args.output_dir, args.allow_different_prompts)
