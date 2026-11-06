"""Offline dashboard contract checks; no browser, accounts, or API keys needed."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DashboardContractTests(unittest.TestCase):
    def test_dashboard_loads_factory_script_and_artifact(self):
        html = (ROOT / "office" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "office" / "factory.js").read_text(encoding="utf-8")
        self.assertIn('src="./factory.js"', html)
        self.assertIn("./data/factory.json", script)
        self.assertIn("schema_version", script)
        self.assertIn("render belum dijalankan", script)
        self.assertIn("posting belum dilakukan", script)

    def test_manual_refresh_does_not_trigger_external_actions(self):
        script = (ROOT / "office" / "factory.js").read_text(encoding="utf-8")
        self.assertIn("refresh.onclick=load", script)
        self.assertIn('fetch("./data/factory.json?ts="', script)
        self.assertIn('{cache:"no-store"}', script)
        self.assertIn("refresh.disabled=true", script)
        self.assertIn("refresh.disabled=false", script)
        self.assertNotIn("fetch(\"https://", script)

    def test_published_snapshot_has_consistent_draft_counts(self):
        path = ROOT / "office" / "data" / "factory.json"
        self.assertTrue(path.is_file(), "Production dashboard needs factory.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["draft_count"], len(data["jobs"]))
        self.assertLessEqual(data["draft_count"], 3)
        self.assertEqual(len(data["agents"]), 6)
        self.assertFalse(data["cost"]["paid_services_called"])
        for job in data["jobs"]:
            with self.subTest(content_id=job["content_id"]):
                self.assertFalse(any(job["external_actions"].values()))
                self.assertEqual(job["visual_creator"]["rendered_images"], [])
                self.assertEqual(job["video_producer"]["rendered_video_url"], "")
                self.assertEqual(job["publisher"]["published_url"], "")
                self.assertIsNone(job["analyst"]["platform_views"])


if __name__ == "__main__":
    unittest.main()
