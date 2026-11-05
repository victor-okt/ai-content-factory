import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from trendhunter.daily import run

WIB = timezone(timedelta(hours=7))
RSS = b'<rss><channel><item><title>Toy figurine comes alive in stop motion AI video</title><link>https://example.com/toy-film</link><pubDate>Thu, 05 Nov 2026 03:00:00 GMT</pubDate></item></channel></rss>'

class TestDailyHistory(unittest.TestCase):
    def test_same_day_overwrites_and_next_day_appends(self):
        with tempfile.TemporaryDirectory() as folder:
            day1 = datetime(2026, 11, 5, 12, tzinfo=WIB)
            report = run(fetcher=lambda _: RSS, when=day1, root=folder)
            self.assertEqual(report['status'], 'ok')
            path = Path(folder) / 'office/data/history.json'
            self.assertTrue(path.exists())
            history = json.loads(path.read_text('utf-8'))
            self.assertEqual(len(history['entries']), 1)
            self.assertGreater(history['entries'][0]['items_scanned'], 0)
            self.assertEqual(history['entries'][0]['qualifying_examples'], 1)
            run(fetcher=lambda _: RSS, when=day1 + timedelta(hours=1), root=folder)
            history = json.loads(path.read_text('utf-8'))
            self.assertEqual(len(history['entries']), 1)
            run(fetcher=lambda _: RSS, when=day1 + timedelta(days=1), root=folder)
            history = json.loads(path.read_text('utf-8'))
            self.assertEqual([v['date'] for v in history['entries']], ['2026-11-05', '2026-11-06'])
            self.assertEqual(history['schema_version'], 1)

    def test_failure_recorded_without_faking_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            def fail(_): raise OSError('source unavailable')
            result=run(fetcher=fail, when=datetime(2026,11,5,12,tzinfo=WIB), root=folder)
            self.assertEqual(result['status'], 'error')
            history=json.loads((Path(folder)/'office/data/history.json').read_text('utf-8'))
            self.assertEqual(history['entries'][0]['source_errors'], len(result['errors']))
            self.assertEqual(history['entries'][0]['qualifying_examples'], 0)

if __name__ == '__main__':
    unittest.main()
