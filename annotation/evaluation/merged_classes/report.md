# Agreement with merged classes

Both human and model labels are mapped into 3 groups before metrics are recalculated. Existing predictions are reused; no inference or prompt changes.

- **Problematic Content**: Problematic Content
- **None–Minimal**: None, Minimal
- **Basic–Good–Excellent**: Basic, Good, Excellent

Comparison cohort: **1,557 documents**, shared across all models, with one distinct human group after merging. The three original None/Minimal human disagreements now fall within the same group and are included. Documents with human labels spanning different groups would remain excluded.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B | 79.13% | 67.44% | 66.69% | 66.12% | 79.23% | 0.6044 |
| google/gemma-3-27b-it | 60.50% | 80.10% | 46.86% | 43.44% | 57.85% | 0.2964 |

## Qwen/Qwen3.8-27B

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 39 | 34 | 41.18% | 35.90% | 38.36% | 97.11% |
| None–Minimal | 912 | 722 | 92.11% | 72.92% | 81.40% | 80.48% |
| Basic–Good–Excellent | 606 | 801 | 69.04% | 91.25% | 78.61% | 80.67% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 14 | 15 | 10 |
| None–Minimal | 9 | 665 | 238 |
| Basic–Good–Excellent | 11 | 42 | 553 |

## google/gemma-3-27b-it

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 39 | 2 | 100.00% | 5.13% | 9.76% | 97.62% |
| None–Minimal | 912 | 395 | 89.87% | 38.93% | 54.32% | 61.66% |
| Basic–Good–Excellent | 606 | 1160 | 50.43% | 96.53% | 66.25% | 61.72% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 2 | 19 | 18 |
| None–Minimal | 0 | 355 | 557 |
| Basic–Good–Excellent | 0 | 21 | 585 |

Macro metrics average the three groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.
