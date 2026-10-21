"""Stream the corpus to disk, profile it, and select an auditable annotation sample."""

import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import math
from pathlib import Path
import random
import re
import sqlite3
import tempfile


def clean_text(text):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def quantile(values, fraction):
    position = (len(values) - 1) * fraction
    low = int(position)
    return values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (position - low)


def allocate(total, weights):
    """Largest-remainder integer allocation."""
    raw = {key: total * value / sum(weights.values()) for key, value in weights.items()}
    result = {key: math.floor(value) for key, value in raw.items()}
    for key in sorted(raw, key=lambda key: raw[key] - result[key], reverse=True)[:total - sum(result.values())]:
        result[key] += 1
    return result


def category_targets(population, budget, minimum, qualifying=1, cap=None):
    """Cover one per category before further minima, then square-root fill."""
    targets = Counter()
    # Qualifying genres receive their coverage opportunities before rare labels.
    # At qualifying=1 (publication years), every category still participates.
    keys = sorted(population, key=lambda key: (population[key] < qualifying, population[key], key))
    for level in range(max(1, minimum)):
        for key in keys:
            desired = minimum if population[key] >= qualifying else 1
            if population[key] < qualifying and any(
                targets[other] < min(minimum, population[other])
                for other in keys if population[other] >= qualifying
            ):
                continue
            if level < min(population[key], desired) and sum(targets.values()) < budget:
                targets[key] += 1
    while sum(targets.values()) < budget:
        candidates = [key for key in keys if targets[key] < population[key]
                      and (cap is None or targets[key] < cap)]
        if not candidates:
            candidates = [key for key in keys if targets[key] < population[key]]
        if not candidates:
            break
        key = max(candidates, key=lambda key: math.sqrt(population[key]) / (targets[key] + 1))
        targets[key] += 1
    return dict(targets)


def validate(p):
    for key in ("diversity_count", "random_count", "edge_count", "year_minimum",
                "genre_minimum_population", "genre_minimum_sample", "near_duplicate_min_chars",
                "near_duplicate_anchors", "near_duplicate_bucket_limit", "near_duplicate_sketch_size"):
        if not isinstance(p[key], int) or p[key] < 0:
            raise ValueError(f"{key} must be a nonnegative integer")
    for key in ("year_cap_fraction", "missing_genre_floor", "markup_threshold",
                "repetition_threshold", "near_duplicate_similarity"):
        if not 0 < p[key] <= 1:
            raise ValueError(f"{key} must be in (0, 1]")
    for key in ("length_quantiles", "extreme_quantiles"):
        if len(p[key]) != 2 or not 0 <= p[key][0] < p[key][1] <= 1:
            raise ValueError(f"{key} must contain two increasing fractions")
    if len(p["length_weights"]) != 3:
        raise ValueError("length_weights must contain three weights")
    for weights in (p["length_weights"], list(p["edge_weights"].values()), list(p["coverage_weights"].values())):
        if any(value < 0 for value in weights) or sum(weights) <= 0:
            raise ValueError("Weights must be nonnegative with a positive sum")


