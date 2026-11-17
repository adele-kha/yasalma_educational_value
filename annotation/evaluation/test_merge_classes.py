import unittest

from evaluate import metrics
from merge_classes import FOUR_GROUPS, GROUPS, MAPPING, merged_human


class MergedClassesTests(unittest.TestCase):
    def test_four_groups_keep_none_separate(self):
        mapping = {label: group for group, labels in FOUR_GROUPS.items() for label in labels}
        self.assertIsNone(merged_human(['None', 'Minimal'], mapping))
        self.assertEqual(merged_human(['Minimal', 'Basic'], mapping), 'Minimal–Basic')
        self.assertEqual(merged_human(['Good', 'Excellent'], mapping), 'Good–Excellent')
        self.assertEqual(merged_human(['None'], mapping), 'None')
        self.assertEqual(merged_human(['❗ Problematic Content ❗'], mapping), 'Problematic Content')
        pairs = [('None', 'Minimal'), ('Minimal', 'Basic'), ('Good', 'Excellent'),
                 ('Problematic Content', 'Problematic Content')]
        result = metrics([(mapping[h], mapping[p]) for h, p in pairs], list(FOUR_GROUPS))
        self.assertEqual(result['accuracy'], .75)
        self.assertEqual(len(result['confusion_matrix']), 4)

    def test_ambiguity_is_resolved_only_within_group(self):
        self.assertEqual(merged_human(['None', 'Minimal']), 'None–Minimal')
        self.assertEqual(merged_human(['Basic', 'Excellent']), 'Basic–Good–Excellent')
        self.assertEqual(merged_human(['❗ Problematic Content ❗']), 'Problematic Content')
        self.assertIsNone(merged_human(['Minimal', 'Basic']))
        self.assertIsNone(merged_human([]))

    def test_metrics_are_recomputed_after_merging(self):
        original = [('None', 'Minimal'), ('Basic', 'Excellent'), ('Good', 'None'),
                    ('Problematic Content', 'Problematic Content')]
        result = metrics([(MAPPING[h], MAPPING[p]) for h, p in original], list(GROUPS))
        self.assertEqual(metrics(original)['accuracy'], .25)
        self.assertEqual(result['accuracy'], .75)
        self.assertEqual(result['per_class']['Basic–Good–Excellent']['precision'], 1)
        self.assertEqual(result['per_class']['Basic–Good–Excellent']['recall'], .5)
        self.assertAlmostEqual(result['macro_precision'], 5/6)
        self.assertEqual(sum(sum(r.values()) for r in result['confusion_matrix'].values()), 4)


if __name__ == '__main__':
    unittest.main()
