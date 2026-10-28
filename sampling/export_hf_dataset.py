"""Package the annotation sample as Parquet; optionally upload to Hugging Face."""

import argparse
from collections import Counter
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def export_sample(source, output):
    sample = json.loads(source.read_text(encoding="utf-8"))
    records = []
    for entry in sample["samples"]:
        document, selection = entry["document"], entry["sampling"]
        records.append({
            "id": str(document["id"]),
            "text": document["text"],
            "publish_year": document.get("publish_year"),
            "genre": document.get("genre"),
            "sampling_component": selection["component"],
            "sampling_rationale": selection["rationale"],
            "normalized_length": selection["length"],
            "length_group": selection["length_bin"],
            "educational_value": None,
            "annotation_notes": None,
        })
    if not records or len({record["id"] for record in records}) != len(records):
        raise ValueError("Sample must be nonempty and document IDs must be unique")
    schema = pa.schema([
        ("id", pa.string()), ("text", pa.string()), ("publish_year", pa.int64()),
        ("genre", pa.string()), ("sampling_component", pa.string()),
        ("sampling_rationale", pa.list_(pa.string())), ("normalized_length", pa.int64()),
        ("length_group", pa.string()), ("educational_value", pa.int64()),
        ("annotation_notes", pa.string()),
    ])
    table = pa.Table.from_pylist(records, schema=schema)
    output.mkdir(parents=True, exist_ok=True)
    data_dir = output / "data"
    data_dir.mkdir(exist_ok=True)
    parquet_path = data_dir / "train.parquet"
    pq.write_table(table, parquet_path, compression="zstd")
    restored = pq.read_table(parquet_path)
    if not restored.equals(table):
        raise ValueError("Parquet round-trip validation failed")
    metadata = sample["metadata"]
    (output / "sampling_report.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = Counter(record["sampling_component"] for record in records)
    card = f"""---
language:
- tt
task_categories:
- text-classification
size_categories:
- n<1K
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.parquet
---

# Tatar educational value annotation sample

An unannotated pool of {len(records)} full documents sampled from
[{metadata['policy']['dataset']}](https://huggingface.co/datasets/{metadata['policy']['dataset']})
at revision `{metadata['resolved_revision']}`.

The `train` split is a storage convention for the annotation pool. Training and
evaluation partitions have not been assigned. Documents have not been selected
or labeled as highly educational.

## Columns

| Column | Meaning |
| --- | --- |
| id | Original document ID |
| text | Full original text, unchanged |
| publish_year | Nullable publication year |
| genre | Original nullable genre string |
| sampling_component | diversity, random, or edge |
| sampling_rationale | List of selection reasons |
| normalized_length | Character length after HTML stripping and whitespace normalization |
| length_group | short, medium, or long, using corpus quantiles |
| educational_value | Nullable int64; all values are unset |
| annotation_notes | Nullable string; all values are unset |

## Sampling

Components: {counts['diversity']} diversity, {counts['random']} random,
{counts['edge']} edge cases. Seed: {metadata['policy']['seed']}.
Scanned {metadata['scan']['scanned']:,} rows and retained
{metadata['scan']['eligible']:,} eligible documents after filtering.

The random component was drawn first as a simple random sample of the eligible,
deduplicated corpus. Edge cases were reserved next, followed by greedy diversity
selection. The complete policy, achieved coverage, relaxations, source revision,
and deduplication limitations are recorded in `sampling_report.json`.
Coverage goals are soft and not all targets were achieved. Near-duplicate
detection is approximate. This mixed sampling design is not a representative
random sample of the corpus as a whole.

## Annotation

The educational-value scoring rubric has not been defined. Leave
`educational_value` and `annotation_notes` null until annotation begins; null
does not mean a score of zero. Keep original IDs and texts unchanged.

## Source and access

This sample is derived from the gated source dataset linked above. Consult its
dataset card and applicable terms for source licensing and attribution. This
repository does not assign a new license to the source documents.
"""
    (output / "README.md").write_text(card, encoding="utf-8")
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).with_name("sample.json"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("hf_dataset"))
    parser.add_argument("--repo-id", default="yasalma/tt-educational-value-sample")
    parser.add_argument("--upload", action="store_true", help="Upload the prepared files to a private dataset repository")
    args = parser.parse_args()
    count = export_sample(args.source, args.output_dir)
    print(f"Prepared and validated {count} rows in {args.output_dir}", flush=True)
    if args.upload:
        from huggingface_hub import HfApi
        api = HfApi()
        api.create_repo(repo_id=args.repo_id, repo_type="dataset", private=True, exist_ok=True)
        commit = api.upload_folder(
            repo_id=args.repo_id, repo_type="dataset", folder_path=str(args.output_dir),
            allow_patterns=["data/train.parquet", "README.md", "sampling_report.json"],
            commit_message="Upload educational value annotation sample and sampling report",
        )
        info = api.dataset_info(args.repo_id, revision=commit.oid)
        print(f"Uploaded https://huggingface.co/datasets/{args.repo_id} at {commit.oid}; private={info.private}")


if __name__ == "__main__":
    main()
