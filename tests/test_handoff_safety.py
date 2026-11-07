"""Regression tests for offline-only factory handoff safety and output contract."""
import unittest
from datetime import datetime, timezone

from factory.pipeline import build_factory

NOW = datetime(2026, 11, 6, tzinfo=timezone.utc)
SOURCE = {
    "content_id": "SOURCE-1",
    "title": "Original miniature scene",
    "category": "miniature_world",
    "source_url": "https://example.org/story",
    "score": 70,
}


class HandoffSafetyTest(unittest.TestCase):
    def test_no_external_side_effects_or_fake_analytics(self):
        output = build_factory({"ideas": [SOURCE], "creative_seeds": []}, NOW)
        self.assertEqual(output["cost"]["spent_by_pipeline"], 0)
        self.assertFalse(output["cost"]["paid_services_called"])
        for job in output["jobs"]:
            self.assertEqual(job["external_actions"], {
                "image_generation": False, "video_generation": False, "posting": False
            })
            self.assertEqual(job["visual_creator"]["rendered_images"], [])
            self.assertEqual(job["video_producer"]["rendered_video_url"], "")
            self.assertEqual(job["publisher"]["published_url"], "")
            self.assertIsNone(job["analyst"]["platform_views"])
            self.assertIsNone(job["analyst"]["retention"])
            self.assertIsNone(job["analyst"]["revenue"])
            self.assertEqual(job["approval"]["publish"], "requires_user_approval")

    def test_source_with_embedded_credentials_is_rejected(self):
        output = build_factory({"ideas": [
            dict(SOURCE, source_url="https://user:password@example.org/story")
        ], "creative_seeds": []}, NOW)
        self.assertEqual(output["draft_count"], 0)

    def test_unknown_category_falls_back_without_crashing(self):
        output = build_factory({"ideas": [
            dict(SOURCE, category="unknown_future_category")
        ], "creative_seeds": []}, NOW)
        self.assertEqual(output["draft_count"], 1)
        self.assertEqual(output["jobs"][0]["creative_director"]["method"],
                         "template_free_no_llm")
        self.assertEqual(len(output["jobs"][0]["creative_director"]["storyboard"]), 6)


if __name__ == "__main__":
    unittest.main()
