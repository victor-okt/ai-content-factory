import unittest
from trendhunter.community import atom_items, community_idea

DAY="2026-11-05"
def feed(title="A tiny robot comes alive in AI animation",media="https://v.redd.it/xyz123",published="2026-11-05T12:00:00+00:00"):
    return (f'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>{title}</title>
      <link href="https://www.reddit.com/r/aivideos/comments/abc123/example/"/>
      <published>{published}</published><content type="html">Video: {media}</content>
      </entry></feed>''').encode()

class CommunityFeedTests(unittest.TestCase):
    def test_atom_parser_has_media_link(self):
        items=atom_items(feed())
        self.assertEqual(len(items),1)
        self.assertTrue(items[0]["has_video"])
        self.assertEqual(items[0]["title"], "A tiny robot comes alive in AI animation")
    def test_video_creative_candidate_is_source_backed(self):
        item=atom_items(feed())[0]
        idea=community_idea(item, DAY)
        self.assertIsNotNone(idea)
        self.assertEqual(idea["source_type"],"community_post")
        self.assertEqual(idea["content_id"],"COMM-ABC123")
        self.assertFalse(idea["metrics_verified"])
        self.assertEqual(idea["approval_status"],"menunggu_persetujuan")
        self.assertIn("Bukan",idea["evidence_label"].capitalize())
    def test_no_video_does_not_qualify(self):
        item=atom_items(feed(media="https://example.com/image.jpg"))[0]
        self.assertFalse(item["has_video"])
        self.assertIsNone(community_idea(item,DAY))
    def test_help_question_does_not_qualify(self):
        item=atom_items(feed(title="How to make an animated toy video"))[0]
        self.assertIsNone(community_idea(item,DAY))
    def test_sensitive_post_does_not_qualify(self):
        item=atom_items(feed(title="Murder video shows animated robot"))[0]
        self.assertIsNone(community_idea(item,DAY))
    def test_old_video_does_not_qualify(self):
        item=atom_items(feed(published="2026-09-05T12:00:00+00:00"))[0]
        self.assertIsNone(community_idea(item,DAY))
if __name__=="__main__": unittest.main()
