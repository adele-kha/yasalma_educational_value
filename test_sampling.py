"""Small synthetic checks; no Hub access required."""

import contextlib
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from sample_dataset import allocate, category_targets, clean_text, run, validate


class SamplingTests(unittest.TestCase):
    def test_near_duplicate_filter(self):
        policy = json.loads(Path(__file__).with_name("sampling_policy.json").read_text())
        policy.update(diversity_count=0, random_count=1, edge_count=0)
        words = [f"token{i}" for i in range(100)]
        records = [dict(id="a", text=" ".join(words)),
                   dict(id="b", text=" ".join(reversed(words))),
                   dict(id="c", text="An unrelated short text.")]
        with tempfile.TemporaryDirectory() as directory:
            policy["output"] = str(Path(directory) / "sample.json")
            with patch.dict(sys.modules, {"datasets": types.SimpleNamespace(load_dataset=lambda *a, **kw: iter(records))}):
                with contextlib.redirect_stdout(io.StringIO()):
                    run(policy, "test-revision")
            report = json.loads(Path(policy["output"]).read_text())["metadata"]
            self.assertEqual(report["scan"]["near_duplicate"], 1)
            self.assertEqual(report["scan"]["eligible"], 2)

    def test_allocation_and_normalization(self):
        self.assertEqual(sum(allocate(17, {"a": 1, "b": 2, "c": 1}).values()), 17)
        self.assertEqual(clean_text("<b>A</b> &amp; B"), "A & B")
        targets = category_targets({"rare": 1, "known": 10}, 5, 5, qualifying=5)
        self.assertEqual(targets.get("known"), 5)
        self.assertEqual(targets.get("rare", 0), 0)

    def test_selection_and_reproducibility(self):
        policy = json.loads(Path(__file__).with_name("sampling_policy.json").read_text())
        policy.update(diversity_count=20, random_count=5, edge_count=5)
        validate(policy)
        records = [dict(id=str(i), text=("word " * (i + 1)) + f"unique{i}\n" + ("repeat\n" * (i % 4)),
                        publish_year=None if i % 5 == 0 else 2000 + i % 6,
                        genre=None if i % 3 == 0 else "history, science") for i in range(80)]
        records += [dict(records[0], id="duplicate"), dict(id="empty", text="  ")]
        with tempfile.TemporaryDirectory() as directory:
            policy["output"] = str(Path(directory) / "sample.json")
            with patch.dict(sys.modules, {"datasets": types.SimpleNamespace(load_dataset=lambda *a, **kw: iter(records))}):
                with contextlib.redirect_stdout(io.StringIO()):
                    run(policy, "test-revision")
                first = Path(policy["output"]).read_bytes()
                with contextlib.redirect_stdout(io.StringIO()):
                    run(policy, "test-revision")
            self.assertEqual(first, Path(policy["output"]).read_bytes())
            result = json.loads(first)
            samples = result["samples"]
            self.assertEqual(len(samples), 30)
            self.assertEqual(len({s["document"]["id"] for s in samples}), 30)
            random_ids = [s["document"]["id"] for s in samples if s["sampling"]["component"] == "random"]
            self.assertEqual(random_ids, [str(i) for i in random.Random(policy["seed"]).sample(range(80), 5)])
            self.assertEqual(result["metadata"]["scan"]["exact_or_id_duplicate"], 1)
            self.assertEqual(result["metadata"]["scan"]["invalid_text"], 1)


if __name__ == "__main__":
    unittest.main()
