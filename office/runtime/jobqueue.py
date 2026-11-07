"""Antrean tugas lokal Pixel Office + VO1995 (SQLite) dan worker-nya.

Fitur yang SUDAH diuji (lihat test_jobqueue.py):
- tugas tersimpan di disk, tetap ada setelah program mati
- pemulihan tugas 'running' yang tertinggal setelah crash / mati listrik
- retry terbatas dengan jeda bertahap
- idempotensi: kunci yang sama tidak membuat tugas ganda
- dua worker tidak mengambil tugas yang sama
- berhenti dengan aman (file STOP, Ctrl+C, atau perintah `stop`)
- log berputar dan status.json / report.md

Yang BELUM ada: model AI, ElevenLabs, render video. Tugas story_outline dan
quality_gate masih TEMPLATE, bukan AI generatif. Tidak ada panggilan API
berbayar dan tidak ada publikasi otomatis.

Catatan: file ini sengaja TIDAK bernama queue.py karena akan menimpa modul
bawaan Python bernama `queue`.
"""
import argparse
import json
import logging
import os
import signal
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

AGENTS = {"nox", "kiro", "miko", "riku", "senn", "zek"}
DEFAULT_LEASE_SECONDS = 300        # tugas dianggap macet jika melewati batas ini
DEFAULT_MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (30, 120, 600)   # jeda sebelum percobaan ke-2, ke-3, dst.
DEFAULT_DIR = Path(os.environ.get("OFFICE_RUNTIME_DIR", Path(__file__).resolve().parent / "runtime-data"))

_NEW_COLUMNS = {
    "max_attempts": "INTEGER NOT NULL DEFAULT 3",
    "run_after": "TEXT",
    "lease_until": "TEXT",
    "idempotency_key": "TEXT",
    "error": "TEXT",
}


class PermanentError(Exception):
    """Kegagalan yang tidak akan berhasil jika diulang (tidak di-retry)."""


def iso(dt=None):
    """Format waktu tetap (UTC) supaya perbandingan teks sama dengan urutan waktu."""
    dt = dt or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


# --------------------------------------------------------------------------- database
def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=30, isolation_level=None)  # autocommit; transaksi manual
    db.execute("PRAGMA busy_timeout=30000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute(
        "CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, agent TEXT NOT NULL, kind TEXT NOT NULL, "
        "payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0, "
        "created_at TEXT NOT NULL, updated_at TEXT NOT NULL, result TEXT)"
    )
    have = {row[1] for row in db.execute("PRAGMA table_info(jobs)")}
    for col, ddl in _NEW_COLUMNS.items():  # upgrade database lama dari queue.py versi awal
        if col not in have:
            db.execute("ALTER TABLE jobs ADD COLUMN %s %s" % (col, ddl))
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS jobs_idem ON jobs(idempotency_key) WHERE idempotency_key IS NOT NULL"
    )
    return db


def _transaction(db, fn):
    db.execute("BEGIN IMMEDIATE")
    try:
        out = fn()
        db.execute("COMMIT")
        return out
    except BaseException:
        db.execute("ROLLBACK")
        raise


def enqueue(db, agent, kind, payload, key=None, max_attempts=DEFAULT_MAX_ATTEMPTS, now=None):
    """Masukkan tugas. Jika `key` sudah pernah dipakai, kembalikan id tugas lama (tidak ganda)."""
    if agent not in AGENTS:
        raise ValueError("agent tidak dikenal: %s" % agent)
    t = iso(now)
    cur = db.execute(
        "INSERT OR IGNORE INTO jobs(agent,kind,payload,status,max_attempts,run_after,idempotency_key,created_at,updated_at) "
        "VALUES(?,?,?,'queued',?,?,?,?,?)",
        (agent, kind, json.dumps(payload, ensure_ascii=False), int(max_attempts), t, key, t, t),
    )
    if cur.rowcount == 0 and key is not None:
        return db.execute("SELECT id FROM jobs WHERE idempotency_key=?", (key,)).fetchone()[0]
    return cur.lastrowid


def recover_stale(db, now=None):
    """Tugas 'running' yang lease-nya habis berarti prosesnya mati. Antrikan lagi, atau gagalkan jika percobaan habis."""
    t = iso(now)

    def work():
        rows = db.execute(
            "SELECT id,attempts,max_attempts FROM jobs WHERE status='running' AND (lease_until IS NULL OR lease_until<?)",
            (t,),
        ).fetchall()
        for jid, attempts, max_attempts in rows:
            if attempts >= max_attempts:
                db.execute(
                    "UPDATE jobs SET status='failed',lease_until=NULL,error=?,updated_at=? WHERE id=?",
                    ("proses terhenti (crash/mati listrik) dan percobaan habis", t, jid),
                )
            else:
                db.execute(
                    "UPDATE jobs SET status='queued',lease_until=NULL,run_after=?,error=?,updated_at=? WHERE id=?",
                    (t, "dipulihkan setelah proses terhenti", t, jid),
                )
        return len(rows)

    return _transaction(db, work)


