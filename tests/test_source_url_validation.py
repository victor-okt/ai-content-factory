"""URL validation regression tests for public source ingestion (offline only)."""
import unittest

from factory.pipeline import safe_link, build_factory


class SourceURLValidationTest(unittest.TestCase):
    def test_accepts_normal_public_links(self):
        self.assertEqual(safe_link("https://example.org/story?q=1"), "https://example.org/story?q=1")
        self.assertEqual(safe_link("http://example.org/story"), "http://example.org/story")

    def test_rejects_ambiguous_or_malformed_links(self):
        for url in (
            "https://", "https:///missing-host", "https://example.org:bad/path",
            "https://example.org:99999/path", "https://user:pass@example.org/path",
            "https://example.org\\@evil.test/path", "https://example.org/path\nInjected: value",
            "https://example.org/path with spaces", "javascript:alert(1)",
        ):
            with self.subTest(url=url):
                self.assertEqual(safe_link(url), "")

    def test_invalid_sources_do_not_generate_public_drafts(self):
        report = {"ideas": [{
            "content_id": "bad-url", "title": "Unsafe reference",
            "source_url": "https://example.org:bad/story",
            "category": "miniature_world",
        }], "creative_seeds": []}
        output = build_factory(report)
        self.assertEqual(output["draft_count"], 0)
        self.assertEqual(output["mode"], "no_ideas")


if __name__ == "__main__":
    unittest.main()
