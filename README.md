# Educational value classification

Source-data exploration for educational value classification and selection of
highly educational Tatar text for Gemma midtraining/fine-tuning.

## Streaming preview

Requires Python 3.10+.

```bash
uv sync
uv run hf auth login
uv run python sampling/preview_datasets.py
```

The script prints three examples from each source:

- https://huggingface.co/datasets/yasalma/crawl-res
- https://huggingface.co/datasets/yasalma/tt-structured-content

Accept any dataset access conditions on Hugging Face first, using the same account
as your login. `tt-structured-content` is gated. A read token in the `HF_TOKEN`
environment variable can be used instead of `uv run hf auth login`; do not commit tokens.

```bash
# Preview just one source.
uv run python sampling/preview_datasets.py --dataset crawl-res --num-examples 5

# Print complete document text (potentially very long).
uv run python sampling/preview_datasets.py --dataset tt-structured-content --num-examples 1 --max-chars 0
```

All fields are printed as readable JSON with Unicode preserved. Strings are
limited to 1,500 characters by default for display only; source records are not
modified. Use `--split` or `--config` if the selected dataset requires a different
split or configuration (`--config` requires selecting one dataset).

Loading always uses `streaming=True` and iteration stops after the requested
number of rows. It does not download or materialize the entire dataset, although
the streaming reader may fetch metadata and data chunks larger than the preview.
It shows the first rows in source order, rather than a random sample. If one
source fails, the script still attempts the other and exits with a nonzero status.

## Annotation sampling

Edit `sampling/sampling_policy.json` to choose component sizes, seed, year/genre quotas,
length quantiles and weights, edge-category weights, detection thresholds, and
coverage-score weights. Then run:

```bash
uv run --env-file .env python sampling/sample_dataset.py
# Optional overrides:
uv run --env-file .env python sampling/sample_dataset.py --policy sampling/sampling_policy.json --seed 123 --output sampling/sample.json
```

The default policy requests 350 diversity + 100 random + 50 edge documents from
`yasalma/tt-structured-content`. The full dataset is scanned with streaming;
original documents are temporarily stored in SQLite on disk, while metadata and
duplicate signatures stay in memory. Allow several GB of temporary disk space.
The temporary database is removed when the run finishes.

`sample.json` contains `metadata` and `samples`. Each sample retains its complete
original record under `document`, with selection component, rationale, normalized
length, metadata groups, and source row under `sampling`. Metadata records the
resolved Hub commit, full policy, corpus statistics, targets, achieved counts,
and relaxations. Reuse the recorded commit with `--revision` to reproduce a run.

Exact duplicate detection uses SHA-256 of HTML-stripped, whitespace-normalized
text, plus unique source IDs. Approximate near-duplicate detection compares token
sets with Jaccard similarity, using shared bottom-hash anchors to find candidates,
bounded anchor buckets, and a bottom-hash sketch prefilter (all configurable).
It can miss duplicates, ignores word order, and may merge texts differing mainly
in repetition. The repetition edge signal measures repeated normalized lines.
The markup signal is the fraction of raw characters occupied by HTML tags.

Random documents are selected first, then edge documents (scarce categories
first, with unused slots redistributed), then diversity documents using a greedy
weighted coverage score. Comma-separated genres are treated as multiple labels.
Year/genre goals use minimum coverage followed by square-root allocation;
qualifying genres receive minimum-coverage opportunities before rare labels. Missing
genre coverage uses prevalence with a configurable minimum floor; format targets
aim for equal markup-heavy and cleaner text. Extreme lengths are excluded from
diversity while moderate candidates remain. Targets are soft: overlapping goals,
quantile ties, available groups, and the year cap can prevent exact attainment.
Inspect the saved target/achievement report before annotation. Edge slots that
cannot be filled by any edge candidate are explicitly marked as fallback draws.

Run the synthetic checks without accessing the Hub:

```bash
uv run python -m unittest discover -s sampling -p 'test_*.py'
```

## Hugging Face export

Prepare the agreed flat Parquet schema, dataset card, and sampling report locally:

```bash
uv run python sampling/export_hf_dataset.py
```

The generated `hf_dataset/` directory is ignored by Git. The exporter validates a
Parquet round trip, preserves full original texts, and gives the initially empty
annotation columns explicit nullable integer/string types.

Upload to `yasalma/tt-educational-value-sample` (created private by default):

```bash
uv run --env-file .env python sampling/export_hf_dataset.py --upload
```

Use `--repo-id`, `--source`, or `--output-dir` to override the defaults.

## FineWeb-C annotation exploration

See [annotation/README.md](annotation/README.md) for the full Tatar split label distribution and reproducible analysis. Previous sampling scripts and generated files are in `sampling/`.

## LLM annotation evaluation

The [Nebius evaluation framework](annotation/evaluation/README.md) uses the supplied
prompt to relabel the Tatar split and report agreement with humans, overall and
per class. Completed models are Qwen3.8-27B and Gemma-3-27b-it; see
[their comparison](annotation/evaluation/comparison.md). Llama 3.3 70B requires
additional Nebius access.
