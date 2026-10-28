"""Resumable Nebius annotation and human agreement evaluation (no extra dependencies)."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parent
LABELS = ['None', 'Minimal', 'Basic', 'Good', 'Excellent', 'Problematic Content']
PROBLEMATIC = '❗ Problematic Content ❗'


def normalize(label):
    return 'Problematic Content' if label == PROBLEMATIC else label


def parse_response(content):
    match = re.fullmatch(r'\s*Reason:\s*(.+?)\s*\nEducational label:\s*([^\n]+)\s*', content, re.S)
    if not match or match[2].strip() not in LABELS:
        raise ValueError('Response does not match required Reason / Educational label format')
    return match[2].strip(), match[1].strip()


def metrics(pairs, labels=None):
    labels = LABELS if labels is None else labels
    matrix = {a: {b: 0 for b in labels} for a in labels}
    for human, model in pairs:
        matrix[human][model] += 1
    n = len(pairs)
    per_class = {}
    for label in labels:
        tp = matrix[label][label]
        support = sum(matrix[label].values())
        predicted = sum(matrix[h][label] for h in labels)
        fp, fn = predicted-tp, support-tp
        tn = n-tp-fp-fn
        precision = tp/predicted if predicted else 0.0
        recall = tp/support if support else 0.0
        per_class[label] = dict(support=support, predicted=predicted, tp=tp, fp=fp, fn=fn, tn=tn,
                               precision=precision, recall=recall,
                               f1=2*precision*recall/(precision+recall) if precision+recall else 0.0,
                               one_vs_rest_accuracy=(tp+tn)/n if n else None)
    accuracy = sum(matrix[x][x] for x in labels)/n if n else None
    expected = sum(sum(matrix[x].values()) * sum(matrix[y][x] for y in labels) for x in labels)/n**2 if n else None
    return dict(n=n, accuracy=accuracy, micro_precision=accuracy,
                macro_precision=sum(v['precision'] for v in per_class.values())/len(labels),
                macro_recall=sum(v['recall'] for v in per_class.values())/len(labels),
                macro_f1=sum(v['f1'] for v in per_class.values())/len(labels),
                weighted_f1=sum(v['f1']*v['support'] for v in per_class.values())/n if n else None,
                cohens_kappa=(accuracy-expected)/(1-expected) if n and expected != 1 else None,
                per_class=per_class, confusion_matrix=matrix)


def request(base_url, key, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base_url.rstrip('/')+path, data=data,
                                 headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def annotate(row, args, prompt, key):
    started = time.monotonic()
    result = dict(id=row['id'], model=args.model, max_tokens=args.max_tokens, timestamp=datetime.now(timezone.utc).isoformat())
    usage = Counter()
    for attempt in range(args.retries+1):
        try:
            response = request(args.base_url, key, '/chat/completions', dict(
                model=args.model, messages=[{'role':'user', 'content':prompt.replace('{example}', row['text'])}],
                temperature=0, max_tokens=args.max_tokens))
            usage.update({k:v for k,v in response.get('usage', {}).items() if isinstance(v, int)})
            choice = response['choices'][0]
            result.update(raw_response=choice['message'].get('content'), finish_reason=choice.get('finish_reason'),
                          usage=dict(usage), response_model=response.get('model'))
            if choice.get('finish_reason') != 'stop':
                raise ValueError('Incomplete response: '+str(choice.get('finish_reason')))
            label, reason = parse_response(result['raw_response'] or '')
            result.update(status='ok', label=label, reason=reason,
                          validation_warnings=['Reason exceeds 100 words'] if len(reason.split()) > 100 else [],
                          attempts=attempt+1,
                          elapsed_seconds=round(time.monotonic()-started, 3))
            result.pop('error', None)
            return result
        except urllib.error.HTTPError as exc:
            result['error'] = f'HTTP {exc.code}: {exc.read().decode(errors="replace")[:1500]}'
            if exc.code not in (429, 500, 502, 503, 504):
                break
        except Exception as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'
        if attempt < args.retries:
            time.sleep(min(30, 2**attempt))
    return dict(result, status='error', attempts=attempt+1)


def report(table, predictions, output):
    rows = table.to_pylist()
    pairs, annotation_pairs, comparisons, exported = [], [], [], []
    ambiguous = 0
    valid = {key: value for key, value in predictions.items() if value['status']=='ok'}
    for row in rows:
        human = [normalize(x) for x in (row['educational_value_labels'] or []) if x is not None]
        if any(x not in LABELS for x in human):
            raise ValueError('Unknown human label')
        unambiguous = len(set(human)) == 1
        ambiguous += not unambiguous
        pred = valid.get(row['id'])
        if pred is None:
            continue
        label = pred['label']
        if unambiguous:
            pairs.append((human[0], label))
        annotation_pairs.extend((h, label) for h in human)
        comparisons.append(dict(id=row['id'], human_labels=json.dumps(human), llm_label=label,
                                included_in_primary=unambiguous, match=human[0]==label if unambiguous else '',
                                matches_any_human=label in human, reason=pred['reason']))
        exported.append(dict(row, educational_value_labels=[PROBLEMATIC if label=='Problematic Content' else label],
                             annotator_ids=['nebius:'+pred['model']],
                             problematic_content_label_present=label=='Problematic Content',
                             problematic_content_label_agreement=1.0))
    summary = dict(total_documents=len(rows), successfully_labeled=len(exported),
                   complete=len(exported)==len(rows), missing_or_failed=len(rows)-len(exported),
                   reasons_exceeding_100_words=sum(len(p.get('reason', '').split()) > 100 for p in valid.values()),
                   ambiguous_or_missing_human_documents=ambiguous,
                   primary=metrics(pairs), all_human_annotations=metrics(annotation_pairs),
                   usage=dict(sum_usage(predictions)))
    output.mkdir(parents=True, exist_ok=True)
    (output/'metrics.json').write_text(json.dumps(summary, indent=2)+'\n')
    if exported:
        pq.write_table(__import__('pyarrow').Table.from_pylist(exported, schema=table.schema),
                       output/('llm_annotations.parquet' if summary['complete'] else 'llm_annotations.partial.parquet'))
    with (output/'comparisons.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id','human_labels','llm_label','included_in_primary','match','matches_any_human','reason'])
        writer.writeheader()
        writer.writerows(comparisons)
    primary = summary['primary']
    lines = ['# LLM vs human annotation', '',
             f'Coverage: {len(exported)}/{len(rows)} documents. Complete: {summary["complete"]}.',
             f'Reasons exceeding the 100-word instruction: {summary["reasons_exceeding_100_words"]} (valid explicit labels retained).',
             f'Primary comparison: {len(pairs)} documents with one distinct human label. Conflicting or missing human labels are excluded.',
             '', 'Overall metrics:', '']
    for key in ['accuracy','micro_precision','macro_precision','macro_recall','macro_f1','weighted_f1','cohens_kappa']:
        value = primary[key]
        lines.append(f'- {key}: {value:.4f}' if value is not None else f'- {key}: unavailable')
    lines += ['', '| Class | Support | Predicted | Precision | Recall | F1 | One-vs-rest accuracy |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for label, v in primary['per_class'].items():
        accuracy = f'{v["one_vs_rest_accuracy"]:.4f}' if v['one_vs_rest_accuracy'] is not None else 'N/A'
        lines.append(f'| {label} | {v["support"]} | {v["predicted"]} | {v["precision"]:.4f} | {v["recall"]:.4f} | {v["f1"]:.4f} | {accuracy} |')
    lines += ['', 'Confusion matrix (rows: human; columns: LLM):', '',
              '| Human / LLM | '+' | '.join(LABELS)+' |', '|---|'+'---:|'*len(LABELS)]
    lines += ['| '+h+' | '+' | '.join(str(primary['confusion_matrix'][h][p]) for p in LABELS)+' |' for h in LABELS]
    lines += ['', 'Undefined precision/recall/F1 are scored as zero. Macro averages include all six classes. '
              'Micro precision equals accuracy for single-label classification. Class accuracy is one-vs-rest; '
              'recall is accuracy within the human class. The supplementary all_human_annotations metrics '
              'compare each individual human vote, weighting documents with more votes more heavily. '
              'Partial coverage can bias results; failed predictions never count as None. '
              'Agreement measures consistency with these human annotations, not objective correctness.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    return summary


def sum_usage(predictions):
    counts = Counter()
    for pred in predictions.values():
        counts.update({k:v for k,v in (pred.get('usage') or {}).items() if isinstance(v, int)})
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BASE.parent/'data/tat_Cyrl-train.parquet')
    parser.add_argument('--prompt', type=Path, default=BASE/'prompt.txt')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--model')
    parser.add_argument('--base-url', default='https://api.tokenfactory.nebius.com/v1')
    parser.add_argument('--list-models', action='store_true')
    parser.add_argument('--report-only', action='store_true')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--max-tokens', type=int, default=512)
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--retry-max-tokens', type=int, help='Override output budget only for previously failed rows; logged per response and execution')
    args = parser.parse_args()
    key = os.environ.get('NEBIUS_API_KEY')
    if args.list_models:
        if not key:
            parser.error('Set NEBIUS_API_KEY (for example via uv run --env-file .env)')
        print(json.dumps(request(args.base_url, key, '/models'), indent=2))
        return
    if not args.model or not args.output_dir:
        parser.error('--model and --output-dir are required')
    if not args.report_only and not key:
        parser.error('Set NEBIUS_API_KEY (for example via uv run --env-file .env)')
    if args.limit is not None and args.limit <= 0 or args.workers <= 0:
        parser.error('--limit and --workers must be positive')
    table = pq.read_table(args.source)
    if len(set(table['id'].to_pylist())) != len(table):
        parser.error('Source IDs must be unique')
    prompt = args.prompt.read_text()
    if prompt.count('{example}') != 1:
        parser.error('Prompt must contain exactly one {example} placeholder')
    manifest = dict(model=args.model, base_url=args.base_url, temperature=0, max_tokens=args.max_tokens,
                    source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                    prompt_sha256=hashlib.sha256(args.prompt.read_bytes()).hexdigest())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir/'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        parser.error('Run configuration differs from saved manifest; choose a new output directory')
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    checkpoint = args.output_dir/'predictions.jsonl'
    predictions = {}
    if checkpoint.exists():
        for line in checkpoint.read_text().splitlines():
            pred = json.loads(line)
            predictions[pred['id']] = pred
    # A valid explicit label remains scoreable if only the reason word limit failed.
    for pred in predictions.values():
        if pred.get('status') == 'error' and pred.get('finish_reason') == 'stop' and pred.get('raw_response'):
            try:
                label, reason = parse_response(pred['raw_response'])
            except ValueError:
                continue
            pred.update(status='ok', label=label, reason=reason,
                        validation_warnings=['Reason exceeds 100 words'] if len(reason.split()) > 100 else [],
                        recovered_from_reason_validation=True)
            pred.pop('error', None)
            with checkpoint.open('a') as handle:
                handle.write(json.dumps(pred, ensure_ascii=False)+'\n')
    if not args.report_only:
        models = request(args.base_url, key, '/models')
        available = [item['id'] for item in models['data']]
        if args.model not in available:
            parser.error(f'Model unavailable: {args.model}. Use --list-models; no fallback is selected.')
        (args.output_dir/'model_catalog.json').write_text(json.dumps(models, indent=2)+'\n')
        rows = table.to_pylist()
        if args.limit:
            rows = rows[:args.limit]
        pending = [row for row in rows if predictions.get(row['id'], {}).get('status') != 'ok']
        with (args.output_dir/'executions.jsonl').open('a') as execution_log:
            execution_log.write(json.dumps(dict(timestamp=datetime.now(timezone.utc).isoformat(),
                pending=len(pending), workers=args.workers, limit=args.limit,
                max_tokens=args.max_tokens, retry_max_tokens=args.retry_max_tokens))+'\n')
        print(f'{args.model}: {len(pending)} requests pending', flush=True)
        with checkpoint.open('a') as handle, ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for row in pending:
                request_args = copy.copy(args)
                if args.retry_max_tokens and predictions.get(row['id'], {}).get('status') == 'error':
                    request_args.max_tokens = args.retry_max_tokens
                futures.append(executor.submit(annotate, row, request_args, prompt, key))
            for index, future in enumerate(as_completed(futures), 1):
                pred = future.result()
                handle.write(json.dumps(pred, ensure_ascii=False)+'\n')
                handle.flush()
                predictions[pred['id']] = pred
                print(f'{index}/{len(pending)} {pred["status"]} {pred["id"]}', flush=True)
    summary = report(table, predictions, args.output_dir)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('primary','all_human_annotations')}, indent=2))


if __name__ == '__main__':
    main()
