import json
import logging
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jobqueue as jq

HERE = Path(__file__).resolve().parent
T0 = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
QUIET = logging.getLogger("test-quiet")
QUIET.addHandler(logging.NullHandler())
QUIET.propagate = False


def fetch(db, jid, cols="status,attempts,error"):
    return db.execute("SELECT %s FROM jobs WHERE id=?" % cols, (jid,)).fetchone()


class QueueBasics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = jq.connect(self.dir / "jobs.sqlite3")

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_persist_across_restart_and_run(self):
        jid = jq.enqueue(self.db, "kiro", "story_outline", {"idea": "Test"})
        self.db.close()
        self.db = jq.connect(self.dir / "jobs.sqlite3")  # "program dimatikan lalu dinyalakan lagi"
        self.assertEqual(jq.work_once(self.db), jid)
        status, result = fetch(self.db, jid, "status,result")
        self.assertEqual(status, "done")
        self.assertIn("offline_template_only", result)
        self.assertIn("template_not_ai", result)

    def test_quality_gate_never_auto_publishes(self):
        jid = jq.enqueue(self.db, "zek", "quality_gate", {})
        jq.work_once(self.db)
        result = json.loads(fetch(self.db, jid, "result")[0])
        self.assertIs(result["auto_publish"], False)

    def test_unknown_agent_rejected(self):
        with self.assertRaises(ValueError):
            jq.enqueue(self.db, "hacker", "story_outline", {})

    def test_unknown_kind_fails_at_once_without_retry(self):
        jid = jq.enqueue(self.db, "nox", "unknown", {}, now=T0)
        jq.work_once(self.db, now=T0)
        status, attempts, error = fetch(self.db, jid)
        self.assertEqual((status, attempts), ("failed", 1))
        self.assertIn("tidak didukung", error)

    def test_idempotency_key_prevents_duplicates(self):
        a = jq.enqueue(self.db, "kiro", "story_outline", {}, key="demo-1")
        b = jq.enqueue(self.db, "kiro", "story_outline", {}, key="demo-1")
        c = jq.enqueue(self.db, "kiro", "story_outline", {}, key="demo-2")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(self.db.execute("SELECT count(*) FROM jobs").fetchone()[0], 2)

    def test_no_idempotency_key_allows_many(self):
        for _ in range(3):
            jq.enqueue(self.db, "kiro", "story_outline", {})
        self.assertEqual(self.db.execute("SELECT count(*) FROM jobs").fetchone()[0], 3)

    def test_old_database_is_upgraded_and_stuck_job_recovered(self):
        old = self.dir / "old.sqlite3"
        raw = sqlite3.connect(str(old))
        raw.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, agent TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, "
                    "status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, "
                    "updated_at TEXT NOT NULL, result TEXT)")
        raw.execute("INSERT INTO jobs(agent,kind,payload,status,attempts,created_at,updated_at) VALUES('kiro','story_outline','{}','running',1,'x','x')")
        raw.execute("INSERT INTO jobs(agent,kind,payload,status,attempts,created_at,updated_at) VALUES('kiro','story_outline','{}','queued',0,'x','x')")
        raw.commit()
        raw.close()
        db = jq.connect(old)
        cols = {r[1] for r in db.execute("PRAGMA table_info(jobs)")}
        self.assertTrue({"max_attempts", "run_after", "lease_until", "idempotency_key", "error"} <= cols)
        self.assertEqual(jq.recover_stale(db), 1)
        while jq.work_once(db) is not None:
            pass
        self.assertEqual(jq.counts(db), {"done": 2})
        db.close()


class RetryAndRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = jq.connect(Path(self.tmp.name) / "jobs.sqlite3")

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_retry_with_backoff_then_final_failure(self):
        def boom(data, job):
            raise RuntimeError("provider mati")
        handlers = {"story_outline": boom}
        jid = jq.enqueue(self.db, "kiro", "story_outline", {}, max_attempts=3, now=T0)

        jq.work_once(self.db, handlers, now=T0)                       # percobaan 1 gagal -> antre lagi
        self.assertEqual(fetch(self.db, jid)[:2], ("queued", 1))
        self.assertIsNone(jq.work_once(self.db, handlers, now=T0 + timedelta(seconds=10)))  # belum waktunya

        jq.work_once(self.db, handlers, now=T0 + timedelta(seconds=31))   # percobaan 2
        self.assertEqual(fetch(self.db, jid)[:2], ("queued", 2))
        self.assertIsNone(jq.work_once(self.db, handlers, now=T0 + timedelta(seconds=100)))

        jq.work_once(self.db, handlers, now=T0 + timedelta(seconds=31 + 121))  # percobaan 3 -> final
        status, attempts, error = fetch(self.db, jid)
        self.assertEqual((status, attempts), ("failed", 3))
        self.assertIn("RuntimeError", error)

    def test_retry_can_succeed_later(self):
        calls = {"n": 0}

        def flaky(data, job):
            calls["n"] += 1
            if calls["n"] == 1:
                raise ConnectionError("putus")
            return {"ok": True}
        handlers = {"story_outline": flaky}
        jid = jq.enqueue(self.db, "kiro", "story_outline", {}, now=T0)
        jq.work_once(self.db, handlers, now=T0)
        jq.work_once(self.db, handlers, now=T0 + timedelta(seconds=40))
        self.assertEqual(fetch(self.db, jid)[:2], ("done", 2))

    def test_crash_mid_job_is_recovered_after_lease(self):
        jid = jq.enqueue(self.db, "kiro", "story_outline", {}, now=T0)
        jq.claim(self.db, now=T0, lease_seconds=300)       # proses mati setelah mengambil tugas
        self.assertEqual(fetch(self.db, jid)[0], "running")
        self.assertEqual(jq.recover_stale(self.db, now=T0 + timedelta(seconds=100)), 0)   # masih dalam lease
        self.assertEqual(fetch(self.db, jid)[0], "running")
        self.assertEqual(jq.recover_stale(self.db, now=T0 + timedelta(seconds=301)), 1)   # lease habis
        self.assertEqual(fetch(self.db, jid)[0], "queued")
        jq.work_once(self.db, now=T0 + timedelta(seconds=302))
        self.assertEqual(fetch(self.db, jid)[:2], ("done", 2))

    def test_crash_with_no_attempts_left_becomes_failed(self):
        jid = jq.enqueue(self.db, "kiro", "story_outline", {}, max_attempts=1, now=T0)
        jq.claim(self.db, now=T0, lease_seconds=300)
        jq.recover_stale(self.db, now=T0 + timedelta(seconds=301))
        status, attempts, error = fetch(self.db, jid)
        self.assertEqual(status, "failed")
        self.assertIn("percobaan habis", error)

    def test_late_finish_does_not_overwrite_recovered_job(self):
        jid = jq.enqueue(self.db, "kiro", "story_outline", {}, now=T0)
        job = jq.claim(self.db, now=T0, lease_seconds=300)
        jq.recover_stale(self.db, now=T0 + timedelta(seconds=301))      # dipulihkan -> queued
        jq._fail(self.db, job, "terlambat", T0 + timedelta(seconds=302), retry=False)  # worker lama baru melapor
        self.assertEqual(fetch(self.db, jid)[0], "queued")

    def test_report_lists_failures(self):
        jq.enqueue(self.db, "nox", "unknown", {})
        jq.work_once(self.db)
        text = jq.build_report(self.tmp.name, self.db)
        self.assertIn("Tugas gagal (1)", text)
        self.assertIn("tidak didukung", text)
        self.assertTrue((Path(self.tmp.name) / "report.md").exists())


