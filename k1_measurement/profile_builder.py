"""Profile builder skeleton for downstream measurement outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_measurement_profile(
    environment: dict[str, str],
    speed_points: list[dict[str, Any]],
    confidence: str = "low",
) -> dict[str, Any]:
    """Build a measurement-only profile for downstream consumers."""

    return {
        "schema_version": "0.1.0",
        "profile_type": "forward_velocity_measurement",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "robot": "Booster K1",
        "environment": environment,
        "confidence": confidence,
        "valid_speed_range_mps": {
            "min": min((point["vx_cmd"] for point in speed_points), default=None),
            "max": max((point["vx_cmd"] for point in speed_points), default=None),
        },
        "speed_points": speed_points,
        "downstream_warnings": [
            "Do not assume high confidence by default.",
            "Check environment match before use.",
            "Avoid extrapolation outside valid_speed_range_mps.",
        ],
    }