def claim(db, now=None, lease_seconds=DEFAULT_LEASE_SECONDS):
    """Ambil satu tugas secara atomik. Dua worker tidak akan mendapat tugas yang sama."""
    now = now or datetime.now(timezone.utc)
    t = iso(now)

    def work():
        row = db.execute(
            "SELECT id,agent,kind,payload,attempts,max_attempts FROM jobs "
            "WHERE status='queued' AND (run_after IS NULL OR run_after<=?) ORDER BY id LIMIT 1",
            (t,),
        ).fetchone()
        if row is None:
            return None
        db.execute(
            "UPDATE jobs SET status='running',attempts=attempts+1,lease_until=?,updated_at=? WHERE id=?",
            (iso(now + timedelta(seconds=lease_seconds)), t, row[0]),
        )
        return {"id": row[0], "agent": row[1], "kind": row[2], "payload": row[3],
                "attempts": row[4] + 1, "max_attempts": row[5]}

    return _transaction(db, work)


def _fail(db, job, message, now, retry):
    t = iso(now)
    if retry and job["attempts"] < job["max_attempts"]:
        wait = BACKOFF_SECONDS[min(job["attempts"] - 1, len(BACKOFF_SECONDS) - 1)]
        db.execute(
            "UPDATE jobs SET status='queued',lease_until=NULL,run_after=?,error=?,updated_at=? WHERE id=? AND status='running'",
            (iso(now + timedelta(seconds=wait)), message, t, job["id"]),
        )
    else:
        db.execute(
            "UPDATE jobs SET status='failed',lease_until=NULL,error=?,updated_at=? WHERE id=? AND status='running'",
            (message, t, job["id"]),
        )


def work_once(db, handlers=None, now=None, lease_seconds=DEFAULT_LEASE_SECONDS):
    """Kerjakan satu tugas. Mengembalikan id tugas, atau None jika tidak ada yang siap."""
    handlers = HANDLERS if handlers is None else handlers
    job = claim(db, now, lease_seconds)
    if job is None:
        return None
    now = now or datetime.now(timezone.utc)
    try:
        fn = handlers.get(job["kind"])
        if fn is None:
            raise PermanentError("jenis tugas tidak didukung: %s" % job["kind"])
        result = fn(json.loads(job["payload"]), job)
        db.execute(
            "UPDATE jobs SET status='done',result=?,error=NULL,lease_until=NULL,updated_at=? WHERE id=? AND status='running'",
            (json.dumps(result, ensure_ascii=False), iso(now), job["id"]),
        )
    except PermanentError as exc:
        _fail(db, job, str(exc), now, retry=False)
    except Exception as exc:  # noqa: BLE001 - semua error tugas dicatat, worker tidak boleh mati
        _fail(db, job, "%s: %s" % (type(exc).__name__, exc), now, retry=True)
    return job["id"]


# --------------------------------------------------------------------------- tugas (MASIH TEMPLATE)
def handle_story_outline(data, job):
    idea = data.get("idea", "Bayangan yang Ingin Libur")
    return {
        "idea": idea,
        "hook": "Bayangan Kitsune mendadak berhenti mengikutinya.",
        "conflict": "Kitsune berusaha membujuk bayangannya bergerak.",
        "twist": "Bayangannya hanya ingin beristirahat bersama Kitsune.",
        "status": "offline_template_only",
        "generator": "template_not_ai",
        "requires_review": True,
    }


def handle_quality_gate(data, job):
    return {
        "status": "needs_human_review",
        "checks": ["real character movement", "subtitle safe area", "voice quality", "story payoff"],
        "generator": "template_not_ai",
        "auto_publish": False,
    }


HANDLERS = {"story_outline": handle_story_outline, "quality_gate": handle_quality_gate}


# --------------------------------------------------------------------------- status, laporan, log
def counts(db):
    return {status: n for status, n in db.execute("SELECT status,count(*) FROM jobs GROUP BY status")}


def write_status(dir_, db, last_job=None):
    dir_ = Path(dir_)
    data = {"updated_at": iso(), "pid": os.getpid(), "counts": counts(db), "last_job": last_job,
            "publishing": "disabled", "paid_api": "disabled"}
    tmp = dir_ / "status.json.tmp"
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(dir_ / "status.json"))
    return data


def build_report(dir_, db):
    c = counts(db)
    lines = ["# Laporan Antrean Pixel Office", "", "Dibuat: " + iso(), "",
             "Jumlah tugas per status: " + (json.dumps(c) if c else "(kosong)"), "",
             "Catatan: tugas story_outline dan quality_gate masih TEMPLATE, bukan AI generatif.", ""]
    failed = db.execute("SELECT id,agent,kind,attempts,error FROM jobs WHERE status='failed' ORDER BY id").fetchall()
    lines.append("## Tugas gagal (%d)" % len(failed))
    lines += ["- #%s %s/%s, %s percobaan: %s" % row for row in failed] or ["- tidak ada"]
    waiting = db.execute("SELECT id,agent,kind,attempts,run_after,error FROM jobs WHERE status='queued' AND attempts>0").fetchall()
    lines += ["", "## Menunggu retry (%d)" % len(waiting)]
    lines += ["- #%s %s/%s, percobaan %s, coba lagi setelah %s: %s" % row for row in waiting] or ["- tidak ada"]
    text = "\n".join(lines) + "\n"
    (Path(dir_) / "report.md").write_text(text, encoding="utf-8")
    return text


