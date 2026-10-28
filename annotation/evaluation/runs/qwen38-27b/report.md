# LLM vs human annotation

Coverage: 3/1557 documents. Complete: False.
Primary comparison: 3 documents with one distinct human label. Conflicting or missing human labels are excluded.

Overall metrics:

- accuracy: 0.0000
- micro_precision: 0.0000
- macro_precision: 0.0000
- macro_recall: 0.0000
- macro_f1: 0.0000
- weighted_f1: 0.0000
- cohens_kappa: -0.1250

| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |
|---|---:|---:|---:|---:|---:|---:|
| None | 1 | 1 | 0.0000 | 0.0000 | 0.0000 | 0.3333 |
| Minimal | 0 | 1 | 0.0000 | 0.0000 | 0.0000 | 0.6667 |
| Basic | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.6667 |
| Good | 0 | 1 | 0.0000 | 0.0000 | 0.0000 | 0.6667 |
| Excellent | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| Problematic Content | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.6667 |

Confusion matrix (rows: human; columns: LLM):

| Human / LLM | None | Minimal | Basic | Good | Excellent | Problematic Content |
|---|---:|---:|---:|---:|---:|---:|
| None | 0 | 1 | 0 | 0 | 0 | 0 |
| Minimal | 0 | 0 | 0 | 0 | 0 | 0 |
| Basic | 0 | 0 | 0 | 1 | 0 | 0 |
| Good | 0 | 0 | 0 | 0 | 0 | 0 |
| Excellent | 0 | 0 | 0 | 0 | 0 | 0 |
| Problematic Content | 1 | 0 | 0 | 0 | 0 | 0 |

Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; recall is accuracy within the human class. The supplementary all_human_annotations metrics compare each individual human vote, weighting documents with more votes more heavily. Partial coverage can bias results; failed predictions never count as None. Agreement measures consistency with these human annotations, not objective correctness.
