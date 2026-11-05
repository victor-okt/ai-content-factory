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

WIB = timezone(timedelta(hours=7))
TREND_URL = "https://trends.google.com/trending/rss?geo=ID"
NEWS_QUERIES = ("TikTok AI animation viral", "video AI kreatif viral", "AI video trend creative")
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
    published = date_of(item.get("pubDate"), day)
    age = (datetime.fromisoformat(day).date() - datetime.fromisoformat(published).date()).days
    if age < 0 or age > 14:
        return None
    group = category(title)
    angles = {
        "object_comes_alive": "Buat karakter orisinal keluar dari benda atau kartu dengan kejutan visual.",
        "miniature_world": "Ubah benda biasa menjadi kota atau dunia mini dalam satu transisi.",
        "surreal_comedy": "Buat perubahan absurd dan lucu dengan twist di akhir.",
        "visual_transformation": "Gunakan satu perubahan visual dramatis dengan reveal singkat."
    }
    identity = title.lower().strip() + "|" + url.split("?")[0]
    uid = "TH-" + hashlib.sha256(identity.encode()).hexdigest()[:12].upper()
    score = round(((5 if group != "visual_transformation" else 4) * 30 + (3 if group == "miniature_world" else 4) * 30 + 3 * 15 + (5 if age <= 7 else 4) * 15 + 3 * 10) / 5, 1)
    return {
        "content_id": uid, "title": title, "source_url": url, "observed_at": published,
        "category": group, "concept": "Sinyal: " + title + ". " + angles[group],
        "score": score, "signal_source": "Google Trends Indonesia" if kind == "trends" else "Google News / liputan publik",
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
    ]
    results, errors, checks = [], [], []
    for kind, url in sources:
        try:
            items = rss_items(fetcher(url))
            checks.append({"source": kind, "url": url, "feed_items": len(items)})
            for item in items:
                candidate = idea_from(item, kind, day)
                if candidate:
                    results.append(candidate)
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
    status = ("partial" if errors else "ok") if current else ("error" if errors else "empty")
    payload = {
        "schema_version": 1, "status": status, "last_checked_at": stamp,
        "last_success_at": stamp if current else previous.get("last_success_at"),
        "feed_checks": checks, "errors": errors,
        "ideas": current[:20] if current else (previous.get("ideas", []) if errors else []),
        "disclaimer": "Sinyal Google Trends dan News, bukan statistik views atau viral TikTok. Skor adalah heuristik, bukan prediksi."
    }
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    seen_path.write_text(json.dumps(dict(list(seen.items())[-500:]), ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

if __name__ == "__main__":
    outcome = run()
    print(json.dumps({"status": outcome["status"], "ideas": len(outcome["ideas"]), "errors": outcome["errors"], "last_checked_at": outcome["last_checked_at"]}, ensure_ascii=False))
    if outcome["status"] == "error" and not outcome.get("last_success_at"):
        sys.exit(1)
