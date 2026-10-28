# Prompt comparison

All metrics below use the same **1,554 documents** with one distinct human label and a successful prediction from every model. Source hashes match; different prompt hashes are explicitly allowed.

| Model | Successful / total | Accuracy | Macro precision | Macro recall | Macro F1 | Kappa |
|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.8-27B (qwen38-27b-4096) | 1557/1557 | 45.69% | 39.44% | 41.72% | 37.26% | 0.2771 |
| Qwen/Qwen3.8-27B (qwen38-27b-human-inspired) | 1557/1557 | 57.53% | 53.19% | 44.14% | 43.17% | 0.4162 |

## Qwen/Qwen3.8-27B (qwen38-27b-4096)

| Human class | Support | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|
| None | 569 | 75.76% | 43.94% | 55.62% | 74.32% |
| Minimal | 340 | 32.74% | 37.65% | 35.02% | 69.43% |
| Basic | 526 | 55.94% | 52.85% | 54.35% | 69.95% |
| Good | 60 | 12.86% | 60.00% | 21.18% | 82.75% |
| Excellent | 20 | 18.18% | 20.00% | 19.05% | 97.81% |
| Problematic Content | 39 | 41.18% | 35.90% | 38.36% | 97.10% |

Run: `annotation/evaluation/runs/qwen38-27b-4096`. The run report also contains the confusion matrix and metrics on all its own successful documents.

## Qwen/Qwen3.8-27B (qwen38-27b-human-inspired)

| Human class | Support | Precision | Recall / within-class accuracy | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|
| None | 569 | 75.39% | 51.14% | 60.94% | 76.00% |
| Minimal | 340 | 37.47% | 51.47% | 43.37% | 70.59% |
| Basic | 526 | 75.15% | 73.00% | 74.06% | 82.69% |
| Good | 60 | 17.47% | 48.33% | 25.66% | 89.19% |
| Excellent | 20 | 50.00% | 5.00% | 9.09% | 98.71% |
| Problematic Content | 39 | 63.64% | 35.90% | 45.90% | 97.88% |

Run: `annotation/evaluation/runs/qwen38-27b-human-inspired`. The run report also contains the confusion matrix and metrics on all its own successful documents.

Accuracy equals micro precision for this single-label task. Macro metrics average all six classes with undefined precision/recall/F1 scored as zero. Agreement is measured against the supplied human labels. Any incomplete coverage is shown above; restricting to the shared cohort can change results relative to the individual run reports.
