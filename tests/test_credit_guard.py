"""Credit Guard tests: zero rupiah, one attempt, simulation only."""
import unittest

from factory.credit_guard import (
    DAILY_BUDGET_IDR, MAX_ATTEMPTS_PER_VIDEO, SIMULATION_ONLY,
    authorize_video_attempt, public_policy,
)
from factory.pipeline import build_factory


class CreditGuardTests(unittest.TestCase):
    def test_policy_is_zero_budget_and_one_attempt(self):
        self.assertEqual(DAILY_BUDGET_IDR, 0)
        self.assertEqual(MAX_ATTEMPTS_PER_VIDEO, 1)
        self.assertTrue(SIMULATION_ONLY)
        policy = public_policy()
        self.assertEqual(policy["daily_budget_idr"], 0)
        self.assertEqual(policy["max_attempts_per_video"], 1)
        self.assertFalse(policy["paid_generation_allowed"])
        self.assertEqual(policy["actual_spend_idr"], 0)

    def test_paid_generation_is_denied_even_on_first_attempt(self):
        decision = authorize_video_attempt(
            video_id="video-1", attempt_number=1, estimated_cost_idr=1)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "zero_budget_blocks_paid_generation")
        self.assertEqual(decision.actual_spend_idr, 0)

    def test_free_attempt_still_only_simulates(self):
        decision = authorize_video_attempt(
            video_id="video-1", attempt_number=1, estimated_cost_idr=0)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "simulation_only_no_provider_execution")

    def test_second_attempt_is_denied(self):
        decision = authorize_video_attempt(
            video_id="video-1", attempt_number=2, estimated_cost_idr=0)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "attempt_limit_exceeded")

    def test_invalid_values_fail_closed(self):
        cases = [
            {"video_id": "", "attempt_number": 1, "estimated_cost_idr": 0},
            {"video_id": "v", "attempt_number": 0, "estimated_cost_idr": 0},
            {"video_id": "v", "attempt_number": True, "estimated_cost_idr": 0},
            {"video_id": "v", "attempt_number": 1, "estimated_cost_idr": -1},
            {"video_id": "v", "attempt_number": 1, "estimated_cost_idr": 1.5},
            {"video_id": "v", "attempt_number": 1, "estimated_cost_idr": 0,
             "spent_today_idr": -1},
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                authorize_video_attempt(**case)

    def test_factory_report_includes_guard_without_spending(self):
        report = build_factory({"ideas": [], "creative_seeds": []})
        self.assertEqual(report["credit_guard"], public_policy())
        self.assertFalse(report["cost"]["paid_services_called"])
        self.assertEqual(report["cost"]["spent_by_pipeline"], 0)


if __name__ == "__main__":
    unittest.main()
