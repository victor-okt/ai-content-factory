"""Content Factory pipeline (offline/free tier).

Generates deterministic *drafts* and preproduction plans from Agent 1's
source-backed ideas. It does NOT call a generative AI model, render footage,
publish TikTok posts, or fetch TikTok analytics.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from factory.credit_guard import public_policy

WIB = timezone(timedelta(hours=7))
MAX_JOBS = 3

AGENTS = (
    ("nova", "Trend Hunter", "Membaca sinyal publik, memberi label sumber"),
    ("kai", "Creative Director", "Menyiapkan hook, skrip, dan storyboard berbasis template"),
    ("mira", "Visual Creator", "Menyiapkan prompt visual untuk generator yang dipilih"),
    ("rio", "Video Producer", "Menyiapkan timeline dan shot list, tanpa merender video"),
    ("sora", "Content Publisher", "Menyiapkan caption dan metadata draft, tanpa posting"),
    ("dex", "Performance Analyst", "Memeriksa pipeline; analytics platform belum terhubung"),
)

CATEGORY = {
    "object_comes_alive": {
        "hook": "Benda kecil ini seharusnya tidak bisa bergerak...",
        "payoff": "Karakter orisinal keluar dari benda dan bereaksi dengan lingkungan.",
        "camera": "macro close-up, depth of field, handheld micro-motion",
        "mood": "playful supernatural realism",
    },
    "miniature_world": {
        "hook": "Ada dunia rahasia di atas meja ini.",
        "payoff": "Benda sehari-hari berubah menjadi kota mini yang hidup.",
        "camera": "macro dolly-in, tilt-shift, miniature depth of field",
        "mood": "whimsical miniature wonder",
    },
    "surreal_comedy": {
        "hook": "Tunggu... kenapa benda itu melakukan ini?",
        "payoff": "Perubahan absurd diakhiri dengan reaksi komedi yang mudah dipahami.",
        "camera": "medium static framing with a fast reaction close-up",
        "mood": "lighthearted absurd comedy",
    },
    "visual_transformation": {
        "hook": "Coba perhatikan perubahan dalam tiga detik...",
        "payoff": "Sebuah benda atau suasana berubah menjadi dunia visual orisinal.",
        "camera": "slow push-in, dramatic match cut, reveal",
        "mood": "surprising cinematic fantasy",
    },
}


def clean_text(value, limit=300):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:limit]


def safe_link(value):
    if not isinstance(value, str) or len(value) > 1500:
        return ""
    try:
        parts = urlsplit(value)
        if (parts.scheme not in ("http", "https") or not parts.netloc
                or not parts.hostname or parts.username is not None
                or parts.password is not None):
            return ""
        # Force port parsing: urlsplit accepts invalid and out-of-range ports.
        _ = parts.port
        # Backslashes, whitespace and controls can be interpreted differently
        # by browsers, proxies and downstream consumers.
        if any(char.isspace() or ord(char) < 32 or char == chr(92) for char in value):
            return ""
    except ValueError:
        return ""
    return value


def safe_score(value):
    """Keep only finite numeric heuristic scores; never accept bool or strings."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except (OverflowError, TypeError, ValueError):
        return None


def agent_statuses(jobs, mode):
    has_jobs = bool(jobs)
    return [
        {"id": "nova", "name": "Nova", "role": AGENTS[0][1],
         "status": "research_available" if mode == "public_research" else ("lab_only" if has_jobs else "no_candidates"),
         "detail": "Sumber publik tersimpan" if mode == "public_research" else "Belum ada tren yang memenuhi filter; mode eksperimen" if has_jobs else "Belum ada bahan"},
        {"id": "kai", "name": "Kai", "role": AGENTS[1][1],
         "status": "draft_ready" if has_jobs else "waiting",
         "detail": "Hook, skrip, dan storyboard template tersedia" if has_jobs else "Menunggu ide dari Nova"},
        {"id": "mira", "name": "Mira", "role": AGENTS[2][1],
         "status": "prompt_ready" if has_jobs else "waiting",
         "detail": "Prompt gambar siap; rendering memerlukan model dan izin biaya" if has_jobs else "Menunggu brief"},
        {"id": "rio", "name": "Rio", "role": AGENTS[3][1],
         "status": "render_blocked" if has_jobs else "waiting",
         "detail": "Timeline siap; belum ada koneksi generator video dan kredit"},
        {"id": "sora", "name": "Sora", "role": AGENTS[4][1],
         "status": "publish_blocked" if has_jobs else "waiting",
         "detail": "Caption draft siap; publikasi memerlukan akun serta persetujuan"},
        {"id": "dex", "name": "Dex", "role": AGENTS[5][1],
         "status": "internal_report_only",
         "detail": "Hanya menghitung status workflow; statistik TikTok belum terhubung"},
    ]


