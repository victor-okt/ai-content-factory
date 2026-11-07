"""Minimal safe, unattended office worker. This does NOT generate AI videos yet."""
import json, os, signal, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("OFFICE_DATA_DIR", "/data"))
INTERVAL = max(60, int(os.environ.get("WORKER_INTERVAL_SECONDS", "300")))
STOP = False
def stop(*_):
    global STOP
    STOP = True
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

def tick():
    ROOT.mkdir(parents=True, exist_ok=True)
    status = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "service": "pixel-office-vo1995",
        "worker": "alive",
        "story": "pending_integration",
        "animation": "pending_real_cutout_assets",
        "narration": "pending_api_access",
        "publishing": "disabled",
        "paid_api": "disabled"
    }
    tmp = ROOT / "status.tmp"
    tmp.write_text(json.dumps(status, indent=2), encoding="utf-8")
    tmp.replace(ROOT / "status.json")
    print(json.dumps(status), flush=True)

if __name__ == "__main__":
    while not STOP:
        tick()
        for _ in range(INTERVAL):
            if STOP: break
            time.sleep(1)
