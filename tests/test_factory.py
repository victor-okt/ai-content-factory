import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from factory.pipeline import build_factory, run

WIB=timezone(timedelta(hours=7))
STAMP=datetime(2026,11,6,6,0,tzinfo=WIB)
SOURCE={"content_id":"COMM-ABC123","title":"Cute toy robot comes alive","category":"object_comes_alive",
        "score":79,"source_type":"community_post","source_url":"https://www.reddit.com/r/aivideos/comments/abc123/example/"}
SEED={"content_id":"LAB-1","title":"Mainan menjadi hidup","category":"object_comes_alive","source_url":""}

class FactoryTest(unittest.TestCase):
    def test_source_backed_pipeline_and_status(self):
        d=build_factory({"ideas":[SOURCE],"creative_seeds":[SEED],"last_checked_at":"2026-11-06T04:00:00+07:00"},STAMP)
        self.assertEqual(d["mode"],"public_research")
        self.assertEqual(d["draft_count"],1)
        self.assertEqual(d["jobs"][0]["source_url"],SOURCE["source_url"])
        self.assertEqual(d["jobs"][0]["creative_director"]["storyboard"][2]["seconds"],[8,12])
        self.assertEqual(d["jobs"][0]["video_producer"]["status"],"render_blocked")
        self.assertFalse(d["jobs"][0]["external_actions"]["posting"])
        self.assertEqual(d["cost"]["spent_by_pipeline"],0)
        self.assertEqual(len(d["agents"]),6)
    def test_lab_is_not_misrepresented(self):
        d=build_factory({"ideas":[],"creative_seeds":[SEED]},STAMP)
        self.assertEqual(d["mode"],"editorial_lab")
        self.assertIn("LAB",d["jobs"][0]["origin"])
        self.assertEqual(d["jobs"][0]["source_url"],"")
        self.assertIsNone(d["jobs"][0]["score"])
    def test_empty_is_safe(self):
        d=build_factory({"ideas":[],"creative_seeds":[]},STAMP)
        self.assertEqual(d["mode"],"no_ideas")
        self.assertEqual(d["jobs"],[])
    def test_dedupe_and_cap(self):
        ideas=[dict(SOURCE,content_id=f"COMM-{i}") for i in range(8)]
        d=build_factory({"ideas":ideas+[ideas[0]],"creative_seeds":[]},STAMP)
        self.assertEqual(len(d["jobs"]),3)
        self.assertEqual(len({j["content_id"] for j in d["jobs"]}),3)
    def test_unsafe_source_rejected(self):
        d=build_factory({"ideas":[dict(SOURCE, source_url="javascript:alert(1)")],"creative_seeds":[]},STAMP)
        self.assertEqual(d["draft_count"],0)
    def test_file_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"office/data/latest.json"
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({"ideas":[SOURCE],"creative_seeds":[]}),encoding="utf-8")
            result=run(temp)
            self.assertEqual(result["draft_count"],1)
            self.assertEqual(json.loads((p.parent/"factory.json").read_text(encoding="utf-8"))["draft_count"],1)

if __name__=="__main__":
    unittest.main()
