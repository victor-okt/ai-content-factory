import unittest
from trendhunter.daily import idea_from
from trendhunter.quality import rejection, title_key

class QualityGateTests(unittest.TestCase):
    def test_spam_rejected(self):
        for title in ["Instagram Viral 80s Photo Prompt","Tutorial cara membuat AI video","Software AI Video Review","Jellysmack aplikasi video"]:
            self.assertIsNone(idea_from({"title":title,"link":"https://example.com"}, "news","2026-11-05"))
    def test_generic_business_news_rejected(self):
        self.assertIsNone(idea_from({"title":"Teknologi AI Lokal Bidik Industri Kreatif Video","link":"https://example.com"}, "news","2026-11-05"))
    def test_creative_subject_accepted(self):
        result=idea_from({"title":"Toy figurine comes alive in stop motion AI video","link":"https://example.com","pubDate":"Thu, 05 Nov 2026 03:00:00 GMT"},"news","2026-11-05")
        self.assertIsNotNone(result)
        self.assertFalse(result["metrics_verified"])
        self.assertEqual(sum(result["score_breakdown"].values()),result["score"])
        self.assertIn("creative_brief",result)
        self.assertEqual(result["approval_status"],"menunggu_persetujuan")
    def test_trends_must_be_entertainment(self):
        self.assertIsNone(idea_from({"title":"Harga minyak","link":"https://example.com"},"trends","2026-11-05"))
    def test_stable_id_across_publishers(self):
        self.assertEqual(title_key("Toy figure comes alive - Site X","object_comes_alive"),title_key("Toy figure comes alive - Site Y","object_comes_alive"))
    def test_sensitive_topic_rejected(self):
        self.assertIsNone(idea_from({"title":"Kecelakaan video anime viral","link":"https://example.com"},"news","2026-11-05"))
if __name__=="__main__": unittest.main()
