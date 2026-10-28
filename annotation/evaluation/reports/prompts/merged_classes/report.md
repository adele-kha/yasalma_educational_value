# Agreement with merged classes

Both human and model labels are mapped into 3 groups before metrics are recalculated. Existing predictions are reused; no additional inference is performed. Each run retains its own recorded prompt.

Source hashes match; this comparison explicitly allows different prompt versions, identified by run folder below.

- **Problematic Content**: Problematic Content
- **None–Minimal**: None, Minimal
- **Basic–Good–Excellent**: Basic, Good, Excellent

Comparison cohort: **1,557 documents**, shared across all models, with one distinct human group after merging. The three original None/Minimal human disagreements now fall within the same group and are included. Documents with human labels spanning different groups would remain excluded.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B (qwen38-27b-4096) | 79.13% | 67.44% | 66.69% | 66.12% | 79.23% | 0.6044 |
| Qwen/Qwen3.8-27B (qwen38-27b-human-inspired) | 86.06% | 78.38% | 70.49% | 73.02% | 85.91% | 0.7256 |

## Qwen/Qwen3.8-27B (qwen38-27b-4096)

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

## Qwen/Qwen3.8-27B (qwen38-27b-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 39 | 22 | 63.64% | 35.90% | 45.90% | 97.88% |
| None–Minimal | 912 | 856 | 91.24% | 85.64% | 88.35% | 86.77% |
| Basic–Good–Excellent | 606 | 679 | 80.27% | 89.93% | 84.82% | 87.48% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 14 | 16 | 9 |
| None–Minimal | 6 | 781 | 125 |
| Basic–Good–Excellent | 2 | 59 | 545 |

Macro metrics average the three groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.
