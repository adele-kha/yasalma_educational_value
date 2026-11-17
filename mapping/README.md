# FineWeb/plain → crawl-res/Markdown mapping

Identify and pin inputs, recover reference provenance, match the web corpus,
audit candidates, and exclude reference overlaps. Annotation-set selection is
deferred until a specific sampling policy is agreed. No LLM inference or
classifier training is performed.

Completed run: [coverage report](reports/report.md),
[audit and interpretation](reports/audit.md), and
[independent validation](reports/validation.json).

## Run with uv

```bash
uv sync
uv run --env-file .env python mapping/pipeline.py all
```

Individual resumable stages:

```bash
uv run --env-file .env python mapping/pipeline.py discover
uv run --env-file .env python mapping/pipeline.py index
uv run --env-file .env python mapping/pipeline.py scan
uv run python mapping/pipeline.py finalize
uv run python mapping/audit.py
uv run python -m unittest discover -s mapping -p 'test_*.py'
```

Edit `policy.json` before starting a new run. Its dataset commits, reference-file
SHA-256, thresholds, seed, and sample size are pinned in `data/manifest.json`.
Changing policy requires separate checkpoints; the pipeline refuses to combine
different policies. A failed download can be retried by repeating the same stage.
FineWeb rows and individual crawl files are checkpointed by physical row number.

The scan uses range-based Parquet reads and bounded Arrow batches. SQLite keeps
the FineWeb lookup on disk with compressed original records. Four independent
processes scan crawl shards by default. Complete source corpora are not loaded
into RAM. Checkpoints, raw texts and generated datasets are ignored by Git; allow
several GB of local disk space, and keep credentials in the ignored `.env`.

## Inputs and provenance

- Local human reference: `annotation/data/tat_Cyrl-train.parquet`, 1,557 rows.
- Source metadata: pinned `data-is-better-together/fineweb-c/with_metadata`.
  The existing local IDs, texts, human labels, and annotator IDs are independently
  checked against that export before reusing its source links.
- Full FineWeb search: pinned `HuggingFaceFW/fineweb-2`, `tat_Cyrl` train/test and
  `tat_Cyrl_removed` train. Removed rows are necessary to preserve low-quality
  examples; upstream removal does not itself become an educational label.
- Markdown corpus: pinned `yasalma/crawl-res`, all Parquet files.

Historical sample provenance and later full-corpus membership are distinct.
The upstream metadata's dataset, revision, file and physical row are retained;
known changes in full-corpus text are not silently assigned historical human
labels. Discovery counts are in [reports/discovery.json](reports/discovery.json).

## Match and exclusion rules

URL normalization lowercases hosts, normalizes default ports and percent-escape
presentation, discards fragments and treats HTTP/HTTPS as candidate aliases.
It preserves path case, reserved path escapes, and query order/values. It does
not remove query parameters or assume that URLs identify unchanged content.

Training acceptance requires equality of the normalized visible word/number
sequence. Markdown is parsed with CommonMark plus tables/strikethrough, then HTML
visible text is extracted. Unicode presentation, casing, punctuation, entities,
and whitespace are normalized. This is strong textual evidence, not a claim
that images or punctuation-dependent semantics have been reviewed. Original
plain and Markdown texts remain unchanged in the exported records.

Same-URL near matches are saved for review and never automatically accepted.
In the initial candidate audit, a zero similarity is a thresholded retrieval
sentinel (or a failed length check), not a measured claim of zero textual
similarity. The rejected review pack adds an uncensored measured score for its
selected snapshot; it does not claim to identify the best of every rejected URL's
versions.
When several FineWeb snapshots have the same normalized content, a deterministic
representative and the number of equivalent records are recorded.

Leakage guards cover all recovered reference URLs, canonical reference text,
historical and later source variants, and anchor-retrieved near duplicates.
The full FineWeb test partition is additionally reserved by default. A cheap
Markdown normalizer screens every crawl record; matched-URL candidates also
receive the full Markdown parser check. Near-duplicate screening is approximate:
it cannot prove the absence of every transformed or partial copy. Unresolved
reference URLs do not disappear from text-based leakage screening.

After every shard is scanned, a global quarantine also removes candidates
sharing an excluded record's ID, normalized URL, or exact canonical text hash.
This propagates through connected candidate records, independent of scan order.
The separate audit checks the full exact-pair inventory against exclusion IDs,
URLs and content hashes, verifies its source locators, and re-renders diagnostic
examples against their stored original texts.

## Outputs

- `data/reference_mapping.parquet`: reference IDs → historical/current source
  locators, URL recovery evidence, and additional full-corpus candidates.
- `data/reference_pairs.parquet`: reference plain text and candidate Markdown,
  original human labels, and explicit content-equivalence/label-transfer flags.
  False flags prohibit automatic transfer of the human label.
