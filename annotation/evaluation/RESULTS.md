# Nebius evaluation results — October 28, 2026

Latest recount: [four groups with the human-inspired prompt](reports/human_inspired_four_classes/report.md).
The grouping is None, Minimal–Basic, Good–Excellent, and Problematic Content.
The three human None/Minimal conflicts are excluded, leaving 1,554 shared
documents. Accuracy / macro F1: Qwen3.8 **64.80% / 52.73%**, Nemotron Ultra
**61.90% / 48.65%**, and Muse Spark Open **62.55% / 52.84%**.

Latest: [human-inspired prompt with merged classes, including Muse Spark Open and
Nemotron Ultra](reports/human_inspired_merged_classes/report.md).
Qwen3.5-397B-A17B is recorded as incomplete because Nebius removed its serving ID
during the run. See the November 2 section below.

**Qwen3.8-27B and Gemma-3-27b-it both completed all 1,557 documents with the unchanged supplied prompt and full texts.**

Primary metrics use the same 1,554 documents with one distinct human label; three conflicting human cases are excluded. Source and prompt hashes match.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Kappa |
|---|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B | 45.69% | 39.44% | 41.72% | 37.26% | 0.2771 |
| google/gemma-3-27b-it | 22.52% | 36.08% | 24.65% | 14.68% | 0.0172 |

## Findings

- Gemma has substantially lower agreement than Qwen with this prompt. Its accuracy is 23.17 percentage points lower.
- Gemma assigns Good to 506 documents in the primary cohort, against 60 human Good labels. Its Good precision is 9.09%. It moves 303 human Basic documents to Good.
- Gemma recognizes only 9/569 human None documents (1.58% recall), and 2/39 Problematic Content documents (5.13% recall). Its 100% Problematic Content precision is based on just two predictions.
- Gemma predicts no Excellent labels. Undefined precision/recall/F1 use zero in macro averages.
- Qwen also rates content higher than humans: 224 human None documents become Minimal, and 193 human Basic documents become Good.

## Execution notes

Both runs use temperature zero and a 4,096-token output allowance. Two truncated Qwen records succeeded with a recorded 16,384-token retry budget. One Qwen reason exceeds 100 words and is flagged; all labels remain valid. Gemma’s longest document initially exceeded the context allowance but succeeded with a 512-token output allowance, preserving all 232,613 input characters. Gemma has no reason-length violations. No failures remain in either run.

Llama 3.3 70B remains inaccessible to this Nebius key (confirmed by direct HTTP 403). GPT OSS has not been tested. The prompt has not been tightened.

## Artifacts

- [Side-by-side comparison, including per-class precision, recall, F1 and accuracy](reports/models/comparison.md)
- [Machine-readable comparison](reports/models/comparison.json)
- [Gemma relabeled dataset (original schema)](runs/gemma3-27b-it/llm_annotations.parquet)
- [Gemma report and confusion matrix](runs/gemma3-27b-it/report.md)
- [Gemma document comparisons and reasons](runs/gemma3-27b-it/comparisons.csv)
- [Qwen relabeled dataset (original schema)](runs/qwen38-27b-4096/llm_annotations.parquet)
- [Qwen report and confusion matrix](runs/qwen38-27b-4096/report.md)
- [Qwen document comparisons and reasons](runs/qwen38-27b-4096/comparisons.csv)

Agreement measures consistency with the supplied human annotations, not independent correctness. Full exports were checked for identical source schema, metadata, document order, and preservation of every field other than model labels, annotator IDs and recomputed problematic-content fields.

## Merged classes

[Three-class report](reports/merged_classes/report.md): Problematic Content, None–Minimal,
and Basic–Good–Excellent. On all 1,557 documents, Qwen accuracy is **79.13%** and
Gemma accuracy is **60.50%**. The original three human None/Minimal conflicts are
resolved by this grouping. All metrics are recalculated from grouped predictions.

## Qwen retest: human-annotation-inspired prompt

The new `prompt_human_annotation_inspired.txt` run completed **1,557/1,557**
documents. The original source, model, temperature and initial response budget
were retained. One truncated response succeeded with a recorded 16,384-token
retry budget. No reason-length violations or failed labels remain.

| Metric | Original prompt | Human-inspired prompt |
|---|---:|---:|
| Six-class accuracy (1,554 documents) | 45.69% | 57.53% |
| Six-class macro precision | 39.44% | 53.19% |
| Six-class macro F1 | 37.26% | 43.17% |
| Merged-class accuracy (1,557 documents) | 79.13% | 86.06% |
| Merged-class macro F1 | 66.12% | 73.02% |

Basic recall improves from 52.85% to 73.00%, and merged None–Minimal recall
from 72.92% to 85.64%. Problematic Content recall stays at 14/39, with precision
improving from 41.18% to 63.64%. Excellent recall falls from 20.00% to 5.00%.
These are comparisons on the existing annotated dataset.

- [Six-class prompt comparison](reports/prompts/comparison.md)
- [Merged-class prompt comparison](reports/prompts/merged_classes/report.md)
- [New relabeled dataset](runs/qwen38-27b-human-inspired/llm_annotations.parquet)
- [New per-document comparisons](runs/qwen38-27b-human-inspired/comparisons.csv)
- [Exact new prompt snapshot](runs/qwen38-27b-human-inspired/prompt_snapshot.txt)

## Additional models — November 2, 2026

Only the unchanged human-annotation-inspired prompt was used for these runs.
The comparison below uses the three merged classes on the same 1,557 documents.
Source and prompt hashes match the existing human-inspired Qwen3.8 baseline.

| Model | Coverage | Merged accuracy | Merged macro F1 |
|---|---:|---:|---:|
| Qwen3.8-27B baseline | 1,557/1,557 | 86.06% | 73.02% |
| Muse Spark Open | 1,557/1,557 | 86.32% | 73.45% |
| Nemotron-3-Ultra-550b-a55b | 1,557/1,557 | 85.55% | 68.12% |
| Qwen3.5-397B-A17B | 3/1,557 | Not ranked | Not ranked |

All three requested serving IDs were initially listed in the live Nebius catalog
and passed a three-document smoke test. Qwen3.5 then returned HTTP 404
`model_not_found` for the remaining 1,554 documents and disappeared from the
catalog. Its three saved predictions are retained in a separate partial merged
report, excluded from the full-cohort ranking. No substitute model was used.
Muse and Nemotron completed without failed predictions or input truncation.
These are agreement metrics on the existing human annotations.

- [Full merged-class comparison and run coverage](reports/human_inspired_merged_classes/report.md)
- [Machine-readable coverage and API errors](reports/human_inspired_merged_classes/coverage.json)
- [Qwen3.5 partial results: three documents only](reports/human_inspired_merged_classes/partial/qwen35-397b-a17b-human-inspired/report.md)
- [Availability snapshot](diagnostics/additional_models_availability.json)

Rebuild the report with
`uv run python annotation/evaluation/run_human_inspired_models.py --report-only`.
