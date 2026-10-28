"""Export original human-annotated documents into one CSV per educational label."""
import argparse
import csv
import json
from pathlib import Path
import sys

import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parent
FILES = {
    'None': 'none_entries.csv',
    'Minimal': 'minimal_entries.csv',
    'Basic': 'basic_entries.csv',
    'Good': 'good_entries.csv',
    'Excellent': 'excellent_entries.csv',
    '❗ Problematic Content ❗': 'problematic_entries.csv',
}


def export(source, output):
    table = pq.read_table(source)
    rows = table.to_pylist()
    unknown = {label for row in rows for label in (row['educational_value_labels'] or [])
               if label is not None and label not in FILES}
    if unknown:
        raise ValueError(f'Unknown labels: {unknown}')
    output.mkdir(parents=True, exist_ok=True)
    csv.field_size_limit(sys.maxsize)
    for label, filename in FILES.items():
        selected = [row for row in rows if label in (row['educational_value_labels'] or [])]
        serialized = [{key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict))
                       else '' if value is None else str(value)
                       for key, value in row.items()} for row in selected]
        path = output/filename
        with path.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=table.column_names)
            writer.writeheader()
            writer.writerows(serialized)
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames == table.column_names
            restored = list(reader)
        if restored != serialized:
            raise ValueError(f'CSV round-trip failed: {path}')
        print(f'{filename}: {len(selected)} documents')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BASE/'data/tat_Cyrl-train.parquet')
    parser.add_argument('--output-dir', type=Path, default=BASE/'results')
    args = parser.parse_args()
    export(args.source, args.output_dir)
