import unittest
from collections import defaultdict

from label_representation import calculate, DISAGREEMENT


class RepresentationTests(unittest.TestCase):
    def fixture(self):
        rows = []
        for match,label in [('exact_match','None'),('same_page','Basic'),
                            ('not_found','Basic'),('not_found',None)]:
            row = {'match_label':match}
            for source in ['human','qwen','muse']:
                for suffix in ['', '_three_classes', '_four_classes']:
                    row[source+'_educational_value'+suffix] = label
            rows.append(row)
        return rows

    def test_denominators_and_representation_ratios(self):
        stats = calculate(self.fixture())
        index = {(r['source'],r['scheme'],r['label'],r['scope']):r for r in stats}
        row = index['human','original','Basic','non_exact_mapped']
        self.assertEqual((row['count'],row['total']),(1,1))
        self.assertEqual(row['baseline_share'],.5)
        self.assertEqual(row['representation_ratio'],2)
        self.assertEqual(row['percentage_point_difference'],50)
        missing = index['human','original',DISAGREEMENT,'unmatched']
        self.assertEqual((missing['count'],missing['total']),(1,2))
        self.assertEqual(missing['representation_ratio'],2)
        none = index['human','original','None','all']
        self.assertEqual(none['count'],1)
        absent = index['human','original','Excellent','unmatched']
        self.assertIsNone(absent['representation_ratio'])

    def test_categories_partition_each_scope(self):
        grouped = defaultdict(list)
        for row in calculate(self.fixture()):
            grouped[row['source'],row['scheme'],row['scope']].append(row)
        for rows in grouped.values():
            self.assertEqual(sum(row['count'] for row in rows),rows[0]['total'])
            self.assertAlmostEqual(sum(row['share'] for row in rows),1)


if __name__ == '__main__':
    unittest.main()
