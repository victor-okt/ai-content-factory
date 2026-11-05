#!/usr/bin/env python3
"""Agent 01 / Trend Hunter: public Google Search trend signals for Indonesia.

No API key, paid model, login, or fake TikTok view metrics.
Run: python scripts/trend_hunter.py
Test offline: python scripts/trend_hunter.py --fixture tests/trends.xml --output /tmp/trends.json
"""
import argparse
import hashlib
import json
import math
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

FEED = "https://trends.google.com/trending/rss?geo=ID"
LOCAL_TIME = ZoneInfo("Asia/Jakarta")
SENSITIVE = ("tewas", "meninggal", "pembunuhan", "bunuh diri", "kecelakaan",
             "perang", "bencana", "gempa", "pemerkosaan", "korban jiwa")
TOPICS = {
    "game": ("game", "gaming", "roblox", "mobile legends", "mlbb", "minecraft", "pokemon", "pokémon", "genshin"),
    "anime": ("anime", "manga", "one piece", "naruto", "demon slayer", "jujutsu", "hunter x hunter"),
    "film": ("film", "movie", "series", "netflix", "cinema", "drama", "trailer"),
    "tech": ("ai", "gadget", "iphone", "android", "teknologi", "chatgpt"),
    "sport": ("sepak bola", "persib", "liga", "football", "vs ", "badminton", "tenis"),
    "music": ("lagu", "musik", "konser", "album", "singer"),
}

def child_text(item, suffix):
    for element in item.iter():
        if element.tag.rsplit("}", 1)[-1] == suffix and element.text:
            return element.text.strip()
    return ""

def volume(raw):
    val = (raw or "").strip().lower().replace("\u00a0", " ")
    m = re.search(r"([\d.,]+)\s*(juta|million|rb|ribu|k|m)?", val)
    if not m:
        return None
    number, unit = m.groups()
    number = number.replace(",", ".") if "." not in number else number.replace(",", "")
    try:
        v = float(number)
    except ValueError:
        return None
    return int(v * {"juta": 1000000, "million": 1000000,
                    "rb": 1000, "ribu": 1000, "k": 1000, "m": 1000000}.get(unit or "", 1))

def topic(title):
    name = title.casefold()
    for label, words in TOPICS.items():
        if any(word in name for word in words):
            return label
    return "general"

def creative_brief(title, category):
    templates = {
        "game": "Buat eksperimen visual lucu yang mengubah benda nyata menjadi elemen game, lalu tutup dengan kejutan.",
        "anime": "Pakai karakter ORISINAL dan transisi sinematik; hindari memakai aset karakter berhak cipta tanpa izin.",
        "film": "Buat sketsa 3 adegan yang memparodikan format trailer secara orisinal.",
        "tech": "Tampilkan demonstrasi sebelum/sesudah atau eksperimen visual yang bisa diverifikasi.",
        "sport": "Buat permainan tebakan atau reaksi penonton, bukan mengklaim hasil pertandingan tanpa cek fakta.",
        "music": "Buat transisi visual ritmis dengan audio yang punya izin penggunaan.",
        "general": "Hubungkan topik dengan situasi keseharian, mulai dengan kejutan visual pada 2 detik pertama.",
    }
    return {
        "hook": f"Kenapa semua orang tiba-tiba membahas '{title}'?",
        "concept": templates[category],
        "warning": "Sinyal berasal dari Google Search, BUKAN bukti sedang viral di TikTok. Verifikasi sebelum produksi.",
    }

def parse(xml_bytes, now):
    root = ET.fromstring(xml_bytes)
    candidates = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or any(word in title.casefold() for word in SENSITIVE):
            continue
        raw_traffic = child_text(item, "approx_traffic")
        searches = volume(raw_traffic)
        category = topic(title)
        score = min(99, round(35 + min(34, math.log10(max(searches or 1, 1)) * 8)
                              + (20 if category in ("anime", "game", "film", "tech") else 8 if category != "general" else 0)))
        published = item.findtext("pubDate") or ""
        try:
            observation_time = parsedate_to_datetime(published).astimezone(LOCAL_TIME).isoformat()
        except (ValueError, TypeError, OverflowError):
            observation_time = now.isoformat()
        key = re.sub(r"\s+", " ", title).casefold()
        brief = creative_brief(title, category)
        candidates.append({
            "id": "TH-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12].upper(),
            "title": title,
            "category": category,
            "score": score,
            "score_type": "heuristic_editorial_not_platform_metric",
            "estimated_google_searches": searches,
            "google_traffic_label": raw_traffic or None,
            "source_url": link if link.startswith("https://") else FEED,
            "source": "Google Trends RSS - Indonesia",
            "published_at": observation_time,
            "observed_at": now.isoformat(),
            "verified_google_trend_signal": True,
            "verified_tiktok_views": False,
            "next_agent": "creative_director",
            **brief,
        })
    seen = set()
    result = []
    for item in sorted(candidates, key=lambda x: x["score"], reverse=True):
        key = re.sub(r"[^a-z0-9]+", "", item["title"].casefold())
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:12]

def run():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", help="Offline test RSS file")
    p.add_argument("--output", default="data/trends.json")
    args = p.parse_args()
    now = datetime.now(timezone.utc).astimezone(LOCAL_TIME)
    if args.fixture:
        raw = Path(args.fixture).read_bytes()
    else:
        request = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (compatible; TrendHunter/1.0)"})
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read(2_000_000)
    items = parse(raw, now)
    if not items:
        raise RuntimeError("Feed kosong atau tidak mengandung item valid; hasil sebelumnya dipertahankan.")
    payload = {
        "agent": "Trend Hunter", "status": "live" if not args.fixture else "fixture_test",
        "generated_at": now.isoformat(), "timezone": "Asia/Jakarta",
        "source": FEED, "signal_type": "Google Search interest, NOT TikTok platform metrics",
        "verified_tiktok_metrics": False, "count": len(items), "items": items,
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(items)} ideas saved at {destination}")

if __name__ == "__main__":
    run()
