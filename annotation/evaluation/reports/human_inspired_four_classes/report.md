# Agreement with merged classes

Both human and model labels are mapped into 4 groups before metrics are recalculated. Existing predictions are reused; no additional inference is performed. Each run retains its own recorded prompt.

- **None**: None
- **Minimal–Basic**: Minimal, Basic
- **Good–Excellent**: Good, Excellent
- **Problematic Content**: Problematic Content

Comparison cohort: **1,554 documents**, shared across all models, with one distinct human group after merging. Human disagreements that resolve to a single merged group are included. Documents with human labels spanning different groups remain excluded.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B (qwen38-27b-human-inspired) | 64.80% | 57.63% | 53.37% | 52.73% | 65.14% | 0.3628 |
| nvidia/Nemotron-3-Ultra-550b-a55b (nemotron3-ultra-550b-a55b-human-inspired) | 61.90% | 58.54% | 53.51% | 48.65% | 63.58% | 0.3843 |
| meta-models/muse-spark-open (muse-spark-open-human-inspired) | 62.55% | 57.72% | 58.28% | 52.84% | 64.61% | 0.3992 |

## Qwen/Qwen3.8-27B (qwen38-27b-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 386 | 75.39% | 51.14% | 60.94% | 76.00% |
| Minimal–Basic | 866 | 978 | 67.69% | 76.44% | 71.80% | 66.54% |
| Good–Excellent | 80 | 168 | 23.81% | 50.00% | 32.26% | 89.19% |
| Problematic Content | 39 | 22 | 63.64% | 35.90% | 45.90% | 97.88% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | None | Minimal–Basic | Good–Excellent | Problematic Content |
|---|---:|---:|---:|---:|
| None | 291 | 269 | 6 | 3 |
| Minimal–Basic | 80 | 662 | 119 | 5 |
| Good–Excellent | 5 | 35 | 40 | 0 |
| Problematic Content | 10 | 12 | 3 | 14 |

## nvidia/Nemotron-3-Ultra-550b-a55b (nemotron3-ultra-550b-a55b-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 667 | 66.27% | 77.68% | 71.52% | 77.35% |
| Minimal–Basic | 866 | 599 | 77.13% | 53.35% | 63.07% | 65.19% |
| Good–Excellent | 80 | 277 | 18.05% | 62.50% | 28.01% | 83.46% |
| Problematic Content | 39 | 11 | 72.73% | 20.51% | 32.00% | 97.81% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | None | Minimal–Basic | Good–Excellent | Problematic Content |
|---|---:|---:|---:|---:|
| None | 442 | 106 | 20 | 1 |
| Minimal–Basic | 198 | 462 | 205 | 1 |
| Good–Excellent | 9 | 20 | 50 | 1 |
| Problematic Content | 18 | 11 | 2 | 8 |

## meta-models/muse-spark-open (muse-spark-open-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 640 | 68.59% | 77.15% | 72.62% | 78.70% |
| Minimal–Basic | 866 | 602 | 77.41% | 53.81% | 63.49% | 65.51% |
| Good–Excellent | 80 | 291 | 18.21% | 66.25% | 28.57% | 82.95% |
| Problematic Content | 39 | 21 | 66.67% | 35.90% | 46.67% | 97.94% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | None | Minimal–Basic | Good–Excellent | Problematic Content |
|---|---:|---:|---:|---:|
| None | 439 | 110 | 16 | 4 |
| Minimal–Basic | 178 | 466 | 219 | 3 |
| Good–Excellent | 8 | 19 | 53 | 0 |
| Problematic Content | 15 | 7 | 3 | 14 |

Macro metrics average the 4 groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.
