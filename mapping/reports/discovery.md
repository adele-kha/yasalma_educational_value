# Input discovery and pinned provenance

Local reference: **1,557 documents**, the complete `tat_Cyrl/train` FineWeb-C split.

The enriched upstream export was checked by local annotation ID, exact annotated text, individual human labels and annotator IDs. It does not replace the reference text with a later source version.

| Recovery / full-corpus membership | Documents |
|---|---:|
| Historical/source metadata recovered | 1,497 |
| Unresolved in upstream recovery | 60 |
| Later full-FineWeb retained | 515 |
| Later full-FineWeb removed | 982 |
| Known later text changes beyond quote normalization | 13 |

The search includes both retained and removed full-corpus rows; upstream filtering is not treated as a human educational label. All reference texts, including unresolved ones, remain in leakage screening.

## Pinned repositories

- reference: `data-is-better-together/fineweb-c` at `913fc6250ca94f032bce31a6e5fa9363ea27ba73`
- fineweb: `HuggingFaceFW/fineweb-2` at `af9c13333eb981300149d5ca60a8e9d659b276b9`
- crawl: `yasalma/crawl-res` at `dc8f0d22c2287e5f8214b26992d87a176aa454a4`

Local reference SHA-256: `0b801f6b86cd468ef49f085257a2cff5329d354c43c6ead38f93a6807e17be14`.

Further mapping and exclusion results are produced only after the complete scan. Discovery alone does not establish reference-to-Markdown content equivalence.