def build_job(idea, mode):
    uid = clean_text(idea.get("content_id"), 80)
    title = clean_text(idea.get("title"), 170)
    if not uid or not title:
        return None
    category = idea.get("category")
    pattern = CATEGORY.get(category, CATEGORY["visual_transformation"])
    source = safe_link(idea.get("source_url"))
    if mode == "public_research" and not source:
        return None
    lab = mode != "public_research"
    angle = clean_text(idea.get("concept"), 300)
    hook = pattern["hook"]
    payoff = pattern["payoff"]
    scenes = [
        {"shot": 1, "seconds": [0, 2], "description": "Close-up objek pembuka dan petunjuk perubahan.", "narration": hook},
        {"shot": 2, "seconds": [2, 8], "description": "Tunjukkan perubahan visual orisinal yang jelas dan sinematik.", "narration": "Fokus pada aksi visual, tanpa penjelasan panjang."},
        {"shot": 3, "seconds": [8, 12], "description": payoff, "narration": "Akhiri dengan twist yang bisa di-loop."},
    ]
    prompt_base = (
        "Original cinematic vertical 9:16, 12-second concept. "
        + pattern["mood"] + ", " + pattern["camera"]
        + ". Visual subject inspired by a public topic but redesigned as a fully original "
          "character, world and composition. Never copy a named artist, copyrighted footage, "
          "brand logo, or recognizable existing character. Clean lighting, stable anatomy, "
          "consistent objects, no watermark, no text. Subject direction: " + payoff
    )
    return {
        "content_id": uid, "title": title, "origin": "IDE LAB / belum terverifikasi" if lab else "REFERENSI PUBLIK / bukan data TikTok",
        "source_type": "editorial_seed" if lab else clean_text(idea.get("source_type") or idea.get("signal_source"), 100),
        "source_url": "" if lab else source, "score": None if lab else safe_score(idea.get("score")),
        "metrics_verified": False, "inspiration": angle,
        "creative_director": {
            "method": "template_free_no_llm", "status": "draft",
            "hook": hook, "big_idea": payoff,
            "storyboard": scenes, "duration_seconds": 12, "format": "9:16",
            "originality": "Hasil harus berupa karya orisinal; sumber hanya inspirasi, bukan untuk ditiru.",
        },
        "visual_creator": {
            "status": "prompt_ready_not_rendered", "image_prompt": prompt_base,
            "reference_frames": [f"Frame {s['shot']}: {s['description']}" for s in scenes],
            "character_consistency": "Gunakan karakter dan wardrobe original yang identik sepanjang adegan.",
            "rendered_images": [],
        },
        "video_producer": {
            "status": "render_blocked", "duration_seconds": 12,
            "shot_timeline": scenes,
            "video_prompt": prompt_base + " Natural continuous motion, engaging first two seconds.",
            "editing_notes": "Utamakan visual storytelling, sound design orisinal, dan looping ending.",
            "rendered_video_url": "",
            "blocker": "Perlu provider video, koneksi akun, kredit, dan batas biaya.",
        },
        "publisher": {
            "status": "draft_not_published",
            "caption_draft": f"Kalau {title.lower()} bisa berubah jadi nyata... kamu bakal ngapain? 👀 #AIVideo #VisualStory #ShortFilm",
            "posting_format": "9:16 vertical short",
            "published_url": "",
            "blocker": "Perlu izin pengguna dan koneksi akun TikTok/Shopee bila publikasi diaktifkan.",
        },
        "analyst": {
            "status": "waiting_platform_analytics", "platform_views": None,
            "retention": None, "revenue": None,
            "blocker": "Belum tersedia koneksi data analytics TikTok.",
        },
        "approval": {"creative_draft": "auto_generated_unreviewed", "render": "requires_access_and_budget",
                     "publish": "requires_user_approval"},
        "external_actions": {"image_generation": False, "video_generation": False, "posting": False},
    }


def build_factory(report, clock=None):
    if not isinstance(report, dict):
        raise ValueError("Agent 1 report must be a JSON object")
    sourced = report.get("ideas", [])
    seeds = report.get("creative_seeds", [])
    if not isinstance(sourced, list) or not isinstance(seeds, list):
        raise ValueError("Agent 1 ideas must be JSON arrays")
    valid_public = [item for item in sourced if isinstance(item, dict) and safe_link(item.get("source_url"))]
    mode = "public_research" if valid_public else ("editorial_lab" if seeds else "no_ideas")
    incoming = valid_public if valid_public else [x for x in seeds if isinstance(x, dict)]
    unique, jobs = set(), []
    for idea in incoming:
        job = build_job(idea, mode)
        if job is None or job["content_id"] in unique:
            continue
        jobs.append(job)
        unique.add(job["content_id"])
        if len(jobs) >= MAX_JOBS:
            break
    if not jobs:
        mode = "no_ideas"
    clock = clock or datetime.now(WIB)
    return {
        "schema_version": 1, "pipeline_version": "0.1",
        "generated_at": clock.isoformat(timespec="seconds"),
        "agent_1_checked_at": report.get("last_checked_at"),
        "mode": mode, "draft_count": len(jobs),
        "agents": agent_statuses(jobs, mode), "jobs": jobs,
        "quality_note": "Skrip dan prompt adalah template otomatis, bukan AI generatif. "
                        "Referensi publik dan ide lab dibedakan; belum ada render atau posting.",
        "credit_guard": public_policy(),
        "cost": {"estimate": "Rp0 untuk template & perencanaan", "spent_by_pipeline": 0,
                 "paid_services_called": False},
    }


def run(root="."):
    root = Path(root)
    agent1 = root / "office/data/latest.json"
    if not agent1.exists():
        raise FileNotFoundError(f"Agent 1 report not found: {agent1}")
    raw = json.loads(agent1.read_text(encoding="utf-8"))
    factory = build_factory(raw)
    path = root / "office/data/factory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(factory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return factory


if __name__ == "__main__":
    status = run()
    print(json.dumps({"mode": status["mode"], "drafts": status["draft_count"],
                      "agents": {agent["name"]: agent["status"] for agent in status["agents"]}},
                     ensure_ascii=False))
