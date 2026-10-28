# LLM vs human annotation

Coverage: 1557/1557 documents. Complete: True.
Reasons exceeding the 100-word instruction: 0 (valid explicit labels retained).
Primary comparison: 1554 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.5753
- micro_precision: 0.5753
- macro_precision: 0.5319
- macro_recall: 0.4414
- macro_f1: 0.4317
- weighted_f1: 0.5913
- cohens_kappa: 0.4162

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 386 | 0.7539 | 0.5114 | 0.6094 | 0.7600 |
| Minimal | 340 | 467 | 0.3747 | 0.5147 | 0.4337 | 0.7059 |
| Basic | 526 | 511 | 0.7515 | 0.7300 | 0.7406 | 0.8269 |
| Good | 60 | 166 | 0.1747 | 0.4833 | 0.2566 | 0.8919 |
| Excellent | 20 | 2 | 0.5000 | 0.0500 | 0.0909 | 0.9871 |
| Problematic Content | 39 | 22 | 0.6364 | 0.3590 | 0.4590 | 0.9788 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 291 | 239 | 30 | 6 | 0 | 3 |
| Minimal | 73 | 175 | 66 | 23 | 0 | 3 |
| Basic | 7 | 37 | 384 | 95 | 1 | 2 |
| Good | 3 | 8 | 20 | 29 | 0 | 0 |
| Excellent | 2 | 2 | 5 | 10 | 1 | 0 |
| Problematic Content | 10 | 6 | 6 | 3 | 0 | 14 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
