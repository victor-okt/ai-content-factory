import json, tempfile, unittest
from datetime import datetime,timedelta,timezone
from trendhunter.daily import run,rss_items,idea_from
WIB=timezone(timedelta(hours=7))
RSS=b'<rss><channel><item><title>Toy figurine stop motion animated video</title><link>https://example.com/story</link><pubDate>Thu, 05 Nov 2026 03:00:00 GMT</pubDate></item></channel></rss>'
class TrendHunterTests(unittest.TestCase):
    def test_parse_feed(self):
        self.assertEqual(rss_items(RSS)[0]['title'],'Toy figurine stop motion animated video')
    def test_report_and_deduplication(self):
        with tempfile.TemporaryDirectory() as d:
            clock=datetime(2026,11,5,12,tzinfo=WIB)
            report=run(fetcher=lambda _:RSS,when=clock,root=d)
            self.assertEqual(report['status'],'ok')
            self.assertEqual(len(report['ideas']),1)
            self.assertFalse(report['ideas'][0]['metrics_verified'])
            report2=run(fetcher=lambda _:RSS,when=clock,root=d)
            self.assertTrue(report2['ideas'][0]['seen_before'])
    def test_fail_preserves_previous_results(self):
        with tempfile.TemporaryDirectory() as d:
            clock=datetime(2026,11,5,12,tzinfo=WIB)
            run(fetcher=lambda _:RSS,when=clock,root=d)
            def fail(url): raise OSError('test outage')
            report=run(fetcher=fail,when=clock,root=d)
            self.assertEqual(report['status'],'stale')
            self.assertEqual(len(report['ideas']),1)
    def test_irrelevant_rejected(self):
        self.assertIsNone(idea_from({'title':'Politik dan kecelakaan','link':'https://example.com','pubDate':''},'trends','2026-11-05'))
if __name__=='__main__': unittest.main()
