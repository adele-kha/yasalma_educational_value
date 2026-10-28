# LLM vs human annotation

Coverage: 1557/1557 documents. Complete: True.
Reasons exceeding the 100-word instruction: 0 (valid explicit labels retained).
Primary comparison: 1554 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.2252
- micro_precision: 0.2252
- macro_precision: 0.3608
- macro_recall: 0.2465
- macro_f1: 0.1468
- weighted_f1: 0.1914
- cohens_kappa: 0.0172

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 17 | 0.5294 | 0.0158 | 0.0307 | 0.6345 |
| Minimal | 340 | 377 | 0.2255 | 0.2500 | 0.2371 | 0.6480 |
| Basic | 526 | 652 | 0.3190 | 0.3954 | 0.3531 | 0.5097 |
| Good | 60 | 506 | 0.0909 | 0.7667 | 0.1625 | 0.6950 |
| Excellent | 20 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.9871 |
| Problematic Content | 39 | 2 | 1.0000 | 0.0513 | 0.0976 | 0.9762 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 9 | 258 | 252 | 50 | 0 | 0 |
| Minimal | 2 | 85 | 169 | 84 | 0 | 0 |
| Basic | 0 | 15 | 208 | 303 | 0 | 0 |
| Good | 0 | 5 | 9 | 46 | 0 | 0 |
| Excellent | 1 | 0 | 3 | 16 | 0 | 0 |
| Problematic Content | 5 | 14 | 11 | 7 | 0 | 2 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
