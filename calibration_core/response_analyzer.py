"""Shared response analysis helpers."""
from __future__ import annotations

import statistics
from typing import Any


def summarize_response(records: list[dict[str, Any]]) -> dict[str, float]:
    if not records:
        raise ValueError("records must not be empty")
    command = float(records[0]["command_velocity"])
    actuals = [float(row["measured_actual_velocity"]) for row in records]
    yaws = [float(row["yaw_drift_statistic"]) for row in records]
    mean_actual = statistics.fmean(actuals)
    tracking_error = mean_actual - command
    std_actual = statistics.stdev(actuals) if len(actuals) > 1 else 0.0
    return {
        "command_velocity": command,
        "n": len(records),
        "mean_actual_velocity": mean_actual,
        "std_actual_velocity": std_actual,
        "mean_tracking_error": tracking_error,
        "relative_tracking_error": tracking_error / command,
        "no_motion_ratio": sum(1 for value in actuals if abs(value) <= 0.02) / len(actuals),
        "mean_yaw_drift_deg": statistics.fmean(yaws),
        "response_uncertainty": std_actual,
    }
