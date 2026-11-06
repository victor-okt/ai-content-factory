"""Open-source video production plan. Pure offline handoff; no GPU or API calls.

Targets ComfyUI-compatible local/self-hosted runners. A 30-second video is
assembled from six independently generated 5-second clips, not a single
unverified 30-second model generation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

CLIP_SECONDS = 5
TARGET_SECONDS = 30
CLIP_COUNT = TARGET_SECONDS // CLIP_SECONDS
BACKEND = "comfyui_self_hosted"
MODEL_CANDIDATES = ("wan2.2-ti2v-5b", "hunyuanvideo-1.5")
RENDER_ENABLED = False


def make_render_plan(job: Mapping) -> dict:
    if not isinstance(job, Mapping):
        raise ValueError("job must be a mapping")
    content_id = job.get("content_id")
    producer = job.get("video_producer")
    if not isinstance(content_id, str) or not content_id.strip():
        raise ValueError("content_id is required")
    if not isinstance(producer, Mapping):
        raise ValueError("video_producer is required")
    prompt = producer.get("video_prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("video_prompt is required")
    shots = []
    for index in range(CLIP_COUNT):
        shots.append({
            "clip_index": index + 1,
            "start_second": index * CLIP_SECONDS,
            "end_second": (index + 1) * CLIP_SECONDS,
            "duration_seconds": CLIP_SECONDS,
            "prompt": prompt,
            "status": "planned_not_rendered",
            "rendered_file": None,
        })
    return {
        "schema_version": 1,
        "content_id": content_id,
        "target_duration_seconds": TARGET_SECONDS,
        "backend": BACKEND,
        "model_candidates": list(MODEL_CANDIDATES),
        "render_enabled": RENDER_ENABLED,
        "requires_gpu_runner": True,
        "requires_workflow_configuration": True,
        "requires_owner_approval_for_costs": True,
        "clips": shots,
        "assembly": {
            "tool": "ffmpeg",
            "strategy": "concat_six_clips_then_add_original_audio",
            "status": "not_executed",
        },
    }
