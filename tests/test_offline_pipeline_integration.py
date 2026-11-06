"""End-to-end offline handoff: Agent 1 JSON -> Agent 2-6 draft artifact.

No external model, credentials, account connection, or publishing is required.
"""
import json
import tempfile
import unittest
from pathlib import Path

from factory.pipeline import run


class OfflinePipelineIntegrationTests(unittest.TestCase):
    def test_public_idea_becomes_safe_persisted_production_brief(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "office" / "data"
            data.mkdir(parents=True)
            (data / "latest.json").write_text(json.dumps({
                "last_checked_at": "2026-11-06T00:00:00+00:00",
                "ideas": [{
                    "content_id": "integration-001",
                    "title": "A miniature city on a desk",
                    "category": "miniature_world",
                    "source_url": "https://example.org/story",
                    "score": 42,
                }],
                "creative_seeds": [],
            }), encoding="utf-8")

            result = run(root)
            saved = json.loads((data / "factory.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, result)
            self.assertEqual(saved["draft_count"], 1)
            self.assertEqual(saved["mode"], "public_research")
            job = saved["jobs"][0]
            self.assertEqual(job["content_id"], "integration-001")
            self.assertEqual(job["creative_director"]["format"], "9:16")
            self.assertEqual(job["creative_director"]["duration_seconds"], 30)
            self.assertEqual(job["video_producer"]["shot_timeline"],
                             job["creative_director"]["storyboard"])
            self.assertEqual(len(job["visual_creator"]["reference_frames"]), 6)
            self.assertEqual(len(job["open_source_video_plan"]["clips"]), 6)
            self.assertFalse(job["open_source_video_plan"]["render_enabled"])
            self.assertTrue(job["publisher"]["caption_draft"])
            self.assertEqual(job["visual_creator"]["rendered_images"], [])
            self.assertEqual(job["video_producer"]["rendered_video_url"], "")
            self.assertEqual(job["publisher"]["published_url"], "")
            self.assertIsNone(job["analyst"]["platform_views"])
            self.assertFalse(any(job["external_actions"].values()))
            self.assertEqual(saved["cost"]["spent_by_pipeline"], 0)
            self.assertFalse(saved["cost"]["paid_services_called"])

    def test_empty_report_writes_empty_safe_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "office" / "data"
            data.mkdir(parents=True)
            (data / "latest.json").write_text(
                '{"ideas": [], "creative_seeds": []}', encoding="utf-8")
            saved = run(root)
            self.assertEqual(saved["mode"], "no_ideas")
            self.assertEqual(saved["jobs"], [])
            self.assertEqual(json.loads(
                (data / "factory.json").read_text(encoding="utf-8"))["draft_count"], 0)


if __name__ == "__main__":
    unittest.main()
