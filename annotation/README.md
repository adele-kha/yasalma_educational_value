# FineWeb-C annotation exploration

Explore the complete `tat_Cyrl/train` split of
[data-is-better-together/fineweb-c](https://huggingface.co/datasets/data-is-better-together/fineweb-c/viewer/tat_Cyrl/train?p=15).
The viewer's `p=15` selects a display page; this analysis covers the full split.

From the repository root:

```bash
uv sync
mkdir -p annotation/data
curl -L --fail 'https://huggingface.co/datasets/data-is-better-together/fineweb-c/resolve/main/tat_Cyrl/train-00000-of-00001.parquet' -o annotation/data/tat_Cyrl-train.parquet
uv run python annotation/explore.py
```

The download is ignored by Git. `results/report.md` contains the readable findings,
`results/summary.json` the counts, combinations and source-file SHA-256, and
`results/distribution.csv` the per-label distribution. These small results are
kept for review. Re-downloading `main` may yield updated data; compare the hash
with the saved summary to confirm the same snapshot.

Labels are reported as stored. Each document can have multiple annotations;
annotation counts and document counts have different denominators. `None` is a
literal rating, not a Python null. The non-None count includes Problematic Content;
the separate educational-rating count includes only Minimal, Basic, Good and
Excellent. No consensus label is imposed.

## Documents by human label

```bash
uv run python annotation/export_by_label.py
```

Creates `results/none_entries.csv`, `minimal_entries.csv`, `basic_entries.csv`,
`good_entries.csv`, `excellent_entries.csv`, and `problematic_entries.csv`.
Each CSV preserves full text and all original columns, with list fields encoded
as JSON and UTF-8 with a BOM for spreadsheet compatibility. A document appears
once per class if any human annotation uses that label; conflicting labels mean
it can appear in multiple files. These exports use human labels, not LLM labels.
The exporter verifies every field by reading each CSV back.
