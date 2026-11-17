"""Find Belem print/node identities by literal URL IDs, without semantic matching."""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from huggingface_hub import HfFileSystem
import pyarrow as pa
import pyarrow.parquet as pq

from pipeline import BASE, read_json, remote_batches, write_json
from text_utils import canonical, visible_markdown
from rapidfuzz.fuzz import ratio


def identity(url):
    if not isinstance(url, str): return None
    parsed = urlsplit(url)
    if (parsed.hostname or '').lower().removeprefix('www.') != 'belem.ru': return None
    match = re.fullmatch(r'/(?:node|print|printpdf)/(\d+)/?', unquote(parsed.path))
    return match[1] if match else None


def scan(task):
    file, output, crawl, targets = task
    destination = Path(output) / (Path(file['path']).stem + '.json')
    if destination.exists(): return read_json(destination)
    wanted = defaultdict(list)
    for target in targets:
        for number in {identity(url) for url in target['original_urls']} - {None}:
            wanted[number].append(target)
    hits = {}
    rows = 0
    for offset, batch in remote_batches(crawl['repo'], crawl['revision'], file['path'], 8192, columns=['id', 'url']):
        for index, row in enumerate(batch.to_pylist()):
            number = identity(row['url'])
            if number in wanted: hits[offset + index] = (row, wanted[number])
        rows += len(batch)
    matches = []
    if hits:
        fs = HfFileSystem()
        with fs.open(f"datasets/{crawl['repo']}@{crawl['revision']}/{file['path']}", 'rb') as handle:
            parquet = pq.ParquetFile(handle)
            offset = 0
            for group in range(parquet.num_row_groups):
                end = offset + parquet.metadata.row_group(group).num_rows
                selected = sorted(index for index in hits if offset <= index < end)
                if selected:
                    table = parquet.read_row_group(group, columns=['id', 'url', 'text', 'source'])
                    for index in selected:
                        document = table.slice(index - offset, 1).to_pylist()[0]
                        visible = visible_markdown(document['text'] or '')
                        for target in hits[index][1]:
                            normal = canonical(target['text'])
                            matches.append(dict(reference_id=target['reference_id'], crawl_file=file['path'],
                                crawl_row=index, crawl_key=file['path'] + ':' + str(index),
                                reference_urls=target['original_urls'], reference_text=target['text'],
                                human_labels=target['human_labels'], text_markdown=document['text'],
                                crawl_res_id=document['id'], url=document['url'], source=document['source'],
                                evidence='Same belem.ru numeric node/print ID',
                                character_similarity=ratio(normal, visible)/100,
                                exact_visible=bool(normal) and normal == visible,
                                label_transfer_allowed=bool(normal) and normal == visible))
                offset = end
    result = dict(path=file['path'], rows=rows, matches=matches)
    write_json(destination, result)
    print(f"URL check {file['path']}: {rows:,} rows, {len(matches)} pairs", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search-dir', type=Path, default=BASE/'data/golden_remaining_v2')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    manifest = read_json(args.search_dir/'manifest.json')
    targets = read_json(args.search_dir/'targets.json')
    output = args.search_dir/'print_urls'
    output.mkdir(exist_ok=True)
    tasks = [(file, str(output), manifest['crawl'], targets) for file in manifest['crawl']['files']]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = [future.result() for future in as_completed([executor.submit(scan, task) for task in tasks])]
    matches = [row for result in results for row in result['matches']]
    if matches:
        matches.sort(key=lambda row: (row['reference_id'], row['crawl_file'], row['crawl_row']))
        pq.write_table(pa.Table.from_pylist(matches), args.search_dir/'print_url_candidates.parquet', compression='zstd')
    summary = dict(rows_scanned=sum(result['rows'] for result in results), shards=len(results),
                   reference_ids=sorted({row['reference_id'] for row in matches}), pairs=len(matches),
                   exact_visible_pairs=sum(row['exact_visible'] for row in matches))
    write_json(args.search_dir/'print_url_summary.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