def run(p, revision):
    from datasets import load_dataset

    rng = random.Random(p["seed"])
    rows = []
    stats = Counter()
    exact = set()
    ids = set()
    # Near-duplicate heuristic: token-set Jaccard, searched through a bottom-hash
    # index. It is approximate and can miss pairs without a shared anchor.
    anchors = defaultdict(list)
    signatures = []
    sketches = []
    with tempfile.TemporaryDirectory(prefix="educational-sampling-") as directory:
        db = sqlite3.connect(str(Path(directory) / "corpus.sqlite"))
        db.execute("CREATE TABLE documents (row_number INTEGER PRIMARY KEY, record TEXT)")
        dataset = load_dataset(p["dataset"], split=p["split"], revision=revision,
                               streaming=True, token=None)
        for source_index, record in enumerate(dataset):
            stats["scanned"] += 1
            text = record.get("text")
            if not isinstance(text, str) or not (clean := clean_text(text)):
                stats["invalid_text"] += 1
                continue
            digest = hashlib.sha256(clean.encode()).hexdigest()
            source_id = str(record["id"]) if record.get("id") is not None else f"row:{source_index}"
            if digest in exact or source_id in ids:
                stats["exact_or_id_duplicate"] += 1
                continue
            exact.add(digest)
            tokens = re.findall(r"\w+", clean.casefold())
            # Stable 64-bit token hashes keep the index compact and seed independent.
            signature = frozenset(int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big")
                                  for token in set(tokens))
            ordered = sorted(signature)
            keys = ordered[:p["near_duplicate_anchors"]] if len(clean) >= p["near_duplicate_min_chars"] else []
            sketch = frozenset(ordered[:p["near_duplicate_sketch_size"]])
            candidates = {index for key in keys for index in anchors[key]}
            threshold = p["near_duplicate_similarity"]
            def near_duplicate(index):
                other = signatures[index]
                if min(len(signature), len(other)) < threshold * max(len(signature), len(other)):
                    return False
                if len(sketch & sketches[index]) < threshold * min(len(sketch), len(sketches[index])):
                    return False
                intersection = len(signature & other)
                return intersection / (len(signature) + len(other) - intersection) >= threshold
            if any(near_duplicate(index) for index in candidates):
                stats["near_duplicate"] += 1
                continue
            ids.add(source_id)
            index = len(rows)
            signatures.append(signature if keys else frozenset())
            sketches.append(sketch)
            for key in keys:
                if len(anchors[key]) < p["near_duplicate_bucket_limit"]:
                    anchors[key].append(index)
            genre = record.get("genre")
            genres = sorted(set(item.strip().casefold() for item in str(genre).split(",") if item.strip())) if genre else []
            year = str(record["publish_year"]) if record.get("publish_year") is not None else "<missing>"
            tag_chars = sum(len(match.group()) for match in re.finditer(r"<[^>]+>", text))
            markup = tag_chars / max(1, len(text))
            # Repeated normalized lines provide a more specific boilerplate signal
            # than vocabulary repetition in long prose.
            lines = [clean_text(line).casefold() for line in text.splitlines() if clean_text(line)]
            repetition = 1 - len(set(lines)) / len(lines) if len(lines) > 1 else 0
            rows.append(dict(index=index, source_index=source_index, id=source_id,
                             year=year, genres=genres, length=len(clean),
                             markup=markup, repetition=repetition, sha256=digest))
            db.execute("INSERT INTO documents VALUES (?, ?)", (index, json.dumps(record, ensure_ascii=False)))
            if stats["scanned"] % 1000 == 0:
                db.commit()
                print(f"Scanned {stats['scanned']:,}; eligible {len(rows):,}", flush=True)
        db.commit()
        print(f"Scan complete: {stats['scanned']:,} rows; {len(rows):,} eligible. Selecting sample.", flush=True)
        del signatures, sketches, anchors
        total = p["diversity_count"] + p["random_count"] + p["edge_count"]
        if len(rows) < total:
            raise ValueError(f"Only {len(rows)} eligible documents for requested {total}")
        lengths = sorted(row["length"] for row in rows)
        boundaries = [quantile(lengths, q) for q in p["length_quantiles"]]
        extremes = [quantile(lengths, q) for q in p["extreme_quantiles"]]
        for row in rows:
            row["length_bin"] = "short" if row["length"] <= boundaries[0] else "medium" if row["length"] <= boundaries[1] else "long"
            row["format"] = "markup_heavy" if row["markup"] >= p["markup_threshold"] else "cleaner_text"
            row["edges"] = [name for name, match in {
                "extremely_short": row["length"] <= extremes[0],
                "extremely_long": row["length"] >= extremes[1],
                "markup_heavy": row["format"] == "markup_heavy",
                "repetitive": row["repetition"] >= p["repetition_threshold"],
                "missing_both": not row["genres"] and row["year"] == "<missing>",
            }.items() if match]

        selected = []
        used = set()

        def choose(row, component, rationale):
            used.add(row["index"])
            selected.append((row, component, rationale))

        # Draw random FIRST: an unconditional simple random sample of the entire
        # eligible corpus. Subsequent components exclude these rows.
        for row in rng.sample(rows, p["random_count"]):
            choose(row, "random", ["simple random sample of eligible deduplicated corpus"])
        edge_targets = allocate(p["edge_count"], p["edge_weights"])
        edge_actual = Counter()
        # Allocate scarce edge groups first to reduce overlap starvation.
        for category in sorted(edge_targets, key=lambda name: sum(name in row["edges"] for row in rows)):
            pool = [row for row in rows if row["index"] not in used and category in row["edges"]]
            for row in rng.sample(pool, min(len(pool), edge_targets[category])):
                choose(row, "edge", [category])
                edge_actual[category] += 1
        remaining = p["edge_count"] - sum(edge_actual.values())
        pool = [row for row in rows if row["index"] not in used and row["edges"]]
        for row in rng.sample(pool, min(remaining, len(pool))):
            category = min(row["edges"], key=lambda name: edge_actual[name])
            choose(row, "edge", [category, "redistributed edge quota"])
            edge_actual[category] += 1
        edge_shortfall = p["edge_count"] - sum(edge_actual.values())
        # If no edge candidates remain, fill explicitly marked fallback slots.
        for row in rng.sample([row for row in rows if row["index"] not in used], edge_shortfall):
            choose(row, "edge", ["fallback: all edge categories exhausted"])

        pool = [row for row in rows if row["index"] not in used]
        budget = p["diversity_count"]
        years = Counter(row["year"] for row in pool)
        genres = Counter(genre for row in pool for genre in row["genres"])
        year_cap = max(1, math.floor(budget * p["year_cap_fraction"]))
        year_targets = category_targets(years, budget, p["year_minimum"], cap=year_cap)
        genre_targets = category_targets(genres, budget, p["genre_minimum_sample"], p["genre_minimum_population"])
        length_targets = allocate(budget, dict(zip(("short", "medium", "long"), p["length_weights"])))
        missing_population = sum(not row["genres"] for row in pool)
        missing_target = min(missing_population, math.ceil(budget * max(p["missing_genre_floor"], missing_population / len(pool)))) if pool else 0
        format_targets = allocate(budget, {"markup_heavy": 1, "cleaner_text": 1})
        counts = {key: Counter() for key in ("year", "genre", "length", "format")}
        missing_count = 0
        weights = p["coverage_weights"]
        rng.shuffle(pool)
        cap_relaxations = 0
        extreme_fallbacks = 0
        for step in range(budget):
            available = [row for row in pool if row["index"] not in used]
            moderate = [row for row in available if extremes[0] < row["length"] < extremes[1]]
            if moderate:
                available = moderate
            else:
                extreme_fallbacks += 1
            capped = [row for row in available if counts["year"][row["year"]] < year_cap]
            if capped:
                available = capped
            else:
                cap_relaxations += 1

            def rewards(row):
                def deficit(target, current):
                    return max(0, target - current) / max(1, target)
                return {
                    "year": deficit(year_targets.get(row["year"], 0), counts["year"][row["year"]]),
                    "genre": sum(deficit(genre_targets.get(g, 0), counts["genre"][g]) for g in row["genres"]) / max(1, len(row["genres"])),
                    "length": deficit(length_targets[row["length_bin"]], counts["length"][row["length_bin"]]),
                    "missing_genre": deficit(missing_target, missing_count) if not row["genres"] else 0,
                    "format": deficit(format_targets[row["format"]], counts["format"][row["format"]]),
                }
            winner = max(available, key=lambda row: sum(weights[key] * value for key, value in rewards(row).items()))
            rationale = [key for key, value in rewards(winner).items() if value > 0]
            choose(winner, "diversity", rationale or ["remaining diversity slot"])
            counts["year"][winner["year"]] += 1
            counts["genre"].update(winner["genres"])
            counts["length"][winner["length_bin"]] += 1
            counts["format"][winner["format"]] += 1
            missing_count += not winner["genres"]
            if (step + 1) % 50 == 0:
                print(f"Selected {step + 1}/{budget} diversity documents", flush=True)

        records = []
        for row, component, rationale in selected:
            record = json.loads(db.execute("SELECT record FROM documents WHERE row_number=?", (row["index"],)).fetchone()[0])
            records.append({"document": record, "sampling": {**row, "component": component, "rationale": rationale}})
        db.close()
        report = {
            "policy": p, "resolved_revision": revision,
            "scan": {**stats, "eligible": len(rows)},
            "length_boundaries": boundaries, "extreme_boundaries": extremes,
            "corpus_years": dict(Counter(row["year"] for row in rows)),
            "corpus_genres": dict(Counter(g for row in rows for g in row["genres"])),
            "targets": {"year": year_targets, "genre": genre_targets, "length": length_targets,
                        "missing_genre": missing_target, "format": format_targets, "edge": edge_targets},
            "achieved_diversity": {**counts, "missing_genre": missing_count},
            "achieved_edges": dict(edge_actual),
            "relaxations": {"year_cap_selections": cap_relaxations, "extreme_diversity_selections": extreme_fallbacks,
                            "edge_fallback_slots": edge_shortfall},
            "limitations": ["Greedy marginal targets are soft and may conflict; compare targets with achieved counts.",
                             "Near-duplicate detection uses approximate token-set Jaccard with bounded bottom-hash anchor buckets and a sketch prefilter; it can miss pairs and ignores word order.",
                             "Repetition is the fraction of repeated normalized nonempty lines.",
                             "Quantile ties can make length bins unequal.",
                             "Random component drawn first to preserve unconditional simple random sampling; edge slots reserved before diversity."],
        }
        output = Path(p["output"])
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps({"metadata": report, "samples": records}, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(output)
        print(json.dumps({"output": str(output), "scan": report["scan"],
                          "components": dict(Counter(item[1] for item in selected)),
                          "relaxations": report["relaxations"]}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=Path(__file__).with_name("sampling_policy.json"))
    parser.add_argument("--output", help="Override policy output path")
    parser.add_argument("--seed", type=int, help="Override policy seed")
    parser.add_argument("--revision", default="main", help="Hub branch/tag/commit; resolved to a commit before scanning")
    args = parser.parse_args()
    p = json.loads(args.policy.read_text(encoding="utf-8"))
    if args.output is not None:
        p["output"] = args.output
    if args.seed is not None:
        p["seed"] = args.seed
    validate(p)
    from huggingface_hub import HfApi
    revision = HfApi().dataset_info(p["dataset"], revision=args.revision).sha
    print(f"Streaming {p['dataset']} at {revision}", flush=True)
    run(p, revision)


if __name__ == "__main__":
    main()
