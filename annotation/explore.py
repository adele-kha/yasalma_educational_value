"""Profile all educational-value annotations in a local FineWeb-C Parquet split."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parent
SOURCE = 'https://huggingface.co/datasets/data-is-better-together/fineweb-c/viewer/tat_Cyrl/train?p=15'


def analyze(source, output):
    rows = pq.read_table(source, columns=['id', 'educational_value_labels']).to_pylist()
    labels = Counter()
    documents = Counter()
    combinations = Counter()
    counts = Counter(dict.fromkeys([
        "null_label_lists", "empty_label_lists", "null_label_entries",
        "documents_with_educational_rating"], 0))
    for row in rows:
        values = row['educational_value_labels']
        if values is None:
            counts['null_label_lists'] += 1
            values = []
        elif not values:
            counts['empty_label_lists'] += 1
        counts['null_label_entries'] += sum(v is None for v in values)
        valid = [v for v in values if v is not None]
        labels.update(valid)
        documents.update(set(valid))
        combinations[tuple(sorted(set(valid)))] += 1
        non_none = [v for v in valid if v != 'None']
        counts['documents_with_educational_rating'] += any(v in {'Minimal', 'Basic', 'Good', 'Excellent'} for v in valid)
        counts['documents_with_any_non_none_label'] += bool(non_none)
        counts['documents_with_only_none_labels'] += bool(valid) and all(v == 'None' for v in valid)
        counts['documents_with_mixed_none_and_non_none'] += bool(non_none) and 'None' in valid
        counts['documents_without_non_null_labels'] += not valid
        counts['documents_with_multiple_distinct_labels'] += len(set(valid)) > 1
    total = len(rows)
    annotations = sum(labels.values())
    distribution = [dict(label=label, annotations=n,
                         annotation_percent=round(100*n/annotations, 3) if annotations else 0,
                         documents=documents[label],
                         document_percent=round(100*documents[label]/total, 3) if total else 0)
                    for label, n in sorted(labels.items())]
    report = dict(source=SOURCE, scope='Complete tat_Cyrl/train split, all rows; viewer page is not a filter',
                  parquet_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  documents=total, unique_ids=len({r['id'] for r in rows}),
                  non_null_annotations=annotations,
                  non_none_annotations=sum(n for label, n in labels.items() if label != 'None'),
                  **counts, distribution=distribution,
                  label_combinations=[dict(labels=list(k), documents=v) for k, v in sorted(combinations.items())])
    output.mkdir(parents=True, exist_ok=True)
    (output/'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    with (output/'distribution.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['label','annotations','annotation_percent','documents','document_percent'])
        writer.writeheader()
        writer.writerows(distribution)
    lines = ['# FineWeb-C Tatar educational values', '', f'Scope: all {total:,} documents in `tat_Cyrl/train`.', '',
             f'Non-None: **{counts["documents_with_any_non_none_label"]:,} documents** '
             f'({100*counts["documents_with_any_non_none_label"]/total:.2f}%) and '
             f'**{report["non_none_annotations"]:,} annotation entries**.', '',
             '| Label | Annotation entries | % of annotations | Documents | % of documents |',
             '|---|---:|---:|---:|---:|']
    lines += [f'| {d["label"]} | {d["annotations"]} | {d["annotation_percent"]} | {d["documents"]} | {d["document_percent"]} |' for d in distribution]
    lines += ['', '## Missingness and disagreement', '']
    lines += [f'- {k}: {v:,}' for k,v in counts.items()]
    lines += ['', 'The literal string `None` is a rating, distinct from null entries or missing/empty lists. '
              'Non-None means a non-null label unequal to that exact string. A document counts if any annotation qualifies. '
              'Problematic Content is included in the literal non-None count; documents_with_educational_rating counts only Minimal, Basic, Good, or Excellent. '
              'Document percentages can overlap when annotators give different labels. No majority vote or numeric score is inferred.', '',
              f'Source: {SOURCE}', f'\nLocal Parquet SHA-256: `{report["parquet_sha256"]}`']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BASE/'data/tat_Cyrl-train.parquet')
    parser.add_argument('--output-dir', type=Path, default=BASE/'results')
    args = parser.parse_args()
    analyze(args.source, args.output_dir)
