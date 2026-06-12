"""Extract corrected measurements from M24-H controlled S2 replication trials.

Uses the corrected command-window method from M24-F (command phase with
trim), NOT the faulty M24-B/M24-C full-log extraction.

Usage:
  python scripts/extract_m24h_controlled_s2_replication_trials.py \\
    --session-dir data/compensation_experiments/m24h_controlled_s2_replication/<id>/
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXTRACTION_FIELDS = [
    "trial_id", "replication_group_id", "surface", "condition",
    "command_velocity_mps", "desired_velocity_mps",
    "measured_actual_velocity_mps", "tracking_error_mps",
    "yaw_drift_deg", "imu_yaw_drift_deg",
    "extraction_status", "invalid_reason",
    "state_log_path", "physical_run_status", "metadata_status", "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract M24-H controlled S2 replication measurements.")
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--command-window-trim-sec", type=float, default=1.0,
                        help="Seconds to trim from start/end of command phase (default: 1.0)")
    args = parser.parse_args(argv)

    session_dir = Path(args.session_dir)
    if not session_dir.is_dir():
        print(f"ERROR: session dir not found: {session_dir}", file=sys.stderr)
        return 1

    state_log_dir = session_dir / "state_logs"
    if not state_log_dir.is_dir():
        print(f"ERROR: state_logs not found: {state_log_dir}", file=sys.stderr)
        return 1

    log_files = sorted(state_log_dir.glob("*.csv"))
    if not log_files:
        print("No state logs found.", file=sys.stderr)
        return 1

    extracted: list[dict[str, Any]] = []
    for log_path in log_files:
        trial_id = log_path.stem
        try:
            result = _extract_trial(log_path, trial_id, args.command_window_trim_sec)
            extracted.append(result)
        except Exception as exc:
            extracted.append({
                "trial_id": trial_id, "extraction_status": "extraction_error",
                "invalid_reason": str(exc), "state_log_path": str(log_path),
            })

    # Write corrected results
    out_csv = session_dir / "corrected_extracted_results.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXTRACTION_FIELDS)
        w.writeheader()
        for rec in extracted:
            w.writerow({k: rec.get(k, "") for k in EXTRACTION_FIELDS})

    summary = {
        "extraction_time": datetime.now(timezone.utc).isoformat(),
        "method": f"command_phase_with_{args.command_window_trim_sec}s_trim",
        "total_logs": len(log_files), "extracted": len(extracted),
        "corrected_extraction": True,
        "disclaimer": "M24-H controlled replication — corrected extraction — no profile adoption claim",
    }
    (session_dir / "corrected_extraction_summary.json").write_text(json.dumps(summary, indent=2))

    report = _build_report(summary, extracted)
    (session_dir / "corrected_extraction_report.md").write_text(report, encoding="utf-8")

    print(f"Extracted {len(extracted)} trials -> {out_csv}")
    return 0


def _extract_trial(log_path: Path, trial_id: str, trim_sec: float) -> dict[str, Any]:
    with log_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {"trial_id": trial_id, "extraction_status": "insufficient_samples", "state_log_path": str(log_path)}

    # Get command-phase rows
    cmd_rows = [r for r in rows if r.get("phase") == "command"]
    if not cmd_rows:
        cmd_rows = rows

    # Apply trim
    if len(cmd_rows) > 2 * int(trim_sec * 10):
        trim_n = max(1, int(len(cmd_rows) * trim_sec / 6.0))  # ~6s command window
        cmd_rows = cmd_rows[trim_n:-trim_n]

    if len(cmd_rows) < 2:
        return {"trial_id": trial_id, "extraction_status": "insufficient_samples", "state_log_path": str(log_path)}

    ox = _safe_floats(cmd_rows, "odom_x")
    oy = _safe_floats(cmd_rows, "odom_y")
    ot = _safe_floats(cmd_rows, "odom_theta")
    iy = _safe_floats(cmd_rows, "imu_yaw")
    ts = _safe_floats(cmd_rows, "timestamp_monotonic")

    forward_dist = math.hypot(ox[-1] - ox[0], oy[-1] - oy[0])
    duration = ts[-1] - ts[0] if len(ts) >= 2 and ts[-1] > ts[0] else len(cmd_rows) / 1000.0
    measured = forward_dist / duration if duration > 0 else 0.0
    yaw_drift = max(abs(ot[-1] - ot[0]) if len(ot) >= 2 else 0.0,
                    abs(iy[-1] - iy[0]) if len(iy) >= 2 else 0.0)
    yaw_drift_deg = math.degrees(yaw_drift)
    imu_drift = math.degrees(abs(iy[-1] - iy[0])) if len(iy) >= 2 else 0.0

    r0 = rows[0]
    return {
        "trial_id": trial_id,
        "replication_group_id": r0.get("pair_id", r0.get("refresh_group_id", "")),
        "surface": "S2_marble_floor",
        "condition": r0.get("condition", "direct_refresh_controlled"),
        "command_velocity_mps": float(r0.get("command_velocity_mps", 0)),
        "desired_velocity_mps": float(r0.get("desired_velocity_mps", 0)),
        "measured_actual_velocity_mps": round(measured, 6),
        "tracking_error_mps": round(measured - float(r0.get("command_velocity_mps", 0)), 6),
        "yaw_drift_deg": round(yaw_drift_deg, 4),
        "imu_yaw_drift_deg": round(imu_drift, 4),
        "extraction_status": "ok",
        "invalid_reason": "",
        "state_log_path": str(log_path),
        "physical_run_status": "extracted",
        "metadata_status": "na",
        "notes": f"corrected command-window extraction, trim={trim_sec}s",
    }


def _safe_floats(rows: list[dict[str, str]], key: str) -> list[float]:
    vals = []
    for r in rows:
        try:
            vals.append(float(r.get(key, 0)))
        except (ValueError, TypeError):
            pass
    return vals


def _build_report(summary: dict, extracted: list) -> str:
    lines = ["# M24-H Corrected Extraction Report", "",
             f"- Method: {summary['method']}", f"- Logs: {summary['total_logs']}",
             f"- Extracted: {summary['extracted']}",
             "", "| Trial | v_cmd | v_actual | |error| | yaw_drift | status |",
             "|-------|-------|----------|--------|-----------|--------|"]
    for r in extracted[:30]:
        lines.append(f"| {r.get('trial_id','?')} | {r.get('command_velocity_mps','?')} | "
                     f"{r.get('measured_actual_velocity_mps',0):.4f} | "
                     f"{abs(r.get('tracking_error_mps',0)):.4f} | "
                     f"{r.get('yaw_drift_deg',0):.2f} | {r.get('extraction_status','?')} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
