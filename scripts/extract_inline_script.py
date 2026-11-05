"""Extract inline JavaScript from the Pixel Office HTML for syntax checks."""
from html.parser import HTMLParser
from pathlib import Path

class Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.inside = "src" not in attrs
            if self.inside:
                self.blocks.append("")
    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False
    def handle_data(self, data):
        if self.inside and self.blocks:
            self.blocks[-1] += data

if __name__ == "__main__":
    src = Path("office/index.html")
    assert src.exists(), "Pixel Office HTML missing"
    p = Extract()
    p.feed(src.read_text("utf-8"))
    assert p.blocks, "No interactive inline JS found"
    output = Path("/tmp/pixel-office-inline.js")
    output.write_text("\n".join(p.blocks), "utf-8")
    print("Extracted", len(p.blocks), "script blocks:", output)
