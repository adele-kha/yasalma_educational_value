# FineWeb ↔ crawl-res mapping

Crawl rows scanned: **4,265,586**. Reference documents: **1,557**.
Eligible exact-content inventory: **117,561 unique normalized texts**. No annotation subset is selected.
Excluded reference/test-related crawl records: **3,994**.
Reference documents linked to crawl records: **1,386**; with equivalent Markdown: **151**.

## Pair decisions

| Status | Crawl rows |
|---|---:|
| exact_visible_tokens | 118,012 |
| excluded_reference_or_test | 3,994 |
| near_requires_review | 244,952 |
| no_fineweb_url_candidate | 3,197,631 |
| url_content_mismatch | 700,997 |

## Source coverage / selection bias

| Source | All crawl rows | Unique exact paired texts |
|---|---:|---:|
| community-oscar-tatar | 290,501 | 17,428 |
| crawl-raw | 3,058,862 | 75,487 |
| culturax | 37,171 | 214 |
| fineweb2 | 14,337 | 3,537 |
| finewiki | 314,639 | 234 |
| hplt2 | 196,230 | 11,676 |
| hplt3 | 148,683 | 8,985 |
| ruwiki | 205,163 | 0 |

## Canonical character-length coverage

| Length band | All crawl rows (screen) | Unique exact paired texts |
|---|---:|---:|
| <500 | 1,939,148 | 27,953 |
| 500–1999 | 1,709,577 | 63,597 |
| 2000–7999 | 542,920 | 23,344 |
| 8000+ | 73,941 | 2,667 |

## Limitations

- Only Tatar Cyrillic retained/train, retained/test and removed/train in the pinned FineWeb release were searched; historical recovery uses the pinned upstream metadata export.
- Training acceptance requires identical normalized visible word/number sequences, not just a URL match. Punctuation/casing/Unicode presentation are normalized; images and their semantics are not evaluated.
- Near-equivalent pairs are audit candidates only and are not included in the exact-pair inventory.
- Reference near-duplicate screening uses a finite anchor set and similarity threshold; it is approximate and cannot prove absence of every transformed duplicate.
- The inventory groups exact canonical-content duplicates only; near-duplicate and sampling policies between candidates have not been chosen.
- The exact-pair inventory is an intersection, not a representative sample of crawl-res. No annotation subset has been selected.
- All-crawl length bands use the cheap Markdown screen; paired/sample bands use fully parsed visible text. The bands are approximate screening diagnostics, not tokenizer lengths.
- The existing reference set has informed model/prompt development; it is a development benchmark, not a pristine final test set.
- No annotation set was selected and no LLM labels were generated.

Raw text, pair tables, exclusions, audit candidates and resumable SQLite checkpoints are in ignored `mapping/data/`. Full policy, pinned revisions, reference SHA-256 and aggregate counts are in `summary.json`.
