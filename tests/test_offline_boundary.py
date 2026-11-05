"""Regression checks: offline pipeline must not imply publication or spend."""
import unittest
from datetime import datetime, timezone

from factory.pipeline import build_factory

NOW = datetime(2026, 11, 6, tzinfo=timezone.utc)


class OfflineBoundaryTests(unittest.TestCase):
    def test_editorial_lab_never_claims_verified_metrics_or_external_actions(self):
        report = {"ideas": [], "creative_seeds": [
            {"content_id": "lab-01", "title": "Original miniature city", "category": "miniature_world"}
        ]}
        result = build_factory(report, NOW)
        self.assertEqual(result["mode"], "editorial_lab")
        self.assertEqual(result["cost"]["spent_by_pipeline"], 0)
        self.assertFalse(result["cost"]["paid_services_called"])
        self.assertEqual(result["draft_count"], 1)
        job = result["jobs"][0]
        self.assertEqual(job["source_url"], "")
        self.assertFalse(job["metrics_verified"])
        self.assertIsNone(job["score"])
        self.assertEqual(job["visual_creator"]["rendered_images"], [])
        self.assertEqual(job["video_producer"]["rendered_video_url"], "")
        self.assertEqual(job["publisher"]["published_url"], "")
        self.assertIsNone(job["analyst"]["platform_views"])
        self.assertEqual(job["approval"]["publish"], "requires_user_approval")
        self.assertFalse(any(job["external_actions"].values()))

    def test_empty_inputs_produce_no_jobs_and_no_external_actions(self):
        result = build_factory({"ideas": [], "creative_seeds": []}, NOW)
        self.assertEqual(result["mode"], "no_ideas")
        self.assertEqual(result["draft_count"], 0)
        self.assertEqual(result["jobs"], [])
        self.assertEqual(result["cost"]["spent_by_pipeline"], 0)
        self.assertFalse(result["cost"]["paid_services_called"])


if __name__ == "__main__":
    unittest.main()
