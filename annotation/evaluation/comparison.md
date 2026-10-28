# Model comparison with unchanged prompt

All metrics below use the same **1,554 documents** with one distinct human label and a successful prediction from every model. Source and prompt hashes match across runs.

| Model | Successful / total | Accuracy | Macro precision | Macro recall | Macro F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B | 1557/1557 | 45.69% | 39.44% | 41.72% | 37.26% | 0.2771 |
| google/gemma-3-27b-it | 1557/1557 | 22.52% | 36.08% | 24.65% | 14.68% | 0.0172 |

## Qwen/Qwen3.8-27B

| Human class | Support | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|
| None | 569 | 75.76% | 43.94% | 55.62% | 74.32% |
| Minimal | 340 | 32.74% | 37.65% | 35.02% | 69.43% |
| Basic | 526 | 55.94% | 52.85% | 54.35% | 69.95% |
| Good | 60 | 12.86% | 60.00% | 21.18% | 82.75% |
| Excellent | 20 | 18.18% | 20.00% | 19.05% | 97.81% |
| Problematic Content | 39 | 41.18% | 35.90% | 38.36% | 97.10% |

Run: `annotation/evaluation/runs/qwen38-27b-4096`. The run report also contains the confusion matrix and metrics on all its own successful documents.

## google/gemma-3-27b-it

| Human class | Support | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|
| None | 569 | 52.94% | 1.58% | 3.07% | 63.45% |
| Minimal | 340 | 22.55% | 25.00% | 23.71% | 64.80% |
| Basic | 526 | 31.90% | 39.54% | 35.31% | 50.97% |
| Good | 60 | 9.09% | 76.67% | 16.25% | 69.50% |
| Excellent | 20 | 0.00% | 0.00% | 0.00% | 98.71% |
| Problematic Content | 39 | 100.00% | 5.13% | 9.76% | 97.62% |

Run: `annotation/evaluation/runs/gemma3-27b-it`. The run report also contains the confusion matrix and metrics on all its own successful documents.

Accuracy equals micro precision for this single-label task. Macro metrics average all six classes with undefined precision/recall/F1 scored as zero. Agreement is measured against the supplied human labels. Any incomplete coverage is shown above; restricting to the shared cohort can change results relative to the individual run reports.