def setup_logging(dir_):
    log = logging.getLogger("jobqueue")
    log.setLevel(logging.INFO)
    for h in list(log.handlers):
        log.removeHandler(h)
        h.close()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    logs = Path(dir_) / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(str(logs / "worker.log"), maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    console = logging.StreamHandler()
    for h in (file_handler, console):
        h.setFormatter(fmt)
        log.addHandler(h)
    return log


# --------------------------------------------------------------------------- worker
def run_worker(dir_=DEFAULT_DIR, poll=5.0, max_jobs=None, until_empty=False, handlers=None, log=None):
    """Jalankan worker sampai dihentikan. Mengembalikan jumlah tugas yang diproses."""
    dir_ = Path(dir_)
    dir_.mkdir(parents=True, exist_ok=True)
    log = log or setup_logging(dir_)
    db = connect(dir_ / "jobs.sqlite3")
    stop_file = dir_ / "STOP"
    if stop_file.exists():
        stop_file.unlink()
        log.info("file STOP lama dihapus karena worker dimulai")
    stopping = {"flag": False}

    def request_stop(*_):
        stopping["flag"] = True

    previous = {}
    if threading.current_thread() is threading.main_thread():
        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):  # SIGBREAK = Ctrl+Break di Windows
            sig = getattr(signal, name, None)
            if sig is not None:
                previous[sig] = signal.signal(sig, request_stop)
    try:
        return _loop(dir_, db, stop_file, stopping, poll, max_jobs, until_empty, handlers, log)
    finally:
        for sig, handler in previous.items():  # kembalikan Ctrl+C seperti semula
            signal.signal(sig, handler)
        db.close()


def _loop(dir_, db, stop_file, stopping, poll, max_jobs, until_empty, handlers, log):
    recovered = recover_stale(db)
    log.info("worker mulai; tugas dipulihkan=%d; folder=%s", recovered, dir_)
    done = 0
    while True:
        if stopping["flag"] or stop_file.exists():
            log.info("permintaan berhenti diterima; berhenti dengan aman")
            break
        if max_jobs is not None and done >= max_jobs:
            break
        recover_stale(db)
        jid = work_once(db, handlers)
        if jid is not None:
            done += 1
            row = db.execute("SELECT agent,kind,status,attempts,error FROM jobs WHERE id=?", (jid,)).fetchone()
            level = logging.INFO if row[2] in ("done", "queued") else logging.ERROR
            log.log(level, "tugas #%s %s/%s -> %s (percobaan %s) %s", jid, row[0], row[1], row[2], row[3], row[4] or "")
            write_status(dir_, db, last_job=jid)
            continue
        write_status(dir_, db)
        if until_empty:
            break
        for _ in range(max(1, int(poll * 2))):  # tidur kecil-kecil agar cepat tanggap saat STOP
            if stopping["flag"] or stop_file.exists():
                break
            time.sleep(0.5)
    write_status(dir_, db)
    build_report(dir_, db)
    log.info("worker selesai; tugas diproses=%d", done)
    return done


# --------------------------------------------------------------------------- CLI
def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(description="Antrean tugas Pixel Office (offline, tanpa biaya)")
    p.add_argument("--dir", default=str(DEFAULT_DIR), help="folder data (database, log, status)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("report")
    sub.add_parser("stop")
    sub.add_parser("run-once")
    add = sub.add_parser("enqueue")
    add.add_argument("--agent", default="kiro")
    add.add_argument("--kind", default="story_outline")
    add.add_argument("--idea", default="Bayangan yang Ingin Libur")
    add.add_argument("--key", default=None, help="kunci idempotensi (kunci sama = tidak dobel)")
    add.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    w = sub.add_parser("worker")
    w.add_argument("--poll", type=float, default=5.0)
    w.add_argument("--max-jobs", type=int, default=None)
    w.add_argument("--until-empty", action="store_true", help="berhenti setelah tidak ada tugas siap")
    args = p.parse_args(argv)

    dir_ = Path(args.dir)
    if args.cmd == "stop":
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / "STOP").write_text(iso(), encoding="utf-8")
        print("STOP dibuat; worker akan berhenti setelah tugas yang berjalan selesai")
        return 0
    if args.cmd == "worker":
        n = run_worker(dir_, poll=args.poll, max_jobs=args.max_jobs, until_empty=args.until_empty)
        print("worker selesai; tugas diproses:", n)
        return 0
    db = connect(dir_ / "jobs.sqlite3")
    try:
        if args.cmd == "init":
            print("initialized", dir_)
        elif args.cmd == "enqueue":
            print("queued", enqueue(db, args.agent, args.kind, {"idea": args.idea}, key=args.key,
                                    max_attempts=args.max_attempts))
        elif args.cmd == "run-once":
            print("processed", work_once(db))
        elif args.cmd == "status":
            print(json.dumps(counts(db)))
        elif args.cmd == "report":
            print(build_report(dir_, db))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
