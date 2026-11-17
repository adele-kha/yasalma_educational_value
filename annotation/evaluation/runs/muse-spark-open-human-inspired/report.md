# LLM vs human annotation

Coverage: 1557/1557 documents. Complete: True.
Reasons exceeding the 100-word instruction: 0 (valid explicit labels retained).
Primary comparison: 1554 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.5689
- micro_precision: 0.5689
- macro_precision: 0.4838
- macro_recall: 0.4515
- macro_f1: 0.4285
- weighted_f1: 0.5837
- cohens_kappa: 0.4072

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 569 | 640 | 0.6859 | 0.7715 | 0.7262 | 0.7870 |
| Minimal | 340 | 215 | 0.4372 | 0.2765 | 0.3387 | 0.7638 |
| Basic | 526 | 387 | 0.7726 | 0.5684 | 0.6550 | 0.7973 |
| Good | 60 | 277 | 0.1264 | 0.5833 | 0.2077 | 0.8282 |
| Excellent | 20 | 14 | 0.2143 | 0.1500 | 0.1765 | 0.9820 |
| Problematic Content | 39 | 21 | 0.6667 | 0.3590 | 0.4667 | 0.9794 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 439 | 92 | 18 | 16 | 0 | 4 |
| Minimal | 155 | 94 | 53 | 35 | 1 | 2 |
| Basic | 23 | 20 | 299 | 176 | 7 | 1 |
| Good | 4 | 6 | 12 | 35 | 3 | 0 |
| Excellent | 4 | 1 | 0 | 12 | 3 | 0 |
| Problematic Content | 15 | 2 | 5 | 3 | 0 | 14 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
