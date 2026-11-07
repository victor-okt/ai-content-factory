import json, unittest
from pathlib import Path
DATA=Path(__file__).with_name("story_bank.json")
class StoryBankTests(unittest.TestCase):
 def setUp(self): self.data=json.loads(DATA.read_text(encoding="utf-8"))
 def test_unique(self):
  ids=[s["id"] for s in self.data["stories"]]; self.assertEqual(len(ids),len(set(ids)))
 def test_duration(self): self.assertTrue(all(20<=s["duration_seconds"]<=40 for s in self.data["stories"]))
 def test_structure(self): self.assertTrue(all(all(s.get(k) for k in ("hook","conflict","twist","ending")) for s in self.data["stories"]))
 def test_selected(self): self.assertIn(self.data["selected_id"],[s["id"] for s in self.data["stories"]])
 def test_scores(self): self.assertTrue(all(s["editorial_score"]==4*s["clarity"]+4*s["retention"]+5*s["payoff"] for s in self.data["stories"]))
if __name__=="__main__": unittest.main()
