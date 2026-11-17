# Agreement with merged classes

Both human and model labels are mapped into 3 groups before metrics are recalculated. Existing predictions are reused; no additional inference is performed. Each run retains its own recorded prompt.

- **Problematic Content**: Problematic Content
- **None–Minimal**: None, Minimal
- **Basic–Good–Excellent**: Basic, Good, Excellent

Comparison cohort: **1,557 documents**, shared across all models, with one distinct human group after merging. Human disagreements that resolve to a single merged group are included. Documents with human labels spanning different groups remain excluded.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B (qwen38-27b-human-inspired) | 86.06% | 78.38% | 70.49% | 73.02% | 85.91% | 0.7256 |
| meta-models/muse-spark-open (muse-spark-open-human-inspired) | 86.32% | 79.53% | 70.67% | 73.45% | 86.15% | 0.7304 |
| nvidia/Nemotron-3-Ultra-550b-a55b (nemotron3-ultra-550b-a55b-human-inspired) | 85.55% | 80.94% | 65.29% | 68.12% | 85.12% | 0.7134 |

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

## meta-models/muse-spark-open (muse-spark-open-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 39 | 21 | 66.67% | 35.90% | 46.67% | 97.94% |
| None–Minimal | 912 | 858 | 91.26% | 85.86% | 88.47% | 86.90% |
| Basic–Good–Excellent | 606 | 678 | 80.68% | 90.26% | 85.20% | 87.80% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 14 | 17 | 8 |
| None–Minimal | 6 | 783 | 123 |
| Basic–Good–Excellent | 1 | 58 | 547 |

## nvidia/Nemotron-3-Ultra-550b-a55b (nemotron3-ultra-550b-a55b-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 39 | 11 | 72.73% | 20.51% | 32.00% | 97.82% |
| None–Minimal | 912 | 865 | 90.06% | 85.42% | 87.68% | 85.93% |
| Basic–Good–Excellent | 606 | 681 | 80.03% | 89.93% | 84.69% | 87.35% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 8 | 26 | 5 |
| None–Minimal | 2 | 779 | 131 |
| Basic–Good–Excellent | 1 | 60 | 545 |

Macro metrics average the three groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.

## Run coverage

The main comparison above includes complete runs only. Incomplete runs are excluded from the ranking; their limited merged-class results are stored under `partial/` and are not comparable to full-cohort results.

| Model | Successful / total | Included in main comparison |
|---|---:|---|
| Qwen/Qwen3.8-27B | 1557/1557 | True |
| meta-models/muse-spark-open | 1557/1557 | True |
| Qwen/Qwen3.5-397B-A17B | 3/1557 | False |
| nvidia/Nemotron-3-Ultra-550b-a55b | 1557/1557 | True |

Recorded API errors and full coverage details: `coverage.json`.
