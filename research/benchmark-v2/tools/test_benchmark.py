"""Unit tests for offline tools, NOT scored coding-agent attempts."""
import copy
import json
from pathlib import Path
import unittest

from benchmark import readiness_issues, schedule, summarize, validate

PLAN = Path(__file__).resolve().parents[1] / "pilot.json"


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(PLAN.read_text(encoding="utf-8"))

    def records(self):
        return [{"study_id": self.config["study_id"], "task_id": t["id"], "repeat": repeat,
                 "condition": c["id"], "status": "completed", "submitted": True,
                 "functional_pass": True, "quality_pass": True, "root_credits": 10,
                 "helper_credits": 1 if c["helpers"] else 0, "helper_count": int(c["helpers"])}
                for t in self.config["tasks"] for repeat in range(1, self.config["repeats"] + 1)
                for c in self.config["conditions"]]

    def test_draft_valid_but_blocked(self):
        validate(self.config)
        self.assertTrue(readiness_issues(self.config))
        self.assertFalse(schedule(self.config)["launch_authorized_by_tool"])

    def test_schedule_reproducible_and_complete(self):
        first = schedule(self.config)
        self.assertEqual(first, schedule(copy.deepcopy(self.config)))
        self.assertEqual(first["scored_starts"], 24)
        self.assertEqual(len({(p["task_id"], p["repeat"]) for p in first["pairs"]}), 12)

    def test_order_balanced_within_task(self):
        pairs = schedule(self.config)["pairs"]
        for task in self.config["tasks"]:
            self.assertEqual(len({p["condition_order"][0] for p in pairs if p["task_id"] == task["id"]}), 2)

    def test_odd_repeats_balanced_over_tasks(self):
        self.config["repeats"] = 3
        self.config["budget"]["max_scored_starts"] = 36
        pairs = schedule(self.config)["pairs"]
        self.assertEqual(sum(p["condition_order"][0] == "current-with-helpers" for p in pairs), 9)

    def test_hash_changes_with_treatment(self):
        before = schedule(self.config)["plan_sha256"]
        self.config["conditions"][0]["helper_effort"] = "high"
        self.assertNotEqual(before, schedule(self.config)["plan_sha256"])

    def test_duplicate_task_rejected(self):
        self.config["tasks"].append(self.config["tasks"][0])
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_boolean_repeat_rejected(self):
        self.config["repeats"] = True
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_changed_budget_rejected(self):
        self.config["budget"]["max_scored_starts"] = 48
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_confirmation_rejects_development(self):
        self.config["phase"] = "confirmation"
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_confirmation_rejects_tuned_holdout(self):
        self.config["phase"] = "confirmation"
        for t in self.config["tasks"]:
            t.update(split="holdout", used_for_tuning=True)
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_instructions_hold_helpers_fixed(self):
        self.config["comparison"] = "instructions"
        with self.assertRaises(ValueError):
            validate(self.config)

    def test_full_report(self):
        report = summarize(self.config, self.records())
        self.assertEqual(report["matched_pairs"], 12)
        self.assertEqual(report["conditions"]["current-with-helpers"]["credits_per_accepted"], 11)

    def test_failed_attempt_spend_is_included(self):
        rows = self.records()
        rows[0]["functional_pass"] = False
        arm = summarize(self.config, rows)["conditions"]["current-with-helpers"]
        self.assertEqual(arm["known_accepted"], 11)
        self.assertEqual(arm["credits_per_accepted"], 12)

    def test_valid_timeout_still_can_have_accepted_commit(self):
        rows = self.records()
        rows[0]["status"] = "timeout"
        arm = summarize(self.config, rows)["conditions"]["current-with-helpers"]
        self.assertEqual(arm["known_accepted"], 12)
        self.assertEqual(arm["timeouts"], 1)

    def test_empty_submission_cannot_pass(self):
        rows = self.records()
        rows[0]["submitted"] = False
        with self.assertRaises(ValueError):
            summarize(self.config, rows)

    def test_invalid_pair_excluded_but_spend_retained(self):
        rows = self.records()
        rows[0]["status"] = "infrastructure_invalid"
        report = summarize(self.config, rows)
        self.assertEqual(report["matched_pairs"], 11)
        self.assertEqual(report["conditions"]["current-with-helpers"]["all_recorded_known_credit_subtotal"], 132)

    def test_missing_result_does_not_create_a_failure(self):
        report = summarize(self.config, self.records()[1:])
        self.assertEqual(report["missing_starts"], 1)
        self.assertEqual(report["matched_pairs"], 11)

    def test_duplicate_result_rejected(self):
        rows = self.records()
        with self.assertRaises(ValueError):
            summarize(self.config, rows + [rows[0]])

    def test_wrong_study_rejected(self):
        rows = self.records()
        rows[0]["study_id"] = "another-study"
        with self.assertRaises(ValueError):
            summarize(self.config, rows)

    def test_missing_usage_is_not_free(self):
        rows = self.records()
        rows[0]["root_credits"] = None
        arm = summarize(self.config, rows)["conditions"]["current-with-helpers"]
        self.assertFalse(arm["matched_cost_complete"])
        self.assertIsNone(arm["credits_per_accepted"])

    def test_pending_quality_does_not_become_rejection(self):
        rows = self.records()
        rows[0]["quality_pass"] = None
        arm = summarize(self.config, rows)["conditions"]["current-with-helpers"]
        self.assertEqual(arm["acceptance_pending"], 1)
        self.assertIsNone(arm["credits_per_accepted"])

    def test_zero_accepted_has_no_cost_ratio(self):
        rows = self.records()
        for row in rows:
            row["functional_pass"] = False
        for arm in summarize(self.config, rows)["conditions"].values():
            self.assertIsNone(arm["credits_per_accepted"])

    def test_nonfinite_negative_and_boolean_costs_rejected(self):
        for value in (float("nan"), float("inf"), -1, True):
            with self.subTest(value=value):
                rows = self.records()
                rows[0]["root_credits"] = value
                with self.assertRaises(ValueError):
                    summarize(self.config, rows)

    def test_disabled_helper_leak_requires_invalid_status(self):
        rows = self.records()
        rows[1]["helper_count"] = 1
        with self.assertRaises(ValueError):
            summarize(self.config, rows)
        rows[1]["status"] = "infrastructure_invalid"
        self.assertEqual(summarize(self.config, rows)["matched_pairs"], 11)

    def test_non_delegating_enabled_attempt_retained(self):
        rows = self.records()
        rows[0].update(helper_count=0, helper_credits=0)
        arm = summarize(self.config, rows)["conditions"]["current-with-helpers"]
        self.assertEqual(arm["matched_attempts"], 12)
        self.assertEqual(arm["enabled_non_delegating_attempts"], 1)

    def test_results_must_be_an_array(self):
        with self.assertRaises(ValueError):
            summarize(self.config, {})

    def test_empty_results_report_missing_not_success(self):
        report = summarize(self.config, [])
        self.assertEqual(report["missing_starts"], 24)
        self.assertEqual(report["matched_pairs"], 0)
        for arm in report["conditions"].values():
            self.assertIsNone(arm["credits_per_accepted"])


if __name__ == "__main__":
    unittest.main()
