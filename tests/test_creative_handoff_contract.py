"""Contract tests for Agent 2 storyboard and Agent 3-6 offline handoff."""
import unittest
from datetime import datetime, timezone

from factory.pipeline import build_factory

FIXED = datetime(2026, 11, 6, tzinfo=timezone.utc)


class CreativeHandoffContractTests(unittest.TestCase):
    def test_storyboard_timing_and_downstream_draft_boundaries(self):
        report = {"ideas": [{
            "content_id": "public-001",
            "title": "Tiny city on a desk",
            "category": "miniature_world",
            "source_url": "https://example.org/creative",
        }], "creative_seeds": []}
        result = build_factory(report, FIXED)
        self.assertEqual(result["mode"], "public_research")
        self.assertEqual(result["draft_count"], 1)
        job = result["jobs"][0]
        director = job["creative_director"]
        self.assertEqual(director["method"], "template_free_no_llm")
        self.assertEqual(director["duration_seconds"], 12)
        self.assertEqual(director["format"], "9:16")
        self.assertEqual([scene["seconds"] for scene in director["storyboard"]],
                         [[0, 2], [2, 8], [8, 12]])
        self.assertEqual([scene["shot"] for scene in director["storyboard"]], [1, 2, 3])
        self.assertEqual(job["video_producer"]["shot_timeline"], director["storyboard"])
        self.assertEqual(len(job["visual_creator"]["reference_frames"]), 3)
        self.assertEqual(job["visual_creator"]["rendered_images"], [])
        self.assertEqual(job["video_producer"]["rendered_video_url"], "")
        self.assertEqual(job["publisher"]["published_url"], "")
        self.assertIsNone(job["analyst"]["platform_views"])
        self.assertFalse(any(job["external_actions"].values()))

    def test_invalid_public_sources_do_not_create_public_drafts(self):
        for url in ("file:///etc/passwd", "https://user:pass@example.org/a",
                    "https://example.org:99999/a", "https://example.org/has path",
                    "https://example.org/\\\\evil"):
            with self.subTest(url=url):
                result = build_factory({"ideas": [{
                    "content_id": "bad", "title": "Untrusted source",
                    "source_url": url,
                }], "creative_seeds": []}, FIXED)
                self.assertEqual(result["draft_count"], 0)
                self.assertEqual(result["mode"], "no_ideas")

    def test_duplicate_ids_are_deduplicated_and_job_count_is_capped(self):
        ideas = [{
            "content_id": f"idea-{i}", "title": f"Scene {i}",
            "source_url": "https://example.org/source",
        } for i in range(6)]
        ideas.insert(1, dict(ideas[0]))
        result = build_factory({"ideas": ideas, "creative_seeds": []}, FIXED)
        self.assertEqual(result["draft_count"], 3)
        self.assertEqual([j["content_id"] for j in result["jobs"]],
                         ["idea-0", "idea-1", "idea-2"])


if __name__ == "__main__":
    unittest.main()
