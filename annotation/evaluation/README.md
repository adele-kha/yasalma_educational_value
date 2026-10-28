# Nebius human–LLM evaluation

Evaluate **Qwen3.8-27B** and **Gemma-3-27b-it** with the unchanged prompt.
Llama 3.3 70B requires Nebius account access; GPT OSS remains deferred.
The exact serving IDs must be verified against the account's live Nebius catalog;
no other model is automatically substituted.

Add `NEBIUS_API_KEY` to the ignored root `.env` file. Do not commit credentials.
From the repository root, list available IDs:

```bash
uv run --env-file .env python annotation/evaluation/evaluate.py --list-models
```

Then run each verified model in its own directory:

```bash
uv run --env-file .env python annotation/evaluation/evaluate.py \
  --model '<exact Llama 3.3 70B ID from catalog>' \
  --output-dir annotation/evaluation/runs/llama33-70b

uv run --env-file .env python annotation/evaluation/evaluate.py \
  --model '<exact Qwen3.8-27B ID from catalog>' \
  --output-dir annotation/evaluation/runs/qwen38-27b-4096 --max-tokens 4096
```

For a completed first pass with truncated outputs, add `--retry-max-tokens 16384`
to retry only failed rows with a larger output budget. Overrides are recorded in
`executions.jsonl` and each retried prediction. Source text and prompt stay identical.

Use `--limit 5` for a smoke run, then repeat the same command without `--limit`
to complete the split. Successful rows are reused. Failed rows are retried on
subsequent runs. Four requests run concurrently by default; use `--workers` to
adjust. Requests retry transient HTTP errors and invalid outputs up to three
times. Permanent HTTP errors are recorded for inspection. Raw responses,
reasons, API model IDs, usage and timestamps are saved to `predictions.jsonl`.
Usage reflects returned token counts for the most recent invocation of each
record, including retries returning usage; it is not a billing total.

## Protocol

- Use the attached prompt verbatim from `prompt.txt`, replacing `{example}` with
  the entire original document. Human labels are never sent to the model.
- Temperature is zero. Use a 4,096-token response budget for Qwen3.8 to leave
  room for reasoning before the answer; the generic default is 512 tokens. Validate the required two-field output and six-label vocabulary. A reason
  exceeding 100 words is flagged but does not invalidate an explicit valid label. Truncated or malformed responses
  are failures, not `None` ratings. No input truncation occurs. Documents exceeding
  the serving context limit remain failures; no shorter extract is silently used.
- Record SHA-256 hashes of source and prompt plus model, endpoint and inference
  settings in `manifest.json`. Changed configurations require a new output folder.
- The primary evaluation includes one vote per document with exactly one distinct
  non-null human label (1,554 of 1,557 in the current snapshot). Repeated identical
  votes count once. Three conflicting human cases are excluded from the primary
  metrics and retained in `comparisons.csv`.
- Supplementary metrics compare every human annotation separately; documents
  with multiple votes therefore have more weight. Problematic Content's decorated
  human string is normalized for scoring and restored for dataset export.

## Outputs per model

- `llm_annotations.parquet`: complete dataset with the **same Arrow schema and
  original document order**, one model-generated label per row, and a model
  annotator ID. Text, IDs and language fields are preserved. Problematic-content
  presence and agreement fields are recomputed for the single model vote.
- `llm_annotations.partial.parquet`: successful rows only when any predictions
  are missing. Never presented as a complete relabeling.
- `comparisons.csv`: human labels, model label, reason, agreement and primary
  evaluation eligibility.
- `metrics.json` and `report.md`: coverage, overall accuracy, micro/macro precision,
  macro recall/F1, weighted F1, Cohen's kappa, per-class precision/recall/F1 and
  one-vs-rest accuracy, plus the full confusion matrix. Undefined precision,
  recall and F1 use zero. Partial results are explicitly marked.

Metrics measure agreement with human annotations, not independent correctness.
For single-label classification, micro precision equals accuracy. Per-class
recall measures accuracy within that human class; one-vs-rest accuracy also
includes true negatives and can be high for rare classes.

Rebuild reports without API calls by adding `--report-only` to the same command.
Run local verification:

```bash
uv run python -m unittest discover -s annotation/evaluation -p 'test_*.py'
```

API protocol: [Nebius inference API reference](https://api.tokenfactory.nebius.com/docs).

## Gemma 3 and model comparison

```bash
uv run --env-file .env python annotation/evaluation/evaluate.py \
  --model google/gemma-3-27b-it \
  --output-dir annotation/evaluation/runs/gemma3-27b-it --max-tokens 4096

uv run python annotation/evaluation/compare_models.py \
  annotation/evaluation/runs/qwen38-27b-4096 \
  annotation/evaluation/runs/gemma3-27b-it
```

`comparison.md` and `comparison.json` compare the same documents across models,
verifying identical source/prompt hashes. If either run has failures, only the
shared successful cohort is used for the comparison, with coverage stated.
`--retry-max-tokens 512` can lower the response allowance on failed long Gemma
documents without truncating inputs; requests still exceeding its context limit
remain failures. Budget overrides are recorded per response and execution.
