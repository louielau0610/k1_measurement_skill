"""Classify M19C surface-speed response regions for skill-side ranking."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

DEFAULT_STATS = Path("outputs/real_k1_validation_m19/surface_response_statistics.csv")
DEFAULT_OUTPUT = Path("outputs/real_k1_validation_m19/region_classification.csv")

DEFAULT_THRESHOLDS = {
    "no_motion_velocity_threshold": 0.02,
    "under_track_relative_threshold": 0.20,
    "over_response_relative_threshold": 0.20,
    "yaw_drift_high_threshold_deg": 5.0,
    "uncertainty_high_threshold": 0.08,
}


def f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def classify_region(row: dict[str, Any], thresholds: dict[str, float] | None = None) -> str:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    n = int(f(row.get("n")))
    no_motion_ratio = f(row.get("no_motion_ratio"))
    response_uncertainty = f(row.get("response_uncertainty"))
    mean_yaw = f(row.get("mean_yaw_drift_deg"))
    relative_error = f(row.get("relative_tracking_error"))
    if n < 3:
        return "insufficient_evidence"
    if no_motion_ratio >= 0.67:
        return "deadzone"
    if response_uncertainty > t["uncertainty_high_threshold"]:
        return "unstable"
    if mean_yaw > t["yaw_drift_high_threshold_deg"]:
        return "drift_prone"
    if relative_error <= -t["under_track_relative_threshold"]:
        return "under_track"
    if relative_error >= t["over_response_relative_threshold"]:
        return "over_response"
    return "reliable"


def risk_score(row: dict[str, Any], thresholds: dict[str, float] | None = None, weights: dict[str, float] | None = None) -> float:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    w = {"alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0, **(weights or {})}
    normalized_yaw = f(row.get("mean_yaw_drift_deg")) / t["yaw_drift_high_threshold_deg"]
    return (
        w["alpha"] * abs(f(row.get("mean_tracking_error")))
        + w["beta"] * f(row.get("response_uncertainty"))
        + w["gamma"] * f(row.get("no_motion_ratio"))
        + w["delta"] * normalized_yaw
    )


def classify_rows(rows: list[dict[str, Any]], thresholds: dict[str, float] | None = None) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        item = dict(row)
        item["region_label"] = classify_region(row, thresholds)
        item["risk_score"] = risk_score(row, thresholds)
        output.append(item)
    return output


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "surface_id",
        "command_velocity",
        "n",
        "region_label",
        "risk_score",
        "mean_actual_velocity",
        "mean_tracking_error",
        "relative_tracking_error",
        "no_motion_ratio",
        "mean_yaw_drift_deg",
        "response_uncertainty",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    rows = classify_rows(read_csv(args.stats))
    write_csv(args.output, rows)
    print(f"M19C regions classified={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
