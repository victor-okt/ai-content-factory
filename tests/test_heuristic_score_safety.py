"""Regression checks for untrusted Agent 1 heuristic scores."""
import json
import unittest
from datetime import datetime, timezone

from factory.pipeline import build_factory

NOW = datetime(2026, 11, 6, tzinfo=timezone.utc)


class HeuristicScoreSafetyTests(unittest.TestCase):
    def test_nonfinite_and_non_numeric_scores_are_not_exported(self):
        values = [float("nan"), float("inf"), float("-inf"),
                  "99", True, {"points": 42}, [1], None]
        for value in values:
            with self.subTest(value=repr(value)):
                report = {"ideas": [{
                    "content_id": "score-case",
                    "title": "Original scene",
                    "source_url": "https://example.org/source",
                    "score": value,
                }], "creative_seeds": []}
                output = build_factory(report, NOW)
                self.assertIsNone(output["jobs"][0]["score"])
                json.dumps(output, allow_nan=False)

    def test_finite_numeric_scores_remain_heuristic(self):
        for value in [0, 1, -3, 12.5]:
            with self.subTest(value=value):
                report = {"ideas": [{
                    "content_id": "score-case",
                    "title": "Original scene",
                    "source_url": "https://example.org/source",
                    "score": value,
                }], "creative_seeds": []}
                output = build_factory(report, NOW)
                self.assertEqual(output["jobs"][0]["score"], value)
                self.assertFalse(output["jobs"][0]["metrics_verified"])
                json.dumps(output, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
