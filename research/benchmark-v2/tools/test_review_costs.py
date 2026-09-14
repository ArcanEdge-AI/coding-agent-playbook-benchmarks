"""Tests use published aggregate values, not newly executed coding attempts."""
import unittest
from review_costs import compare


def fixture():
    return {"all_18_attempts_per_arm": {
        "previous": {"attempts": 18, "raw_full_passes": 6,
                     "credits": {"total": 724.219695, "root": 675.884733, "helper": 48.334962,
                                 "uncached_input": 154.850615, "cached_input": 411.89568, "output": 157.4734},
                     "credits_by_model": {"gpt-5.6-luna": 95.785105, "gpt-5.6-sol": 232.63276,
                                          "gpt-5.6-terra": 108.03523, "gpt-6-astra": 287.7666}},
        "revised": {"attempts": 18, "raw_full_passes": 4,
                    "credits": {"total": 884.192096, "root": 847.446108, "helper": 36.745988,
                                "uncached_input": 146.62215, "cached_input": 564.397056, "output": 173.17289},
                    "credits_by_model": {"gpt-5.6-luna": 82.623416, "gpt-5.6-sol": 277.2176,
                                         "gpt-5.6-terra": 91.91178, "gpt-6-astra": 432.4393}}}}


class CostReviewTests(unittest.TestCase):
    def test_published_role_deltas(self):
        delta = compare(fixture())["credit_deltas"]
        self.assertEqual(delta["total"], 159.972401)
        self.assertEqual(delta["root"], 171.561375)
        self.assertEqual(delta["helper"], -11.588974)
        self.assertAlmostEqual(delta["root"] + delta["helper"], delta["total"])

    def test_token_categories_reconcile(self):
        delta = compare(fixture())["credit_deltas"]
        self.assertEqual(delta["cached_input"], 152.501376)
        self.assertAlmostEqual(sum(delta[k] for k in ("uncached_input", "cached_input", "output")), delta["total"])

    def test_actual_model_categories_reconcile(self):
        report = compare(fixture())
        self.assertAlmostEqual(sum(report["actual_model_credit_deltas_including_helpers"].values()),
                               report["credit_deltas"]["total"])


if __name__ == "__main__":
    unittest.main()
