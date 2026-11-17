# LLM vs human annotation

Coverage: 1557/1557 documents. Complete: True.
Reasons exceeding the 100-word instruction: 1 (valid explicit labels retained).
Primary comparison: 1554 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.5644
- micro_precision: 0.5644
- macro_precision: 0.4719
- macro_recall: 0.4016
- macro_f1: 0.3848
- weighted_f1: 0.5729
- cohens_kappa: 0.3955

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 667 | 0.6627 | 0.7768 | 0.7152 | 0.7735 |
| Minimal | 340 | 196 | 0.3776 | 0.2176 | 0.2761 | 0.7503 |
| Basic | 526 | 403 | 0.7965 | 0.6103 | 0.6911 | 0.8153 |
| Good | 60 | 264 | 0.1136 | 0.5000 | 0.1852 | 0.8301 |
| Excellent | 20 | 13 | 0.1538 | 0.1000 | 0.1212 | 0.9813 |
| Problematic Content | 39 | 11 | 0.7273 | 0.2051 | 0.3200 | 0.9781 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 442 | 91 | 15 | 19 | 1 | 1 |
| Minimal | 170 | 74 | 50 | 45 | 0 | 1 |
| Basic | 28 | 17 | 321 | 154 | 6 | 0 |
| Good | 6 | 5 | 14 | 30 | 4 | 1 |
| Excellent | 3 | 1 | 0 | 14 | 2 | 0 |
| Problematic Content | 18 | 8 | 3 | 2 | 0 | 8 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