class Concurrency(unittest.TestCase):
    def test_four_workers_never_take_the_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.sqlite3"
            setup = jq.connect(path)
            ids = [jq.enqueue(setup, "kiro", "story_outline", {"n": i}) for i in range(40)]
            setup.close()
            seen, lock = [], threading.Lock()

            def handler(data, job):
                with lock:
                    seen.append(job["id"])
                return {"ok": True}

            def worker():
                db = jq.connect(path)
                while jq.work_once(db, {"story_outline": handler}) is not None:
                    pass
                db.close()

            threads = [threading.Thread(target=worker) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(60)
            self.assertEqual(sorted(seen), sorted(ids))   # tiap tugas tepat satu kali
            check = jq.connect(path)
            self.assertEqual(jq.counts(check), {"done": 40})
            check.close()


class WorkerLoop(unittest.TestCase):
    def test_stop_file_stops_after_current_job(self):
        with tempfile.TemporaryDirectory() as d:
            dir_ = Path(d)
            db = jq.connect(dir_ / "jobs.sqlite3")
            for _ in range(3):
                jq.enqueue(db, "kiro", "story_outline", {})
            db.close()

            def stop_after_first(data, job):
                (dir_ / "STOP").write_text("stop")
                return {"ok": True}

            done = jq.run_worker(dir_, poll=0.2, handlers={"story_outline": stop_after_first}, log=QUIET)
            self.assertEqual(done, 1)
            db = jq.connect(dir_ / "jobs.sqlite3")
            self.assertEqual(jq.counts(db), {"done": 1, "queued": 2})
            db.close()
            self.assertTrue((dir_ / "status.json").exists())
            self.assertTrue((dir_ / "report.md").exists())

    def test_stale_stop_file_is_cleared_on_start(self):
        with tempfile.TemporaryDirectory() as d:
            dir_ = Path(d)
            (dir_ / "STOP").write_text("sisa lama")
            db = jq.connect(dir_ / "jobs.sqlite3")
            jq.enqueue(db, "zek", "quality_gate", {})
            db.close()
            self.assertEqual(jq.run_worker(dir_, until_empty=True, log=QUIET), 1)

    def test_worker_survives_crashing_handler(self):
        with tempfile.TemporaryDirectory() as d:
            def bad(data, job):
                raise ValueError("rusak")
            db = jq.connect(Path(d) / "jobs.sqlite3")
            jq.enqueue(db, "kiro", "story_outline", {}, max_attempts=1)
            jq.enqueue(db, "kiro", "story_outline", {}, max_attempts=1)
            db.close()
            done = jq.run_worker(d, until_empty=True, handlers={"story_outline": bad}, log=QUIET)
            self.assertEqual(done, 2)   # worker tidak mati meski semua tugas error
            db = jq.connect(Path(d) / "jobs.sqlite3")
            self.assertEqual(jq.counts(db), {"failed": 2})
            db.close()

    def test_worker_recovers_stuck_job_on_start(self):
        with tempfile.TemporaryDirectory() as d:
            db = jq.connect(Path(d) / "jobs.sqlite3")
            hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            jid = jq.enqueue(db, "kiro", "story_outline", {}, now=hour_ago)
            self.assertIsNotNone(jq.claim(db, now=hour_ago, lease_seconds=60))  # worker mati 1 jam lalu
            self.assertEqual(fetch(db, jid)[0], "running")
            db.close()
            self.assertEqual(jq.run_worker(d, until_empty=True, log=QUIET), 1)
            db = jq.connect(Path(d) / "jobs.sqlite3")
            self.assertEqual(fetch(db, jid)[:2], ("done", 2))
            db.close()


class CommandLine(unittest.TestCase):
    def run_cli(self, d, *args):
        out = subprocess.run([sys.executable, str(HERE / "jobqueue.py"), "--dir", d, *args],
                             capture_output=True, text=True, timeout=60, cwd=d)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return out.stdout.strip()

    def test_end_to_end_cli(self):
        with tempfile.TemporaryDirectory() as d:
            self.run_cli(d, "init")
            first = self.run_cli(d, "enqueue", "--key", "demo")
            second = self.run_cli(d, "enqueue", "--key", "demo")    # klik dua kali = tidak dobel
            self.assertEqual(first, second)
            self.run_cli(d, "enqueue", "--agent", "zek", "--kind", "quality_gate")
            self.assertIn("tugas diproses: 2", self.run_cli(d, "worker", "--until-empty"))
            self.assertEqual(json.loads(self.run_cli(d, "status")), {"done": 2})
            self.assertIn("template", self.run_cli(d, "report").lower())
            self.assertTrue((Path(d) / "logs" / "worker.log").exists())
            self.assertIn("STOP dibuat", self.run_cli(d, "stop"))


class NoStdlibShadowing(unittest.TestCase):
    def test_no_file_named_like_a_stdlib_module(self):
        self.assertFalse((HERE / "queue.py").exists(), "queue.py menimpa modul bawaan Python")
        import queue
        self.assertTrue(hasattr(queue, "Queue"))
        self.assertNotEqual(Path(queue.__file__).resolve().parent, HERE)


if __name__ == "__main__":
    unittest.main()
