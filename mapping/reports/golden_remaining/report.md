# Focused nonsemantic search for remaining golden documents

Targets: **171**. Full crawl scan complete: **True**. Rows searched: **4,265,586**.

| Best candidate category | Reference documents |
|---|---:|
| near_lexical_review | 37 |
| no_candidate | 60 |
| partial_lexical_review | 8 |
| reordered_lexical_review | 1 |
| url_alias_content_review | 1 |
| weak_lexical_candidate | 40 |
| wikipedia_page_identity_review | 24 |

URL aliases, Wikipedia redirect/page-ID metadata, many compact character passages, rare literal tokens, edit similarity, token overlap and partial string matching are used. No embeddings or LLM inference.

Candidate tables retain full original texts, human labels, locators and lexical evidence. Baseline alignment and labels are unchanged. No training set is selected.

- A lexical candidate is not independent confirmation of document identity or human-label applicability.
- Only exact visible-word equality permits automatic label transfer under the unchanged policy.
- Shared passages may be quotations, boilerplate or partial copies. Multiple candidates are retained.
- The partial-ratio metric is skipped for very long pairs; other full-text metrics still apply. No text is truncated.
