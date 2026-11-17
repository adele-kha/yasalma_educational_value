---
language:
- tt
task_categories:
- text-classification
tags:
- educational-value
- text-alignment
- tatar
configs:
- config_name: golden
  default: true
  data_files:
  - split: golden
    path: golden.parquet
---

# Mapped crawl-res ↔ FineWeb

This dataset aligns the human-labeled Tatar golden subset of
[FineWeb-C](https://huggingface.co/datasets/data-is-better-together/fineweb-c)
with Markdown documents from
[yasalma/crawl-res](https://huggingface.co/datasets/yasalma/crawl-res), using
[FineWeb-2](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2) source records
to recover URLs and native IDs. It contains **{{rows}} golden documents**, with
one selected crawl-res candidate per golden ID where available. Unmatched golden
documents are retained.

Existing human educational-value labels and saved **{{qwen_model}}** and
**{{muse_model}}** predictions are included. Both model runs used the
human-inspired annotation prompt on the original golden plain text. No new
annotation or model inference was performed to build this dataset.

## Match-label legend

The categories describe alignment evidence, independently of educational value.
They are exclusive for the selected candidate in each golden row.

| `match_label` | Documents | Meaning |
|---|---:|---|
| `exact_match` | {{count_0}} | The golden text and rendered crawl-res text have the same normalized sequence of words and numbers. This permits differences in markup, punctuation, case and whitespace; it does not mean byte-for-byte equality. |
| `same_page` | {{count_1}} | The records share a recovered normalized source URL, a Wikipedia page ID resolved through title/redirect metadata, or a Belem numeric node/print page ID. Text may differ substantially between page versions or extractions. |
| `near_match` | {{count_2}} | Literal character/word evidence suggests related content, a partial copy, changed word boundaries, or reordered passages, without establishing exact equality or a same-page link. These remain candidates. |
| `weak_match` | {{count_3}} | A retrieved candidate has weaker lexical overlap or only a broader URL association. A URL can occur inside an embed response rather than identify the document itself. This category does not confirm document identity. |
| `not_found` | {{count_4}} | No candidate was retained by the searches used here. The crawl-res text, URL and ID are null. This does not establish that the document is absent from every version of crawl-res. |

## Matching policy

1. **Recover FineWeb sources.** Start with the labeled golden IDs and their
   original plain texts. Use upstream FineWeb-C metadata and normalized-text
   searches of the pinned FineWeb-2 Tatar retained train/test and removed train
   partitions to recover native source IDs, URLs and record locators. Golden,
   FineWeb and crawl-res IDs are distinct identifier systems; an ID equality join
   is not assumed.
2. **Search crawl-res.** Search all **4,265,586 records in 50 pinned parquet
   shards**, using bounded streaming batches. The initial pass uses normalized
   source URLs, normalized text hashes and literal passage anchors. The focused
   follow-up searches the 171 golden IDs without an initial crawl-res candidate.
3. **Broaden retrieval without semantic similarity.** The focused search uses
   URL variants (including tracking parameters, wrapped URLs, Wikipedia title
   encodings/mobile URLs and Drupal node URLs), current Wikipedia title redirects
   and page IDs, compact character passages, and rare literal words. A separate
   URL-column pass checks Belem `/node/ID`, `/print/ID` and `/printpdf/ID`
   identities. These broader aliases retrieve candidates; they do not themselves
   establish text equality.
4. **Compare full text.** Render Markdown to visible text, HTML-unescape,
   normalize Unicode with NFKC, case-fold, and compare word/number sequences.
   Additional lexical metrics use character edit similarity, compact text with
   word boundaries removed, word-multiset overlap, containment, reordered
   passages and partial string matching. Original full texts remain unchanged in
   the exported text columns. **No embeddings, semantic similarity or LLM
   judgments are used for matching.**
5. **Select one candidate deterministically.** Prefer exact text, then same-page
   links, then near/partial/reordered candidates, then weak/URL-only evidence.
   Within a category, choose the largest character/compact similarity, then word
   Dice overlap, then source locator. Alternative candidates remain in the local analysis artifacts. The published
   dataset contains only the selected candidate per golden ID; retrieval is
   bounded and does not enumerate every possible pair.

The focused lexical search uses 32-character compact anchors at stride 16,
discarding anchors shared by more than three target references. Rare-word
retrieval uses up to 16 words per reference, at least eight characters long and
shared by at most two targets. Two distinct anchors or two rare-word hits can
retrieve a candidate; URL/page-ID evidence can retrieve it independently.
Near-text checks use character or compact similarity of at least 0.85 and word
Dice overlap of at least 0.75. Focused reordered checks use word Dice of at least
0.95 and reference-anchor coverage of at least 0.50. Partial checks use partial
similarity of at least 0.95, reference-word coverage of at least 0.75 and anchor
coverage of at least 0.25. The partial metric is skipped when either normalized
text exceeds 150,000 characters; other full-text checks still apply. These are
retrieval/review heuristics, not calibrated probabilities of a correct match.

## Educational labels and transfer policy

Original classes are `None`, `Minimal`, `Basic`, `Good`, `Excellent`, and
`Problematic Content`. The decorative warning symbols in original problematic
labels are removed in clean fields and preserved in raw-label lists. The string
`"None"` is an educational class; JSON `null` means an unavailable value.

Human label lists and annotator IDs are preserved. A single human label is
provided only when all recorded labels agree after normalization; otherwise it
is null. Disagreement rows are retained. Model labels are joined by golden ID,
with exact checks of the annotated text and source-file fingerprints.

**Existing human, Qwen and Muse labels are transferred to every available
crawl-res candidate, regardless of match type.** They were originally assigned
to the golden FineWeb text; the mapped Markdown is not annotated again.
`labels_transferred_to_crawl_res` and `label_transfer_allowed` are true whenever
candidate text is available. `exact_text_match`, match categories and
`review_required` remain descriptive evidence and do not block this requested
transfer. Unmatched rows retain the original golden labels and have no crawl-res
text. A transferred label therefore does not independently validate the content
of a changed or weakly matched page.

Both previous label merges are included:

| Merge | Groups |
|---|---|
| Three classes | `None–Minimal`; `Basic–Good–Excellent`; `Problematic Content` |
| Four classes | `None`; `Minimal–Basic`; `Good–Excellent`; `Problematic Content` |

Each merge is applied separately to human and model labels. Human consensus can
become available after merging even when original classes disagree. Model/human
agreement flags are null when no human consensus exists at the relevant level.

<!-- BEGIN LABEL REPRESENTATION -->

{{label_representation_stats}}

<!-- END LABEL REPRESENTATION -->

## Files and columns

- `golden.parquet`: the main dataset, with one row per golden document.
- `README.md`: dataset description, matching policy, label legend and statistics.

The Hugging Face viewer uses the `golden` configuration and `golden` split.
Supplementary candidate tables, duplicate JSONL exports and analysis files
are kept locally and are not part of this published repository.

| Columns | Contents |
|---|---|
| `reference_id` | Labeled golden-subset ID. |
| `fineweb_text` | Full original annotated plain text. |
| `fineweb_urls`, `upstream_fineweb_url` | Recovered source URLs, where available. |
| `upstream_fineweb_id`, `fineweb_source_matches` | Native FineWeb IDs and exact normalized source-text matches with record locators. An empty source-match list means no such native match was recovered. |
| `crawl_res_id`, `crawl_res_url`, `crawl_res_locator` | Selected crawl-res record ID, URL and parquet row locator; null when unmatched. |
| `crawl_res_text` | Full original crawl-res Markdown; null when unmatched. |
| `match_label`, `match_method`, similarity fields | Alignment category and lexical evidence. Scores are not semantic similarity or confidence probabilities. |
| `candidate_count` | Number of available distinct candidate records for the golden ID. |
| `human_educational_value`, `qwen_educational_value`, `muse_educational_value` | Original-class consensus or saved model prediction. |
| Label-list, raw-label and merged-class fields | Original annotations and both class merges. |
| `qwen_model`, `muse_model`, agreement fields | Model provenance and agreement with human labels. |
| `labels_apply_to`, transfer/exactness/review flags | Applied label-transfer policy and descriptive alignment evidence. |

Neither text column is truncated by this export. A source record may itself
contain only a title, navigation fragment or incomplete extraction; “full” means
the complete text stored in that source record, not a reconstructed web page.

The golden references have already informed prompt/model selection. This is an
alignment and development resource; the `golden` split name does not imply an
independent, untouched classifier test set. No new annotation sample is selected.

Rebuild locally with `uv run python mapping/build_golden_dataset.py` in the
project repository. Model runs and output directory can be overridden with
command-line options.
