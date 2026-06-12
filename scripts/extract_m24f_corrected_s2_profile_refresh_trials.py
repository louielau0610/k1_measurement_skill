"""Corrected M24-F extraction for the clean M24-B S2 profile refresh session.

Uses command-phase timing from session metadata and excludes the first/last
second of the command phase by default. It does not use idle/stop time for
velocity and does not overwrite the original M24-B/M24-C extraction outputs.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SESSION = Path("data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358")
FIELDS = [
    "trial_id",
    "refresh_group_id",
    "surface",
    "command_velocity_mps",
    "desired_velocity_mps",
    "measured_actual_velocity_mps",
    "tracking_error_mps",
    "yaw_drift_deg",
    "imu_yaw_drift_deg",
    "forward_distance_m",
    "duration_sec",
    "window_start_sec",
    "window_end_sec",
    "n_samples",
    "extraction_status",
    "invalid_reason",
    "state_log_path",
    "physical_run_status",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Correct M24-B S2 profile refresh extraction.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--trim-sec", type=float, default=1.0)
    args = parser.parse_args(argv)
    summary = extract_session(args.session_dir, args.trim_sec)
    print(f"M24-F corrected extraction rows: {summary['corrected_extracted_count']}")
    print(f"Output: {args.session_dir / 'corrected_extracted_results.csv'}")
    return 0 if summary["invalid_count"] == 0 else 1


def extract_session(session_dir: Path, trim_sec: float = 1.0) -> dict[str, Any]:
    metadata = read_json(session_dir / "session_metadata.json")
    timing = metadata.get("timing", {})
    idle_sec = float(timing.get("idle_sec", 2.0))
    command_sec = float(timing.get("command_sec", 6.0))
    window_start = idle_sec + trim_sec
    window_end = idle_sec + command_sec - trim_sec
    records = read_csv(session_dir / "trial_records.csv")
    results = []
    for record in records:
        log_path = session_dir / "state_logs" / f"{record['trial_id']}.csv"
        results.append(extract_trial(record, log_path, window_start, window_end))

    output = session_dir / "corrected_extracted_results.csv"
    write_csv(output, results, FIELDS)
    invalid = [row for row in results if row["extraction_status"] != "ok"]
    summary = {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "session_id": metadata.get("session_id", session_dir.name),
        "session_dir": str(session_dir),
        "method": "command_phase_forward_projection_trimmed",
        "idle_sec": idle_sec,
        "command_sec": command_sec,
        "trim_sec": trim_sec,
        "window_start_sec": window_start,
        "window_end_sec": window_end,
        "corrected_extracted_count": len(results),
        "invalid_count": len(invalid),
        "invalid_trial_ids": [row["trial_id"] for row in invalid],
        "original_faulty_extraction_used": False,
        "gold_profile_overwritten": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "claim_boundary": "corrected extraction only; no profile adoption or compensation improvement claim",
    }
    (session_dir / "corrected_extraction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (session_dir / "corrected_extraction_report.md").write_text(build_report(summary, results), encoding="utf-8")
    return summary


def extract_trial(record: dict[str, str], log_path: Path, window_start: float, window_end: float) -> dict[str, Any]:
    base = {
        "trial_id": record.get("trial_id", ""),
        "refresh_group_id": record.get("refresh_group_id", ""),
        "surface": record.get("surface", ""),
        "command_velocity_mps": record.get("command_velocity_mps", ""),
        "desired_velocity_mps": record.get("desired_velocity_mps", ""),
        "measured_actual_velocity_mps": "",
        "tracking_error_mps": "",
        "yaw_drift_deg": "",
        "imu_yaw_drift_deg": "",
        "forward_distance_m": "",
        "duration_sec": "",
        "window_start_sec": window_start,
        "window_end_sec": window_end,
        "n_samples": 0,
        "extraction_status": "invalid",
        "invalid_reason": "",
        "state_log_path": str(log_path),
        "physical_run_status": record.get("physical_run_status", ""),
        "notes": "M24-F corrected command-window extraction",
    }
    if not log_path.exists():
        base["invalid_reason"] = "state_log_missing"
        return base
    rows = read_csv(log_path)
    window = [row for row in rows if window_start <= to_float(row.get("t_rel")) <= window_end]
    if len(window) < 2:
        base["invalid_reason"] = "insufficient_window_samples"
        base["n_samples"] = len(window)
        return base
    try:
        start = window[0]
        end = window[-1]
        x0, y0, theta0 = float(start["odom_x"]), float(start["odom_y"]), float(start["odom_theta"])
        x1, y1, theta1 = float(end["odom_x"]), float(end["odom_y"]), float(end["odom_theta"])
        t0 = float(start.get("timestamp_monotonic") or start["t_rel"])
        t1 = float(end.get("timestamp_monotonic") or end["t_rel"])
        duration = t1 - t0
        if duration <= 0:
            duration = float(end["t_rel"]) - float(start["t_rel"])
        if duration <= 0:
            raise ValueError("non_positive_duration")
        distance = (x1 - x0) * math.cos(theta0) + (y1 - y0) * math.sin(theta0)
        measured = distance / duration
        desired = float(record["desired_velocity_mps"])
        yaw = abs(wrap_to_pi(theta1 - theta0)) * 180.0 / math.pi
        imu0 = maybe_float(start.get("imu_yaw"))
        imu1 = maybe_float(end.get("imu_yaw"))
        imu_yaw = "" if imu0 is None or imu1 is None else round(abs(wrap_to_pi(imu1 - imu0)) * 180.0 / math.pi, 6)
    except Exception as exc:
        base["invalid_reason"] = f"extraction_error:{exc}"
        base["n_samples"] = len(window)
        return base
    base.update({
        "measured_actual_velocity_mps": round(measured, 6),
        "tracking_error_mps": round(measured - desired, 6),
        "yaw_drift_deg": round(yaw, 6),
        "imu_yaw_drift_deg": imu_yaw,
        "forward_distance_m": round(distance, 6),
        "duration_sec": round(duration, 6),
        "n_samples": len(window),
        "extraction_status": "ok",
        "invalid_reason": "",
    })
    return base


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: str | None) -> float:
    try:
        return float(value) if value not in (None, "") else float("nan")
    except ValueError:
        return float("nan")


def maybe_float(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def wrap_to_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def build_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-F Corrected Extraction Report",
        "",
        f"- Session: `{summary['session_id']}`",
        f"- Method: `{summary['method']}`",
        f"- Window: {summary['window_start_sec']} to {summary['window_end_sec']} sec",
        f"- Corrected rows: {summary['corrected_extracted_count']}",
        f"- Invalid rows: {summary['invalid_count']}",
        f"- Original faulty extraction used: `{str(summary['original_faulty_extraction_used']).lower()}`",
        "",
        "| Trial ID | Command | Corrected Actual | Tracking Error | Yaw Drift | Status |",
        "|----------|---------|------------------|----------------|-----------|--------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['trial_id']} | {row['command_velocity_mps']} | {row['measured_actual_velocity_mps']} | "
            f"{row['tracking_error_mps']} | {row['yaw_drift_deg']} | {row['extraction_status']} |"
        )
    lines += [
        "",
        "This corrected extraction does not overwrite the K1 gold profile and does not claim compensation improvement.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
