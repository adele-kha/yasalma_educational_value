# Agreement with merged classes

Both human and model labels are mapped into 3 groups before metrics are recalculated. Existing predictions are reused; no additional inference is performed. Each run retains its own recorded prompt.

- **Problematic Content**: Problematic Content
- **None–Minimal**: None, Minimal
- **Basic–Good–Excellent**: Basic, Good, Excellent

Comparison cohort: **3 documents**, shared across all models, with one distinct human group after merging. Human disagreements that resolve to a single merged group are included. Documents with human labels spanning different groups remain excluded.

| Model | Accuracy / micro precision | Macro precision | Macro recall | Macro F1 | Weighted F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.5-397B-A17B (qwen35-397b-a17b-human-inspired) | 66.67% | 22.22% | 33.33% | 26.67% | 53.33% | 0.0000 |

## Qwen/Qwen3.5-397B-A17B (qwen35-397b-a17b-human-inspired)

| Human group | Support | Predicted | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Problematic Content | 1 | 0 | 0.00% | 0.00% | 0.00% | 66.67% |
| None–Minimal | 2 | 3 | 66.67% | 100.00% | 80.00% | 66.67% |
| Basic–Good–Excellent | 0 | 0 | 0.00% | 0.00% | 0.00% | 100.00% |

Confusion matrix: rows are human groups; columns are model groups.

| Human / LLM | Problematic Content | None–Minimal | Basic–Good–Excellent |
|---|---:|---:|---:|
| Problematic Content | 0 | 1 | 0 |
| None–Minimal | 0 | 2 | 0 |
| Basic–Good–Excellent | 0 | 0 | 0 |

Macro metrics average the three groups equally. Undefined precision, recall and F1 use zero. Recall is accuracy within a human group; one-vs-rest accuracy includes true negatives. These metrics assess agreement with human annotations. The original six-class reports are preserved.
