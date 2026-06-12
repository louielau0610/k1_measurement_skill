"""Extract M24-B S2 profile refresh measurements from odometer logs."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXTRACTION_FIELDS = [
    "trial_id",
    "refresh_group_id",
    "surface",
    "command_velocity_mps",
    "desired_velocity_mps",
    "measured_actual_velocity_mps",
    "tracking_error_mps",
    "yaw_drift_deg",
    "imu_yaw_drift_deg",
    "extraction_status",
    "invalid_reason",
    "state_log_path",
    "physical_run_status",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract M24-B S2 profile refresh trials.")
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--window-start-sec", type=float, default=1.0)
    parser.add_argument("--window-end-sec", type=float, default=6.0)
    args = parser.parse_args(argv)

    if not args.session_dir.is_dir():
        print(f"ERROR: session directory not found: {args.session_dir}", file=sys.stderr)
        return 1

    records = read_trial_records(args.session_dir / "trial_records.csv")
    metadata = read_json(args.session_dir / "session_metadata.json")
    results: list[dict[str, Any]] = []
    for record in records:
        log_path = Path(record.get("state_log_path", ""))
        if not log_path.is_absolute():
            cwd_relative = Path(record.get("state_log_path", ""))
            log_path = cwd_relative if cwd_relative.exists() else args.session_dir / cwd_relative
        if not log_path.exists():
            fallback = args.session_dir / "state_logs" / f"{record['trial_id']}.csv"
            log_path = fallback
        results.append(extract_record(record, log_path, args.window_start_sec, args.window_end_sec))

    output_csv = args.session_dir / "extracted_results.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXTRACTION_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result.get(field, "") for field in EXTRACTION_FIELDS})

    ok_count = sum(1 for result in results if result["extraction_status"] == "ok")
    summary = {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "session_dir": str(args.session_dir),
        "session_id": metadata.get("session_id", ""),
        "planned_records": len(records),
        "extracted_results": len(results),
        "ok_count": ok_count,
        "invalid_count": len(results) - ok_count,
        "extraction_method": "odometer_forward_projection_window",
        "analysis_window_sec": [args.window_start_sec, args.window_end_sec],
        "profile_update_status": "not_updated",
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "claim_boundary": "extraction only; no profile refresh claim until QC passes and no compensation improvement claim",
    }
    (args.session_dir / "extraction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.session_dir / "extraction_report.md").write_text(build_report(summary, results), encoding="utf-8")
    print(f"Extracted {len(results)} M24-B trials ({ok_count} ok)")
    return 0 if ok_count == len(results) else 1


def read_trial_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"trial_records.csv not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def extract_record(record: dict[str, str], log_path: Path, window_start: float, window_end: float) -> dict[str, Any]:
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
        "extraction_status": "invalid",
        "invalid_reason": "",
        "state_log_path": str(log_path),
        "physical_run_status": record.get("physical_run_status", ""),
        "notes": record.get("notes", ""),
    }
    if record.get("valid", "").lower() not in {"true", "1", "yes"}:
        base["invalid_reason"] = record.get("invalid_reason", "trial_not_valid")
        return base
    if not log_path.exists():
        base["invalid_reason"] = "state_log_missing"
        return base

    with log_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    window = [
        row for row in rows
        if _float(row.get("t_rel")) is not None and window_start <= _float(row.get("t_rel")) <= window_end
    ]
    if len(window) < 2:
        base["invalid_reason"] = "insufficient_window_samples"
        return base

    try:
        start = window[0]
        end = window[-1]
        start_x = float(start["odom_x"])
        start_y = float(start["odom_y"])
        end_x = float(end["odom_x"])
        end_y = float(end["odom_y"])
        start_theta = float(start["odom_theta"])
        end_theta = float(end["odom_theta"])
        start_t = float(start["t_rel"])
        end_t = float(end["t_rel"])
        elapsed = end_t - start_t
        if elapsed <= 0:
            raise ValueError("non_positive_elapsed")
        dx = end_x - start_x
        dy = end_y - start_y
        distance = dx * math.cos(start_theta) + dy * math.sin(start_theta)
        measured = distance / elapsed
        desired = float(record["desired_velocity_mps"])
        yaw_drift = abs(_wrap_to_pi(end_theta - start_theta)) * 180.0 / math.pi
        imu_yaw_drift = ""
        imu_start = _float(start.get("imu_yaw"))
        imu_end = _float(end.get("imu_yaw"))
        if imu_start is not None and imu_end is not None:
            imu_yaw_drift = round(abs(_wrap_to_pi(imu_end - imu_start)) * 180.0 / math.pi, 6)
    except Exception as exc:
        base["invalid_reason"] = f"extraction_error:{exc}"
        return base

    base.update({
        "measured_actual_velocity_mps": round(measured, 6),
        "tracking_error_mps": round(measured - desired, 6),
        "yaw_drift_deg": round(yaw_drift, 6),
        "imu_yaw_drift_deg": imu_yaw_drift,
        "extraction_status": "ok",
        "invalid_reason": "",
    })
    return base


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None and value != "" else None
    except ValueError:
        return None


def _wrap_to_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def build_report(summary: dict[str, Any], results: list[dict[str, Any]]) -> str:
    lines = [
        "# M24-B S2 Profile Refresh Extraction Report",
        "",
        f"- Session: `{summary['session_id']}`",
        f"- Results: {summary['extracted_results']}",
        f"- OK: {summary['ok_count']}",
        f"- Invalid: {summary['invalid_count']}",
        f"- Method: `{summary['extraction_method']}`",
        f"- Profile update status: `{summary['profile_update_status']}`",
        f"- Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        "",
        "This extraction does not overwrite `k1_gold_profile_v1` and does not claim compensation improvement.",
        "",
        "| Trial ID | Group | Command | Measured | Tracking Error | Yaw Drift | Status |",
        "|----------|-------|---------|----------|----------------|-----------|--------|",
    ]
    for result in results:
        lines.append(
            f"| {result['trial_id']} | {result['refresh_group_id']} | {result['command_velocity_mps']} | "
            f"{result['measured_actual_velocity_mps']} | {result['tracking_error_mps']} | "
            f"{result['yaw_drift_deg']} | {result['extraction_status']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
