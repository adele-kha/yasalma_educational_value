"""Descriptive educational-label distributions by alignment category; no inference."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

import pyarrow.parquet as pq

LABELS = ['None', 'Minimal', 'Basic', 'Good', 'Excellent', 'Problematic Content']
DISAGREEMENT = 'No single human label (disagreement)'
START = '<!-- BEGIN LABEL REPRESENTATION -->'
END = '<!-- END LABEL REPRESENTATION -->'


def calculate(rows):
    scopes = {'all': rows,
        'exact': [r for r in rows if r['match_label'] == 'exact_match'],
        'non_exact_mapped': [r for r in rows if r['match_label'] not in {'exact_match','not_found'}],
        'unmatched': [r for r in rows if r['match_label'] == 'not_found'],
        'non_exact_or_unmatched': [r for r in rows if r['match_label'] != 'exact_match']}
    for label in dict.fromkeys(r['match_label'] for r in rows):
        scopes['match_label: ' + label] = [r for r in rows if r['match_label'] == label]
    result = []
    for source in ['human', 'qwen', 'muse']:
        for scheme,suffix in [('original',''),('three_classes','_three_classes'),('four_classes','_four_classes')]:
            field = source + '_educational_value' + suffix
            baseline = Counter(r[field] if r[field] is not None else DISAGREEMENT for r in rows)
            for scope,subset in scopes.items():
                counts = Counter(r[field] if r[field] is not None else DISAGREEMENT for r in subset)
                labels = list(dict.fromkeys((LABELS if scheme == 'original' else []) + sorted(baseline)))
                for label in labels:
                    share = counts[label]/len(subset) if subset else None
                    reference = baseline[label]/len(rows) if rows else None
                    result.append(dict(source=source,scheme=scheme,label=label,scope=scope,
                        count=counts[label],total=len(subset),share=share,baseline_share=reference,
                        representation_ratio=share/reference if share is not None and reference else None,
                        percentage_point_difference=100*(share-reference) if share is not None and reference is not None else None))
    return result


def render(stats):
    index = {(r['source'],r['scheme'],r['label'],r['scope']):r for r in stats}
    sizes = {r['scope']:r['total'] for r in stats}
    lines = ['## Educational-label representation by match outcome', '',
        f'This analysis uses all **{sizes["all"]:,} golden rows**, counted once each. '
        f'Groups: **{sizes["exact"]:,} exact**, **{sizes["non_exact_mapped"]:,} non-exact mapped**, '
        f'and **{sizes["unmatched"]:,} unmatched**. Non-exact mapped excludes unmatched rows.', '',
        'Each cell gives the label count and its percentage within that column’s group. '
        'For non-exact and unmatched groups, the final number is the **representation ratio**: '
        'label share in that group divided by its share in the full golden dataset. '
        '**Above 1× means overrepresented; below 1× means underrepresented.** '
        'The comparison baseline is the full golden set, not the much smaller exact-match subset.', '',
        'Human disagreement rows are shown as a separate non-class category, so every group uses its full row count as denominator. '
        'Model tables use the existing labels assigned to the golden text; transferred labels are not additional independent annotations.', '']
    for source,name in [('human','Human'),('qwen','Qwen3.8-27B'),('muse','Muse Spark Open')]:
        lines += [f'### {name}', '',
            '| Educational value | All golden | Exact | Non-exact mapped (ratio) | Unmatched (ratio) |',
            '|---|---:|---:|---:|---:|']
        labels = LABELS + ([DISAGREEMENT] if (source,'original',DISAGREEMENT,'all') in index else [])
        for label in labels:
            cells = []
            for scope in ['all','exact','non_exact_mapped','unmatched']:
                r = index[source,'original',label,scope]
                percentage = f'{100*r["share"]:.1f}%' if r['share'] is not None else 'n/a'
                cell = f'{r["count"]} ({percentage})'
                if scope in ['non_exact_mapped','unmatched']:
                    cell += f'; {r["representation_ratio"]:.2f}×' if r['representation_ratio'] is not None else '; n/a'
                cells.append(cell)
            lines.append('| ' + ' | '.join([label,*cells]) + ' |')
        lines.append('')
    lines += ['These are descriptive distributions, not significance tests or evidence that educational value causes a matching outcome. '
        'Rare classes and the 60-row unmatched group can have large ratios based on only a few documents; inspect the counts alongside ratios.', '',
        'The tables above show original educational classes. Both merged-class label schemes remain available as columns in the main dataset.']
    return '\n'.join(lines)


def write_statistics(rows, output):
    stats = calculate(rows)
    with (output/'label_representation.json').open('w') as handle:
        json.dump(stats,handle,ensure_ascii=False,indent=2)
        handle.write('\n')
    with (output/'label_representation.csv').open('w',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=list(stats[0]))
        writer.writeheader();writer.writerows(stats)
    report = render(stats)
    (output/'label_representation.md').write_text(report+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-dir',type=Path,default=Path(__file__).resolve().parents[1]/'golden_crawlres_fineweb')
    args = parser.parse_args()
    report = write_statistics(pq.read_table(args.dataset_dir/'golden.parquet').to_pylist(),args.dataset_dir)
    path = args.dataset_dir/'README.md'
    card = path.read_text()
    block = START+'\n\n'+report+'\n\n'+END
    if START in card:
        before,remainder = card.split(START,1)
        _,after = remainder.split(END,1)
        card = before+block+after
    else:
        card += '\n'+block+'\n'
    path.write_text(card)
    print(report)


if __name__ == '__main__':
    main()
