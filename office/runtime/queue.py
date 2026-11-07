"""Persistent offline task queue for Pixel Office + VO1995. No paid AI calls."""
import argparse, json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

def utc(): return datetime.now(timezone.utc).isoformat()
def connect(path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, agent TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, result TEXT)")
    db.commit()
    return db
def enqueue(db,agent,kind,payload):
    if agent not in {"nox","kiro","miko","riku","senn","zek"}: raise ValueError("unknown agent")
    cur=db.execute("INSERT INTO jobs(agent,kind,payload,status,created_at,updated_at) VALUES(?,?,?,'queued',?,?)",(agent,kind,json.dumps(payload,ensure_ascii=False),utc(),utc()))
    db.commit();return cur.lastrowid
def work_once(db):
    row=db.execute("SELECT id,agent,kind,payload FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
    if row is None:return None
    jid,agent,kind,payload=row
    db.execute("UPDATE jobs SET status='running',attempts=attempts+1,updated_at=? WHERE id=?",(utc(),jid));db.commit()
    try:
        data=json.loads(payload)
        if kind=="story_outline":
            idea=data.get("idea","Bayangan yang Ingin Libur")
            result={"idea":idea,"hook":"Bayangan Kitsune mendadak berhenti mengikutinya.","conflict":"Kitsune berusaha membujuk bayangannya bergerak.","twist":"Bayangannya hanya ingin beristirahat bersama Kitsune.","status":"offline_template_only","requires_review":True}
        elif kind=="quality_gate":
            result={"status":"needs_human_review","checks":["real character movement","subtitle safe area","voice quality","story payoff"],"auto_publish":False}
        else:
            raise ValueError("unsupported job kind: "+kind)
        db.execute("UPDATE jobs SET status='done',result=?,updated_at=? WHERE id=?",(json.dumps(result,ensure_ascii=False),utc(),jid))
    except Exception as e:
        db.execute("UPDATE jobs SET status='failed',result=?,updated_at=? WHERE id=?",(str(e),utc(),jid))
    db.commit();return jid
def main():
    p=argparse.ArgumentParser();p.add_argument("--db",default=os.environ.get("OFFICE_DB","office-runtime/jobs.sqlite3"))
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init"); sub.add_parser("run-once"); sub.add_parser("status")
    add=sub.add_parser("enqueue");add.add_argument("--agent",default="kiro");add.add_argument("--kind",default="story_outline");add.add_argument("--idea",default="Bayangan yang Ingin Libur")
    args=p.parse_args();db=connect(args.db)
    if args.cmd=="enqueue":print("queued",enqueue(db,args.agent,args.kind,{"idea":args.idea}))
    elif args.cmd=="run-once":print("processed",work_once(db))
    elif args.cmd=="status":print(json.dumps(db.execute("SELECT status,count(*) FROM jobs GROUP BY status").fetchall()))
    else:print("initialized",args.db)
if __name__=="__main__":main()
