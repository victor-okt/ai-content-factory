import unittest
from pathlib import Path
from html.parser import HTMLParser

class ScriptTags(HTMLParser):
    def __init__(self):
        super().__init__(); self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            self.sources.extend(v for k,v in attrs if k=="src")

class PixelUiContractTest(unittest.TestCase):
    def test_all_six_agents_visible(self):
        doc=Path("office/index.html").read_text("utf-8")
        for term in ("NOVA","KAI","MIRA","RIO","SORA","DEX"):
            self.assertIn(term,doc)
    def test_scripts_linked(self):
        p=ScriptTags();p.feed(Path("office/index.html").read_text("utf-8"))
        self.assertIn("./live.js",p.sources)
        self.assertIn("./factory.js",p.sources)
    def test_factory_indicates_real_gates(self):
        d=Path("office/factory.js").read_text("utf-8")
        self.assertIn("render belum dijalankan",d)
        self.assertIn("posting belum dilakukan",d)
        self.assertIn("data/factory.json",d)
    def test_workflow_runs_pipeline(self):
        yml=Path(".github/workflows/trend-hunter-daily.yml").read_text("utf-8")
        self.assertIn("python -m factory.pipeline",yml)
        self.assertIn("office/data/factory.json",yml)

if __name__=="__main__":
    unittest.main()
