"""Print a small streaming preview of the educational-value source datasets."""

import argparse
import json
import sys
from typing import Any


DATASETS = {
    "crawl-res": "yasalma/crawl-res",
    "tt-structured-content": "yasalma/tt-structured-content",
}


def nonnegative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return number


def truncate(value: Any, max_chars: int) -> Any:
    """Shorten strings for display, including strings in nested metadata."""
    if isinstance(value, str) and max_chars and len(value) > max_chars:
        return value[:max_chars] + f"… [{len(value) - max_chars} more characters]"
    if isinstance(value, dict):
        return {key: truncate(item, max_chars) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [truncate(item, max_chars) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["all", *DATASETS], default="all")
    parser.add_argument("--num-examples", type=nonnegative_int, default=3)
    parser.add_argument("--split", default="train")
    parser.add_argument("--config", help="Optional dataset configuration; use with one dataset.")
    parser.add_argument("--max-chars", type=nonnegative_int, default=1500,
                        help="Maximum characters per string; 0 prints full strings.")
    args = parser.parse_args()
    if args.config and args.dataset == "all":
        parser.error("--config requires selecting a single --dataset")
    if args.num_examples == 0:
        return 0

    try:
        from datasets import load_dataset
    except ImportError:
        print("Install dependencies first: uv sync", file=sys.stderr)
        return 1

    selected = DATASETS if args.dataset == "all" else {args.dataset: DATASETS[args.dataset]}
    failed = False
    for repo_id in selected.values():
        print(f"\n=== {repo_id} | split={args.split} ===", flush=True)
        try:
            # token=None uses HF_TOKEN or a saved Hugging Face login if available.
            # Never fall back to a full download when streaming fails.
            dataset = load_dataset(repo_id, name=args.config, split=args.split,
                                   streaming=True, token=None)
            count = 0
            for count, example in enumerate(dataset.take(args.num_examples), start=1):
                print(f"\nExample {count}")
                print(json.dumps(truncate(example, args.max_chars),
                                 ensure_ascii=False, indent=2, default=str), flush=True)
            if count == 0:
                print("No examples in this split.")
        except Exception as exc:
            failed = True
            print(f"Could not stream {repo_id}: {type(exc).__name__}: {exc}\n"
                  "For gated/private datasets, ensure your account has access and run `hf auth login` "
                  "or set HF_TOKEN. Also check the split and configuration names.", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
