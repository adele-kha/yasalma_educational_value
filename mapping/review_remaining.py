"""Validate and combine focused lexical and literal page-identity search results."""
import argparse
from collections import Counter, defaultdict
import hashlib
from pathlib import Path

import pyarrow.parquet as pq

from pipeline import BASE, read_json, write_json
from text_utils import canonical, visible_markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search-dir', type=Path, default=BASE/'data/golden_remaining_v2')
    args = parser.parse_args()
    root = args.search_dir
    summary = read_json(root/'summary.json')
    prints = read_json(root/'print_url_summary.json')
    targets = {row['reference_id']: row for row in read_json(root/'targets.json')}
    manifest = read_json(root/'manifest.json')
    for name, expected in manifest['input_sha256'].items():
        assert hashlib.sha256((BASE/'data'/name).read_bytes()).hexdigest() == expected
    for name, expected in manifest['implementation_sha256'].items():
        assert hashlib.sha256((BASE/name).read_bytes()).hexdigest() == expected
    baseline = set(pq.read_table(BASE/'data/reference_pairs.parquet', columns=['reference_id'])['reference_id'].to_pylist())
    refs = {row['id'] for row in pq.read_table(BASE/'data/reference_metadata.parquet', columns=['id']).to_pylist()}
    assert set(targets) == refs - baseline
    assert summary['full_corpus_scan_complete']
    expected_rows = 0
    import sqlite3
    for file in manifest['crawl']['files']:
        connection = sqlite3.connect(root/'shards'/(Path(file['path']).stem+'.sqlite'))
        row = connection.execute('select next_row,complete from checkpoint where id=1').fetchone()
        assert row and row[1] == 1
        expected_rows += row[0]
        connection.close()
    assert expected_rows == summary['crawl_rows_scanned'] == prints['rows_scanned']
    assert prints['shards'] == len(manifest['crawl']['files'])
    candidates = pq.read_table(root/'candidates.parquet').to_pylist() if (root/'candidates.parquet').exists() else []
    supplemental = pq.read_table(root/'print_url_candidates.parquet').to_pylist() if (root/'print_url_candidates.parquet').exists() else []
    groups = defaultdict(list)
    seen = set()
    for candidate in candidates + supplemental:
        ref = candidate['reference_id']
        assert ref in targets
        assert candidate['reference_text'] == targets[ref]['text']
        assert candidate['human_labels'] == targets[ref]['human_labels']
        exact = canonical(candidate['reference_text']) == visible_markdown(candidate['text_markdown'])
        assert candidate['label_transfer_allowed'] == exact
        if 'tier' in candidate:
            assert (ref, candidate['crawl_key']) not in seen
            seen.add((ref, candidate['crawl_key']))
        groups[ref].append(candidate)
    categories = {key: [] for key in ['exact_visible', 'exact_compact_review',
        'page_identity_review', 'high_lexical_or_contained_review',
        'near_reordered_or_partial_review', 'url_alias_only_review', 'weak_only', 'no_candidate']}
    review = []
    for ref, target in sorted(targets.items()):
        rows = groups[ref]
        tiers = {row.get('tier') for row in rows}
        if any(row['label_transfer_allowed'] for row in rows): category = 'exact_visible'
        elif 'exact_compact' in tiers: category = 'exact_compact_review'
        elif any(row.get('wikipedia_page_id_match') or row.get('evidence') == 'Same belem.ru numeric node/print ID' for row in rows): category = 'page_identity_review'
        elif tiers & {'high_lexical', 'reference_contained'}: category = 'high_lexical_or_contained_review'
        elif tiers & {'near_lexical_review', 'reordered_lexical_review', 'partial_lexical_review'}: category = 'near_reordered_or_partial_review'
        elif 'url_alias_content_review' in tiers: category = 'url_alias_only_review'
        elif rows: category = 'weak_only'
        else: category = 'no_candidate'
        categories[category].append(ref)
        for row in rows:
            row['method'] = row.get('tier', 'belem_print_page_identity')
        compact = [{key: row.get(key) for key in ['crawl_key','url','method','character_similarity','compact_similarity','token_dice','reference_token_coverage','wikipedia_page_id_match','label_transfer_allowed']} for row in rows]
        review.append(dict(reference_id=ref, category=category, original_urls=target['original_urls'], candidates=compact))
    assert not (BASE/'data/annotation_pool.parquet').exists()
    report = BASE/'reports/golden_remaining'
    report.mkdir(exist_ok=True)
    results = dict(targets=len(targets), rows_scanned=expected_rows, shards=len(manifest['crawl']['files']),
                   categories={key:len(value) for key,value in categories.items()}, reference_ids=dict(categories),
                   all_candidates_require_review_except_exact_visible=True,
                   input_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['manifest.json','status.parquet','candidates.parquet','print_url_summary.json','print_url_candidates.parquet'] if (root/name).exists()})
    write_json(report/'combined_summary.json', results)
    write_json(report/'review.json', review)
    lines = ['# Combined review of the remaining golden references', '',
             f'All **{expected_rows:,} crawl records in {results["shards"]} shards** were searched. Scope: **{len(targets)}** previously unmatched golden references.', '',
             '| Evidence category (exclusive) | Golden references |', '|---|---:|']
    lines += [f'| {key} | {len(value)} |' for key,value in categories.items()]
    lines += ['', 'Categories prioritize exact visible text, compact text, page identity, strong lexical evidence, near/partial/reordered text, URL-only evidence, weak overlap, then no candidate. A page identity or lexical candidate does not establish label applicability. No semantic similarity was used.', '',
              'Belem print/node IDs and current Wikipedia page IDs identify page versions. Current Wikipedia metadata may describe a later revision. URL-only evidence can also be an embedded link or an oEmbed response rather than the source document.', '',
              'Full texts, original labels and crawl locators are in `data/golden_remaining_v2/candidates.parquet` and `print_url_candidates.parquet`. `review.json` lists evidence for every target. Baseline files and human labels are unchanged; no annotation sample is created.', '',
              '## Per-reference overview', '', '| Reference ID | Evidence category | Original URL |', '|---|---|---|']
    lines += [f'| {row["reference_id"]} | {row["category"]} | {"; ".join(row["original_urls"]).replace("|","%7C")} |' for row in review]
    (report/'combined_report.md').write_text('\n'.join(lines)+'\n')
    print(results['categories'])


if __name__ == '__main__':
    main()
