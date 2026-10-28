# LLM vs human annotation

Coverage: 1557/1557 documents. Complete: True.
Reasons exceeding the 100-word instruction: 1 (valid explicit labels retained).
Primary comparison: 1554 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.4569
- micro_precision: 0.4569
- macro_precision: 0.3944
- macro_recall: 0.4172
- macro_f1: 0.3726
- weighted_f1: 0.4845
- cohens_kappa: 0.2771

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 330 | 0.7576 | 0.4394 | 0.5562 | 0.7432 |
| Minimal | 340 | 391 | 0.3274 | 0.3765 | 0.3502 | 0.6943 |
| Basic | 526 | 497 | 0.5594 | 0.5285 | 0.5435 | 0.6995 |
| Good | 60 | 280 | 0.1286 | 0.6000 | 0.2118 | 0.8275 |
| Excellent | 20 | 22 | 0.1818 | 0.2000 | 0.1905 | 0.9781 |
| Problematic Content | 39 | 34 | 0.4118 | 0.3590 | 0.3836 | 0.9710 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 250 | 224 | 81 | 9 | 0 | 5 |
| Minimal | 62 | 128 | 114 | 29 | 3 | 4 |
| Basic | 6 | 25 | 278 | 193 | 14 | 10 |
| Good | 1 | 6 | 16 | 36 | 1 | 0 |
| Excellent | 1 | 3 | 1 | 10 | 4 | 1 |
| Problematic Content | 10 | 5 | 7 | 3 | 0 | 14 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