- `data/exclusions.parquet`: crawl record locators/IDs and exclusion reasons.
- `data/eligible_pairs.parquet`: the full metadata inventory of 117,561 distinct
  canonical-text groups passing the current exact matching and quarantine rules.
  This is **not an annotation sample**. It contains source locators and hashes;
  original full texts remain accessible in the SQLite checkpoints. All 118,012
  exact pair rows, including duplicate text groups, remain in the shard databases.
- `data/pair_audit.parquet`: bounded examples of near matches and content mismatches;
  full status totals are reported separately.
- `reports/summary.json` and `reports/report.md`: aggregate coverage, exclusions,
  source/length distributions, and limitations.
- `reports/validation.json`: inventory integrity checks, reference recovery,
  artifact hashes, and implementation/dependency fingerprints.
- `data/accepted_review_pack.jsonl` and `data/rejected_review_pack.jsonl`:
  diagnostic examples for mapping review only, not training/annotation selections.

No annotation sample is generated by any stage. The previous 10k export and its
80/20 selection policy have been removed. We can apply the future sampling policy
to these inventories without repeating the full corpus scan. Near-duplicate
handling between candidate documents is also left for that policy.

The exact intersection is not representative of every crawl-res source. Inspect
coverage before planning annotation. The existing human reference has already
informed prompt/model selection, so it is a development benchmark; a fresh human
test set is still needed for final classifier evaluation.

## Focused search for the 171 remaining golden documents

`search_remaining.py` searches only golden IDs absent from the baseline
`reference_pairs.parquet`. It streams the pinned full crawl, with resumable
per-shard checkpoints and thresholds in `golden_search_policy.json`:

```sh
uv run --env-file .env python mapping/wiki_identity.py
uv run --env-file .env python mapping/search_remaining.py scan
uv run python mapping/search_remaining.py report
```

The Wikipedia step records live title normalization, redirects and page IDs.
Run it before starting the crawl search: its response is frozen in the search
manifest along with baseline input hashes, code hashes and policy. Do not refresh
it midway through a resumed search. Use `--output-dir` for a separate search if
inputs or thresholds change.

Retrieval uses URL aliases, Wikipedia page IDs, compact character passages and
rare literal words. Candidates are checked with the full Markdown renderer,
character edit similarity, word multiset overlap, containment and partial string
matching. No embeddings, LLM judgments or semantic similarity are used. URL
aliases and page IDs identify possible source pages; changed revisions still
need content review.

Results are in `data/golden_remaining_v2/`: `status.parquet` covers every target;
`candidates.parquet` retains up to eight candidates per target, full texts,
original human labels, crawl locators and evidence. `summary.json` and
`reports/golden_remaining/report.md` describe coverage and limitations. A strong
candidate is a review priority, not confirmation that the human label applies.
Only exact normalized visible-word equality permits automatic label transfer.
Baseline mappings remain unchanged and no annotation sample is generated.

An additional URL-column pass checks Belem's numeric `/node/ID`, `/print/ID`
and `/printpdf/ID` variants, including pages below the lexical retrieval thresholds:

```sh
uv run --env-file .env python mapping/search_print_urls.py
```

It saves `print_url_candidates.parquet` and `print_url_summary.json` beside the
focused results. These are page-identity candidates; only the explicit exact
visible-text flag permits label transfer. Per-file JSON checkpoints support
restarts; use a separate search directory when changing inputs.

After both passes finish, validate their coverage and build the combined
per-reference review:

```sh
uv run python mapping/review_remaining.py
```

The combined report and JSON under `reports/golden_remaining/` distinguish exact
text, compact text, page identity, strong lexical candidates, near/partial/
reordered candidates, URL-only evidence, weak overlap and references without a
candidate. These are exclusive review categories, not newly accepted mappings.

## Golden dataset with human, Qwen and Muse labels

Run `uv run python mapping/build_golden_dataset.py` to join the complete 1,557-row
golden set to the baseline and focused crawl-res candidates. The default complete
human-inspired runs are Qwen3.8-27B and Muse Spark Open. The join checks IDs,
original annotated texts, and source-file fingerprints. Override model run paths
with `--qwen-run` and `--muse-run`.

The root `golden_crawlres_fineweb/` directory contains `golden.parquet` and
`golden.jsonl` (one best candidate per golden ID, retaining unmatched IDs),
`candidates.parquet` (all available candidate pairs), `manifest.json` and a data
README. Each main row includes the original plain text, candidate Markdown,
source URLs/locators, one of the requested five match labels, human/model labels,
both previous class merges and agreement flags. Human disagreements remain in
the lists, with a null original-class consensus. Per the requested export policy,
existing human, Qwen and Muse labels are transferred to every available Markdown
candidate regardless of match type, without new inference. Exactness and review
flags remain descriptive and do not gate transfer in this export. Earlier mapping
artifacts retain their original stricter flags. Alternative candidate selection
is recorded in the manifest.
