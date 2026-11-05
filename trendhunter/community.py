"""Optional public AI-video community discovery, not TikTok engagement data.

Parses Reddit's public Atom RSS feed. No API key, account or scraping bypass.
If a feed blocks access, Agent 1 continues with its other sources.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from html import unescape

# One focused source; avoid extra requests and Reddit rate limiting.
FEEDS = (
    ("community", "https://www.reddit.com/r/aivideos/new/.rss"),
)
ATOM = "{http://www.w3.org/2005/Atom}"
EXCLUDE = re.compile(
    r"\b(how do|how to|tutorial|help|looking for|which ai|which tool|"
    r"question|pricing|price|free ai|please help|need help|"
    r"feedback|giveaway|discount|prompt|prompts|course|kursus|"
    r"subscription|plan|got myself|trailer|remake|my first|first short film|" 
    r"cara membuat|software|app review|subscription)\b", re.I
)
UNSAFE = re.compile(
    r"\b(gore|death|suicide|abuse|murder|murdered|killed|"
    r"tragedy|tragedi|kecelakaan|bunuh|tewas|meninggal|"
    r"pembunuhan|kekerasan|terror|fireworks?|explosive|bomb|grenade)\b", re.I
)
VISUAL = re.compile(
    r"\b(animation|animated|animasi|anime|fantasy|fantasi|miniature|"
    r"toy|figure|character|characters|creature|surreal|cartoon|"
    r"stop motion|3d|cat|dog|robot|world|sci.fi|sci fi|dragon|wolf|viking|alien|spaceship|"
    r"monster|cute|horror|funny|comedy|trailer|magic)\b", re.I
)

def atom_items(payload):
    root = ET.fromstring(payload)
    items = []
    for entry in root.findall(ATOM + "entry"):
        title = (entry.findtext(ATOM + "title") or "").strip()
        published = entry.findtext(ATOM + "published") or entry.findtext(ATOM + "updated") or ""
        link = next((el.get("href", "") for el in entry.findall(ATOM + "link") if el.get("href")), "")
        html = entry.findtext(ATOM + "content") or ""
        # Community posts must link to playable video/media, rather than questions.
        is_video = any(s in html.lower() for s in ("v.redd.it/", "youtube.com/watch", "youtu.be/", "streamable.com/"))
        if title and link:
            items.append({"title": unescape(title), "link": link,
                          "published": published, "has_video": is_video})
    return items

def community_idea(item, day):
    title = re.sub(r"\s+", " ", item.get("title", "")).strip()[:160]
    link = item.get("link", "")
    if not title or not link.startswith("https://www.reddit.com/r/"):
        return None
    if len(title) < 12 or len(title.split()) < 2:
        return None
    if EXCLUDE.search(title) or UNSAFE.search(title) or not item.get("has_video"):
        return None
    # A video link is real evidence of an upload, not evidence of virality.
    if not VISUAL.search(title):
        return None
    try:
        timestamp = datetime.fromisoformat(item.get("published", "").replace("Z", "+00:00"))
        if not timestamp.tzinfo:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = (date.fromisoformat(day) - timestamp.date()).days
    except (ValueError, TypeError):
        return None
    if age < 0 or age > 7:
        return None
    lower = title.lower()
    if re.search(r"miniature|tiny|world|diorama", lower):
        group, angle = "miniature_world", "Buat transisi benda kecil menjadi dunia mini dengan satu reveal."
    elif re.search(r"toy|figure|character|creature|monster|robot", lower):
        group, angle = "object_comes_alive", "Buat karakter orisinal keluar dari objek, lalu bergerak di dunia nyata."
    elif re.search(r"funny|comedy|surreal|cat|dog|cute", lower):
        group, angle = "surreal_comedy", "Bangun kejutan visual yang lucu dan mudah dimengerti tanpa dialog."
    else:
        group, angle = "visual_transformation", "Uji satu perubahan visual yang kuat dalam 8–15 detik."
    item_id = re.search(r"/comments/([a-z0-9]+)/", link)
    uid = "COMM-" + (item_id.group(1).upper() if item_id else hashlib.sha256(link.encode()).hexdigest()[:10].upper())
    score = min(85, 55 + (12 if group != "visual_transformation" else 6) + (12 if age < 3 else 5))
    return {
        "content_id": uid, "title": title, "source_url": link,
        "observed_at": timestamp.date().isoformat(), "category": group,
        "concept": "Contoh unggahan video komunitas: " + title + ". Inspirasi orisinal: " + angle,
        "score": score, "score_label": "Kecocokan konsep, bukan tingkat viral",
        "score_breakdown": {"relevance": score, "visual_hook": 0, "freshness": 0, "source": 0},
        "confidence": "rendah", "why_recommended": [
            "Ada tautan unggahan video di komunitas AI video",
            "Judul sesuai inspirasi hiburan visual",
            "Tidak ada metrik views TikTok terverifikasi"
        ],
        "source_type": "community_post",
        "signal_source": "Komunitas AI Video Reddit",
        "evidence_label": "Posting komunitas; bukan bukti viral atau statistik TikTok",
        "metrics_verified": False, "approval_status": "menunggu_persetujuan",
        "creative_brief": {
            "idea_id": uid, "duration_seconds": 12, "ratio": "9:16",
            "angle": angle, "source_url": link,
            "guidance": "Buat karya orisinal; jangan menyalin footage atau desain milik pembuat asal."
        }, "next_agent": "creative_director"
    }
