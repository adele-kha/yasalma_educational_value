# Nebius evaluation results — October 28, 2026

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

- [Side-by-side comparison, including per-class precision, recall, F1 and accuracy](comparison.md)
- [Machine-readable comparison](comparison.json)
- [Gemma relabeled dataset (original schema)](runs/gemma3-27b-it/llm_annotations.parquet)
- [Gemma report and confusion matrix](runs/gemma3-27b-it/report.md)
- [Gemma document comparisons and reasons](runs/gemma3-27b-it/comparisons.csv)
- [Qwen relabeled dataset (original schema)](runs/qwen38-27b-4096/llm_annotations.parquet)
- [Qwen report and confusion matrix](runs/qwen38-27b-4096/report.md)
- [Qwen document comparisons and reasons](runs/qwen38-27b-4096/comparisons.csv)

Agreement measures consistency with the supplied human annotations, not independent correctness. Full exports were checked for identical source schema, metadata, document order, and preservation of every field other than model labels, annotator IDs and recomputed problematic-content fields.
