"""Trend Hunter Agent 1: source-backed public signals for creative video ideas.

Google Trends / Google News are NOT TikTok view statistics. Standard library only.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from collections import Counter
from .quality import rejection, title_key, assess, ANGLES, laboratory_seeds
from .community import FEEDS, atom_items, community_idea

WIB = timezone(timedelta(hours=7))
TREND_URL = "https://trends.google.com/trending/rss?geo=ID"
# Wider editorial discovery: the previous quoted combinations returned mostly
# unrelated tutorials and zero qualifying story signals on 2026-11-05.
# These searches remain public news signals, NOT verified TikTok trends.
NEWS_QUERIES = (
    'miniature animation video',
    'stop motion toy animation',
    'animated short film fantasy',
    'surreal animation video',
    'figurine comes alive animation',
    'animasi 3d kucing video pendek',
    'kartu animasi video pendek'
)
BAD = re.compile(r"\b(meninggal|tewas|bunuh|pembunuhan|bencana|gempa|banjir|perang|korban|kecelakaan|tragedi|politik|pemilu|korupsi|suicide|death|war|disaster|crash|election|murder|abuse)\b", re.I)
TOPIC = re.compile(r"\b(anime|animasi|animation|game|gaming|kartu|card|miniatur|miniature|toy|robot|gadget|kucing|cat|dog|food|makanan|viral|tiktok|ai video|video ai|creator|creative|cosplay|fantasy|meme|figure|kartun|video|3d)\b", re.I)

def now():
    return datetime.now(WIB)

def clean(value):
    value = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TrendHunter/1.0)", "Accept": "application/rss+xml,application/xml,text/xml"})
    with urllib.request.urlopen(request, timeout=18) as response:
        content = response.read(1_500_001)
    if len(content) > 1_500_000:
        raise ValueError("Feed too large")
    return content

def rss_items(payload):
    root = ET.fromstring(payload)
    items = []
    for item in root.findall(".//channel/item"):
        row = {}
        for child in item:
            key = child.tag.split("}")[-1]
            if key in ("title", "link", "pubDate", "description"):
                row[key] = clean(child.text)
        if row.get("title") and row.get("link"):
            items.append(row)
    return items

def date_of(value, fallback):
    if not value:
        return fallback
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(WIB).date().isoformat()
    except (ValueError, TypeError, OverflowError):
        return fallback

def category(title):
    if re.search(r"\b(kartu|card|game|anime|figure|toy|cosplay)\b", title, re.I):
        return "object_comes_alive"
    if re.search(r"\b(mini|miniature|miniatur|tiny)\b", title, re.I):
        return "miniature_world"
    if re.search(r"\b(meme|lucu|funny|comedy)\b", title, re.I):
        return "surreal_comedy"
    return "visual_transformation"

def idea_from(item, kind, day):
    title = clean(item.get("title", ""))[:170]
    url = item.get("link", "")
    if not title or not url.startswith(("https://", "http://")) or BAD.search(title) or not TOPIC.search(title):
        return None
    if rejection(title, kind):
        return None
    published = date_of(item.get("pubDate"), day)
    age = (datetime.fromisoformat(day).date() - datetime.fromisoformat(published).date()).days
    if age < 0 or age > 10:
        return None
    group = category(title)
    angles = {
        "object_comes_alive": "Buat karakter orisinal keluar dari benda atau kartu dengan kejutan visual.",
        "miniature_world": "Ubah benda biasa menjadi kota atau dunia mini dalam satu transisi.",
        "surreal_comedy": "Buat perubahan absurd dan lucu dengan twist di akhir.",
        "visual_transformation": "Gunakan satu perubahan visual dramatis dengan reveal singkat."
    }
    uid = title_key(title, group)
    score, breakdown = assess(title, group, kind, age)
    return {
        "content_id": uid, "title": title, "source_url": url, "observed_at": published,
        "category": group, "concept": "Inspirasi dari sinyal publik: " + title + ". " + ANGLES[group],
        "score": score, "score_label": "Kecocokan konsep, bukan prediksi viral",
        "score_breakdown": breakdown,
        "confidence": "rendah" if kind == "news" else "rendah-menengah",
        "why_recommended": ["Topik sesuai format hiburan visual", "Bisa dibuat sebagai video pendek", "Bukan data analytics TikTok"],
        "approval_status": "menunggu_persetujuan",
        "creative_brief": {"idea_id": uid, "duration_seconds": 12, "ratio": "9:16", "angle": ANGLES[group], "source_url": url},
        "signal_source": "Google Trends Indonesia" if kind == "trends" else "Google News / liputan publik",
        "evidence_label": "Pencarian Google, bukan statistik video TikTok." if kind == "trends" else "Liputan publik, bukan bukti video viral TikTok.",
        "metrics_verified": False, "next_agent": "creative_director"
    }

def run(fetcher=fetch, when=None, root="."):
    clock = when or now()
    day = clock.date().isoformat()
    root = Path(root)
    latest_path = root / "office/data/latest.json"
    seen_path = root / "office/data/seen.json"
    try:
        previous = json.loads(latest_path.read_text("utf-8"))
    except (OSError, ValueError):
        previous = {}
    try:
        seen = json.loads(seen_path.read_text("utf-8"))
    except (OSError, ValueError):
        seen = {}
    if not isinstance(seen, dict):
        seen = {}
    sources = [("trends", TREND_URL)] + [
        ("news", "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=id&gl=ID&ceid=ID:id")
        for q in NEWS_QUERIES
    ] + list(FEEDS)
    results, errors, checks, rejected = [], [], [], Counter()
    for kind, url in sources:
        try:
            items = atom_items(fetcher(url)) if kind == "community" else rss_items(fetcher(url))
            accepted = 0
            for item in items:
                candidate = community_idea(item, day) if kind == "community" else idea_from(item, kind, day)
                if candidate:
                    results.append(candidate)
                    accepted += 1
                else:
                    rejected["komunitas_tidak_lolos" if kind == "community" else (rejection(item.get("title",""),kind) or "lainnya")] += 1
            checks.append({"source": kind, "url": url, "feed_items": len(items), "accepted": accepted})
        except (OSError, ValueError, ET.ParseError, TimeoutError) as exc:
            errors.append(kind + ": " + type(exc).__name__ + " " + str(exc)[:120])
    unique = {row["content_id"]: row for row in results}
    current = list(unique.values())
    for item in current:
        item["first_seen_at"] = seen.get(item["content_id"], day)
        item["seen_before"] = item["content_id"] in seen
        seen[item["content_id"]] = item["first_seen_at"]
    current.sort(key=lambda item: (-item["score"], item["seen_before"], item["title"]))
    stamp = clock.isoformat(timespec="seconds")
    status = ("partial" if errors else "ok") if current else ("partial" if errors and checks else ("error" if errors else "empty"))
    previous_ideas = previous.get("ideas", []) if isinstance(previous.get("ideas"), list) else []
    if not current and errors and previous_ideas:
        status = "stale"
    payload = {
        "schema_version": 1, "agent_version": "1.3", "status": status, "last_checked_at": stamp,
        "last_success_at": stamp if current else previous.get("last_success_at"),
        "feed_checks": checks, "errors": errors,
        "quality_control": {"items_scanned": sum(x["feed_items"] for x in checks),
                            "qualified_unique": len(current), "rejected_by_reason": dict(sorted(rejected.items()))},
        "ideas": current[:12] if current else (previous_ideas if errors else []),
        "creative_seeds": laboratory_seeds() if not current and not previous_ideas else [],
        "handoff": {"next_agent": "creative_director", "approval": "pending",
                    "top_candidate_ids": [i["content_id"] for i in current[:3]],
                    "lab_candidate_ids": [i["content_id"] for i in laboratory_seeds()] if not current else [],
                    "note": "Agent 2 belum dijalankan, perlu persetujuan pengguna."},
        "disclaimer": "Sumber publik Google Trends, berita dan komunitas AI video. Bukan analytics TikTok. Skor kecocokan kreatif bukan peluang viral atau penghasilan."
    }
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    seen_path.write_text(json.dumps(dict(list(seen.items())[-500:]), ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

if __name__ == "__main__":
    outcome = run()
    print(json.dumps({"status": outcome["status"], "ideas": len(outcome["ideas"]), "errors": outcome["errors"], "last_checked_at": outcome["last_checked_at"]}, ensure_ascii=False))
    if outcome["status"] in ("error","stale") and not outcome.get("last_success_at"):
        sys.exit(1)
