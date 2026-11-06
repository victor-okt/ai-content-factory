"""Fail-closed Credit Guard. No provider calls, billing, or credentials."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date

DAILY_BUDGET_IDR = 0
MAX_ATTEMPTS_PER_VIDEO = 1
SIMULATION_ONLY = True


@dataclass(frozen=True)
class Decision:
    allowed: bool
    mode: str
    reason: str
    daily_budget_idr: int
    max_attempts_per_video: int
    simulated_cost_idr: int
    actual_spend_idr: int = 0


def authorize_video_attempt(*, video_id: str, attempt_number: int,
                            estimated_cost_idr: int, spent_today_idr: int = 0,
                            today: date | None = None) -> Decision:
    """Return a dry-run decision, never permission to invoke a paid provider.

    No caller can override the zero budget or simulation-only policy.
    """
    if not isinstance(video_id, str) or not video_id.strip():
        raise ValueError("video_id must be a non-empty string")
    for name, value in (("attempt_number", attempt_number),
                        ("estimated_cost_idr", estimated_cost_idr),
                        ("spent_today_idr", spent_today_idr)):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if attempt_number < 1:
        raise ValueError("attempt_number must be at least 1")
    if today is not None and not isinstance(today, date):
        raise ValueError("today must be a date")
    if attempt_number > MAX_ATTEMPTS_PER_VIDEO:
        reason = "attempt_limit_exceeded"
    elif estimated_cost_idr + spent_today_idr > DAILY_BUDGET_IDR:
        reason = "zero_budget_blocks_paid_generation"
    else:
        reason = "simulation_only_no_provider_execution"
    return Decision(
        allowed=False, mode="simulation", reason=reason,
        daily_budget_idr=DAILY_BUDGET_IDR,
        max_attempts_per_video=MAX_ATTEMPTS_PER_VIDEO,
        simulated_cost_idr=estimated_cost_idr,
    )


def public_policy() -> dict:
    """Safe metadata for a public dashboard; no credentials or API calls."""
    decision = authorize_video_attempt(
        video_id="example", attempt_number=1, estimated_cost_idr=0
    )
    return {
        "mode": "simulation",
        "daily_budget_idr": DAILY_BUDGET_IDR,
        "max_attempts_per_video": MAX_ATTEMPTS_PER_VIDEO,
        "paid_generation_allowed": decision.allowed,
        "actual_spend_idr": 0,
        "approval_required_to_change_policy": True,
    }
