# Mapping audit and interpretation

## Source recovery

The local reference contains 1,557 documents. The pinned enriched FineWeb-C
export supplies historical source links for 1,497. Searching the full retained,
test, and removed Tatar partitions adds canonical-exact URL candidates for
41 previously unresolved reference IDs, for 1,538 reference IDs with source URL
evidence. Nineteen remain unresolved under these search rules; their IDs are in
`validation.json`. No reference ID has several distinct canonical-exact URL
candidates in this search.

The full-corpus search matches the original annotation's canonical text for
1,532 IDs. Historical URL evidence is still retained for six other references
whose later full-corpus text no longer matches under this normalization. The
upstream export separately flags 13 later text changes beyond quote
normalization; these are different checks and should not be conflated.

Every reference, including unresolved ones, participates in text-based leakage
screening. Historical source records and later source versions remain separate.
Canonical-exact here means normalized visible word/number sequences, not raw
byte equality or an independent semantic judgment.

## Reference → Markdown coverage

There are crawl candidates linked to 1,386 reference IDs. The best candidate
for each ID has the following canonical character-similarity distribution:

| Best match | Reference IDs |
|---|---:|
| Identical normalized word/number sequence | 151 |
| Nonexact, similarity ≥99% | 173 |
| Similarity ≥95% and <99% | 384 |
| Similarity ≥90% and <95% | 318 |
| Similarity <90% | 360 |

No linked crawl candidate was found for the other 171 reference IDs under the
current URL/text screening rules. This does not prove their absence from every
corpus version or under every possible normalization.

Only the first row currently permits automatic transfer of the human label.
The nonexact rows are **not all substantively different documents**. Inspection
of the closest reference candidates found split words, a split formula token,
and an omitted heading. Other cases involve more substantial extraction/version
differences. A high similarity alone is not permission to transfer a label.

Examples for follow-up in `data/reference_pairs.parquet`:

- `e5d4beb2-4a0b-4b8a-a832-7afb18256428`: a word split into two tokens.
- `2a5734e2-f32a-40de-a708-74654aeab2a0`: a split token in the author name.
- `036afcaa-1abb-42d7-bd94-f0317714731d`: an omitted heading in a long document.
- `2a2532e3-6628-4da1-a74b-ffa5574aa8e2`: formula token boundaries differ.

## Mapping integrity and spot checks

The inventory contains 117,561 distinct normalized-text groups from 118,012
exact pair rows. The 3,994 detected reference/test-related crawl records are
quarantined. The global post-scan pass found no additional eligible rows to
remove in this run; its transitive behavior is covered by a synthetic test.

**No annotation subset is selected.** The previous 10k file and its 80/20 policy
were removed at the user's request. The inventory has no class or source quotas,
annotation split, or generated labels. Near-duplicate handling for future
sampling remains undecided. Full raw match records and texts are retained in the
SQLite checkpoints, so the corpus need not be rescanned for a future policy.

The independent audit checks the entire inventory's source IDs, locators and
canonical hashes, plus exclusion IDs/URLs/hashes. A separate 20-pair diagnostic
pack rechecks full original plain and Markdown text and the reference guard.
Diagnostic examples are not an annotation or training set.

Earlier excerpt inspection covered seven accepted examples from seven sources,
four near candidates, four rejected URL candidates, and five closest nonexact
reference candidates. Accepted examples preserve paragraph content, including an
encyclopedia title rendered as a Markdown heading. Mixed-language/low-quality
text remains aligned rather than silently cleaned. Rejected cases include both
small banner/timestamp differences and changed page contents. This is an agent
spot-check, not a new human annotation or an estimated semantic error rate.

Full-text diagnostic examples are in `data/accepted_review_pack.jsonl` and
`data/rejected_review_pack.jsonl`. Their purpose is mapping review only. Artifact
hashes, validation scope and dependency versions are in `validation.json`.

## Scope and next decision

The strict intersection is not representative of all crawl-res records. For
example, all 205,163 `ruwiki` rows have zero eligible exact pairs in this search;
only 234 unique `finewiki` pairs qualify out of 314,639 source rows. The source
and length tables in `report.md` quantify these gaps. Additional targeted human
evaluation is needed before generalizing a classifier to those sources.

Sampling and annotation are deferred until a specific policy is agreed. No LLM
annotation, label generation, classifier training, upload, or deployment was
performed. Expanding the Markdown gold benchmark beyond the 151 strict-equivalent
reference IDs requires review of nonexact candidates. The existing reference is
a development benchmark because it has informed model/prompt selection; it is
not a pristine final test set.
