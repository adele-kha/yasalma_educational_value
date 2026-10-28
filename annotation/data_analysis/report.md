# FineWeb-C Tatar educational values

Scope: all 1,557 documents in `tat_Cyrl/train`.

Non-None: **988 documents** (63.46%) and **988 annotation entries**.

| Label | Annotation entries | % of annotations | Documents | % of documents |
|---|---:|---:|---:|---:|
| Basic | 526 | 33.696 | 526 | 33.783 |
| Excellent | 20 | 1.281 | 20 | 1.285 |
| Good | 60 | 3.844 | 60 | 3.854 |
| Minimal | 343 | 21.973 | 343 | 22.03 |
| None | 573 | 36.707 | 572 | 36.737 |
| ❗ Problematic Content ❗ | 39 | 2.498 | 39 | 2.505 |

## Missingness and disagreement

- null_label_lists: 0
- empty_label_lists: 0
- null_label_entries: 0
- documents_with_educational_rating: 949
- documents_with_any_non_none_label: 988
- documents_with_only_none_labels: 569
- documents_with_mixed_none_and_non_none: 3
- documents_without_non_null_labels: 0
- documents_with_multiple_distinct_labels: 3

The literal string `None` is a rating, distinct from null entries or missing/empty lists. Non-None means a non-null label unequal to that exact string. A document counts if any annotation qualifies. Problematic Content is included in the literal non-None count; documents_with_educational_rating counts only Minimal, Basic, Good, or Excellent. Document percentages can overlap when annotators give different labels. No majority vote or numeric score is inferred.

Source: https://huggingface.co/datasets/data-is-better-together/fineweb-c/viewer/tat_Cyrl/train?p=15

Local Parquet SHA-256: `0b801f6b86cd468ef49f085257a2cff5329d354c43c6ead38f93a6807e17be14`
