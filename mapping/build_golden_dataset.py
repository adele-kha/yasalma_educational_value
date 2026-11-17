"""Export all golden IDs with crawl candidates, match categories and saved labels."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from rapidfuzz.fuzz import ratio

from pipeline import BASE, ROOT, read_json, write_json
from search_print_urls import identity as print_identity
from text_utils import canonical, url_key, visible_markdown
from label_representation import write_statistics

MATCH_LABELS = ['exact_match', 'same_page',
    'near_match',
    'weak_match', 'not_found']
GROUPS = {
    'three_classes': {'None':'None–Minimal', 'Minimal':'None–Minimal',
        'Basic':'Basic–Good–Excellent', 'Good':'Basic–Good–Excellent',
        'Excellent':'Basic–Good–Excellent', 'Problematic Content':'Problematic Content'},
    'four_classes': {'None':'None', 'Minimal':'Minimal–Basic', 'Basic':'Minimal–Basic',
        'Good':'Good–Excellent', 'Excellent':'Good–Excellent', 'Problematic Content':'Problematic Content'},
}


def normalize_label(label):
    label = label.replace('❗', '').strip()
    if label not in GROUPS['four_classes']: raise ValueError(f'Unknown label: {label}')
    return label


def consensus(labels, mapping=None):
    labels = [normalize_label(label) for label in labels]
    values = {mapping[label] if mapping else label for label in labels}
    return next(iter(values)) if len(values) == 1 else None


def label_fields(prefix, raw):
    return {f'{prefix}_educational_value': consensus(raw),
        f'{prefix}_educational_value_labels': [normalize_label(label) for label in raw],
        f'{prefix}_educational_value_raw_labels': raw,
        **{f'{prefix}_educational_value_{name}': consensus(raw, mapping) for name,mapping in GROUPS.items()}}


def match_evidence(reference, candidate, known_urls, policy):
    normal = canonical(reference['text'])
    visible = visible_markdown(candidate['text_markdown'])
    compact_normal, compact_visible = normal.replace(' ', ''), visible.replace(' ', '')
    chars = ratio(normal, visible)/100
    compact = ratio(compact_normal, compact_visible)/100
    ref_words, doc_words = Counter(normal.split()), Counter(visible.split())
    shared = sum((ref_words & doc_words).values())
    dice = 2*shared/max(1,sum(ref_words.values())+sum(doc_words.values()))
    exact = bool(normal) and normal == visible
    key = url_key(candidate.get('url'))
    same_url = bool(key) and key in {url_key(url) for url in known_urls if url}
    node = print_identity(candidate.get('url'))
    same_print = bool(node) and node in {print_identity(url) for url in known_urls}
    wiki = candidate.get('wikipedia_page_id_match', False)
    contained = bool(compact_normal) and compact_normal in compact_visible
    tier = candidate.get('tier')
    if exact:
        label, method = MATCH_LABELS[0], 'exact_normalized_visible_words'
    elif same_url or same_print or wiki:
        label = MATCH_LABELS[1]
        method = 'wikipedia_page_id' if wiki else 'belem_node_print_id' if same_print and not same_url else 'normalized_source_url'
    elif (tier in {'exact_compact','reference_contained','high_lexical','near_lexical_review',
                  'reordered_lexical_review','partial_lexical_review'}
          or contained or (max(chars,compact)>=policy['near_character_similarity'] and dice>=policy['near_token_dice'])):
        label, method = MATCH_LABELS[2], tier or ('reference_contained' if contained else 'near_lexical_review')
    else:
        label, method = MATCH_LABELS[3], tier or 'weak_lexical_or_url_evidence'
    return dict(match_label=label, match_method=method, character_similarity=chars,
        compact_similarity=compact, token_dice=dice,
        reference_token_coverage=shared/max(1,sum(ref_words.values())),
        document_token_coverage=shared/max(1,sum(doc_words.values())),
        exact_text_match=exact, label_transfer_allowed=True, review_required=not exact)


def load_model(path, references):
    rows = pq.read_table(path).to_pylist()
    if len({row['id'] for row in rows}) != len(rows): raise ValueError(f'Duplicate model IDs: {path}')
    result = {row['id']:row for row in rows}
    if set(result) != set(references): raise ValueError(f'Model IDs do not cover golden set: {path}')
    for key,row in result.items():
        if row['text'] != references[key]['text']: raise ValueError(f'Model annotated different text: {path}, {key}')
        if len(row['educational_value_labels']) != 1: raise ValueError(f'Expected one model label: {key}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'golden_crawlres_fineweb')
    parser.add_argument('--qwen-run', type=Path, default=ROOT/'annotation/evaluation/runs/qwen38-27b-human-inspired')
    parser.add_argument('--muse-run', type=Path, default=ROOT/'annotation/evaluation/runs/muse-spark-open-human-inspired')
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    args.qwen_run = args.qwen_run.resolve()
    args.muse_run = args.muse_run.resolve()
    refs = {row['id']:row for row in pq.read_table(ROOT/'annotation/data/tat_Cyrl-train.parquet').to_pylist()}
    metadata = {row['id']:row for row in pq.read_table(BASE/'data/reference_metadata.parquet').to_pylist()}
    qwen, muse = (load_model(run/'llm_annotations.parquet',refs) for run in [args.qwen_run,args.muse_run])
    qwen_manifest, muse_manifest = (read_json(run/'manifest.json') for run in [args.qwen_run,args.muse_run])
    if qwen_manifest['source_sha256'] != muse_manifest['source_sha256']: raise ValueError('Models used different source datasets')
    if hashlib.sha256((ROOT/'annotation/data/tat_Cyrl-train.parquet').read_bytes()).hexdigest() != qwen_manifest['source_sha256']:
        raise ValueError('Model source fingerprint differs from golden data')
    known_urls = defaultdict(set)
    fw_matches = defaultdict(list)
    for key,row in metadata.items():
        for field in ['source_url','fineweb2_url']:
            if row.get(field): known_urls[key].add(row[field])
    for row in pq.read_table(BASE/'data/reference_candidate_audit.parquet').to_pylist():
        if row['original_annotation_canonical_exact']:
            known_urls[row['reference_id']].add(row['url'])
            fw_matches[row['reference_id']].append(dict(id=row['fineweb_id'],url=row['url'],
                locator=row['fineweb_key'],raw_text_exact=row['original_annotation_raw_exact']))
    focused = BASE/'data/golden_remaining_v2'
    sources = [BASE/'data/reference_pairs.parquet',focused/'candidates.parquet',focused/'print_url_candidates.parquet']
    candidates = defaultdict(dict)
    policy = read_json(BASE/'golden_search_policy.json')
    for path in sources:
        for row in pq.read_table(path).to_pylist():
            key = row['reference_id'];ref = refs[key]
            if row['reference_text'] != ref['text'] or row['human_labels'] != ref['educational_value_labels']:
                raise ValueError(f'Candidate reference text/labels differ: {key}')
            locator = row.get('crawl_key',row.get('crawl_locator'))
            candidate = dict(reference_id=key,crawl_key=locator,crawl_res_id=row['crawl_res_id'],
                url=row['url'],text_markdown=row['text_markdown'],source=row.get('source'),
                **match_evidence(ref,row,known_urls[key],policy))
            previous = candidates[key].get(locator)
            if previous is None or MATCH_LABELS.index(candidate['match_label']) < MATCH_LABELS.index(previous['match_label']):
                candidates[key][locator] = candidate
    output = []; all_candidates = []
    for key,ref in sorted(refs.items()):
        options = sorted(candidates[key].values(), key=lambda row:(MATCH_LABELS.index(row['match_label']),
            -max(row['character_similarity'],row['compact_similarity']),-row['token_dice'],row['crawl_key']))
        chosen = options[0] if options else None
        for candidate in options:
            all_candidates.append(dict(**candidate,selected=candidate is chosen,
                **label_fields('human',ref['educational_value_labels']),
                **label_fields('qwen',qwen[key]['educational_value_labels']),
                **label_fields('muse',muse[key]['educational_value_labels']),
                labels_transferred_to_crawl_res=True))
        row = dict(reference_id=key,fineweb_text=ref['text'],fineweb_urls=sorted(url for url in known_urls[key] if url),
            fineweb_source_matches=sorted(fw_matches[key],key=lambda match:(not match['raw_text_exact'],match['locator'])),
            upstream_fineweb_id=metadata[key].get('source_id'),upstream_fineweb_url=metadata[key].get('source_url'),
            crawl_res_id=chosen['crawl_res_id'] if chosen else None,
            crawl_res_url=chosen['url'] if chosen else None,
            crawl_res_text=chosen['text_markdown'] if chosen else None,
            crawl_res_locator=chosen['crawl_key'] if chosen else None,
            match_label=chosen['match_label'] if chosen else MATCH_LABELS[4],
            match_method=chosen['match_method'] if chosen else None,
            character_similarity=chosen['character_similarity'] if chosen else None,
            compact_similarity=chosen['compact_similarity'] if chosen else None,
            token_dice=chosen['token_dice'] if chosen else None,
            candidate_count=len(options),label_transfer_allowed=bool(chosen and chosen['label_transfer_allowed']),
            exact_text_match=bool(chosen and chosen['exact_text_match']),
            labels_transferred_to_crawl_res=chosen is not None,
            review_required=bool(chosen and chosen['review_required']),
            labels_apply_to='fineweb_text and crawl_res_text' if chosen else 'fineweb_text',
            **label_fields('human',ref['educational_value_labels']),
            human_annotator_ids=ref['annotator_ids'],
            **label_fields('qwen',qwen[key]['educational_value_labels']),qwen_model=qwen_manifest['model'],
            **label_fields('muse',muse[key]['educational_value_labels']),muse_model=muse_manifest['model'])
        for prefix in ['qwen','muse']:
            for suffix in ['', '_three_classes', '_four_classes']:
                human = row['human_educational_value'+suffix]
                row[f'{prefix}_matches_human'+suffix] = row[prefix+'_educational_value'+suffix] == human if human is not None else None
        output.append(row)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    pq.write_table(pa.Table.from_pylist(output),args.output_dir/'golden.parquet',compression='zstd')
    pq.write_table(pa.Table.from_pylist(all_candidates),args.output_dir/'candidates.parquet',compression='zstd')
    with (args.output_dir/'golden.jsonl').open('w') as handle:
        for row in output: handle.write(json.dumps(row,ensure_ascii=False)+'\n')
    summary = dict(rows=len(output),candidate_pairs=len(all_candidates),
        match_labels={label:sum(row['match_label']==label for row in output) for label in MATCH_LABELS},
        human_disagreements=sum(row['human_educational_value'] is None for row in output),
        model_label_coverage={'qwen':len(qwen),'muse':len(muse)},
        qwen_run=str(args.qwen_run),muse_run=str(args.muse_run),
        qwen_manifest=qwen_manifest,muse_manifest=muse_manifest,
        source_datasets={key:dict(repo=value['repo'],revision=value['revision'])
            for key,value in read_json(BASE/'data/manifest.json')['repositories'].items()},
        inputs_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [ROOT/'annotation/data/tat_Cyrl-train.parquet',*sources,
                BASE/'data/reference_metadata.parquet',BASE/'data/reference_candidate_audit.parquet',
                args.qwen_run/'llm_annotations.parquet',args.muse_run/'llm_annotations.parquet']},
        selection='One row per golden ID. Exact text > same page > near/partial/reordered > weak/URL-only. Within category: highest character/compact similarity, then token Dice, then source locator.',
        semantic_similarity_used=False,labels_apply_to='Existing human, Qwen and Muse labels transferred to every available crawl-res candidate, regardless of match type, as requested. No new inference.')
    write_json(args.output_dir/'manifest.json',summary)
    card = (BASE/'golden_dataset_card.md').read_text()
    label_statistics = write_statistics(output,args.output_dir)
    replacements = {'rows': f'{len(output):,}', 'candidate_pairs': f'{len(all_candidates):,}',
        'qwen_model': qwen_manifest['model'], 'muse_model': muse_manifest['model'],
        'label_representation_stats': label_statistics,
        **{f'count_{index}': f'{summary["match_labels"][label]:,}' for index,label in enumerate(MATCH_LABELS)}}
    for name,value in replacements.items():
        card = card.replace('{{' + name + '}}', value)
    (args.output_dir/'README.md').write_text(card)
    print(json.dumps({key:summary[key] for key in ['rows','candidate_pairs','match_labels','human_disagreements','model_label_coverage']},indent=2))


if __name__ == '__main__':
    main()
