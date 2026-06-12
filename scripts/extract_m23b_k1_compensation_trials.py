"""Extract measurements from M23-B K1 compensation trials.

Reads a M23-B session directory, extracts measured velocity and yaw drift
from state logs, and preserves pair_id, condition, desired_velocity,
and command_velocity.

Usage:
  python scripts/extract_m23b_k1_compensation_trials.py \\
    --session-dir data/compensation_experiments/m23b_k1/<session_id>/
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXTRACTION_FIELDS = [
    "trial_id", "pair_id", "condition", "surface",
    "desired_velocity_mps", "command_velocity_mps",
    "measured_actual_velocity_mps", "absolute_tracking_error_mps",
    "relative_tracking_error", "yaw_drift_deg", "imu_yaw_drift_deg",
    "extraction_status", "n_samples", "state_log_path", "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract M23-B K1 compensation trial measurements.")
    parser.add_argument("--session-dir", required=True, help="Path to session directory")
    args = parser.parse_args(argv)

    session_dir = Path(args.session_dir)
    if not session_dir.is_dir():
        print(f"Error: session directory not found: {session_dir}", file=sys.stderr)
        return 1

    state_log_dir = session_dir / "state_logs"
    if not state_log_dir.is_dir():
        print(f"Error: state_logs directory not found: {state_log_dir}", file=sys.stderr)
        return 1

    log_files = sorted(state_log_dir.glob("*.csv"))
    if not log_files:
        print(f"No CSV log files found in {state_log_dir}", file=sys.stderr)
        return 1

    extracted: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for log_path in log_files:
        trial_id = log_path.stem
        try:
            result = _extract_trial(log_path, trial_id)
            extracted.append(result)
        except Exception as exc:
            errors.append({"trial_id": trial_id, "error": str(exc)})

    # Write extracted results
    output_csv = session_dir / "extracted_results.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXTRACTION_FIELDS)
        w.writeheader()
        for rec in extracted:
            w.writerow({k: rec.get(k, "") for k in EXTRACTION_FIELDS})

    # Write summary
    summary = {
        "extraction_time": datetime.now(timezone.utc).isoformat(),
        "session_dir": str(session_dir),
        "total_logs": len(log_files),
        "successfully_extracted": len(extracted),
        "extraction_errors": len(errors),
        "extraction_method": "odometer_displacement_over_command_window",
        "disclaimer": "M23-B execution pack — not physical validation — no compensation improvement claim",
    }
    (session_dir / "extraction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Write report
    report = _build_report(summary, extracted, errors)
    (session_dir / "extraction_report.md").write_text(report, encoding="utf-8")

    print(f"Extracted {len(extracted)} trials ({len(errors)} errors)")
    print(f"  Output: {output_csv}")
    print(f"  Summary: {session_dir / 'extraction_summary.json'}")
    return 0


def _extract_trial(log_path: Path, trial_id: str) -> dict[str, Any]:
    with log_path.open(newline="", encoding="utf-8-sig") as f:
        samples = list(csv.DictReader(f))

    if not samples:
        raise ValueError(f"Empty log: {log_path}")

    # Read metadata from first row
    pair_id = samples[0].get("pair_id", "")
    condition = samples[0].get("condition", "")
    desired = float(samples[0].get("desired_velocity_mps", 0))
    cmd = float(samples[0].get("command_velocity_mps", 0))

    # Extract command-phase samples
    cmd_samples = [s for s in samples if s.get("phase") == "command"]
    if not cmd_samples:
        cmd_samples = samples

    odom_x = []
    odom_y = []
    odom_theta = []
    imu_yaw = []
    for s in cmd_samples:
        try:
            odom_x.append(float(s.get("odom_x", 0)))
            odom_y.append(float(s.get("odom_y", 0)))
            odom_theta.append(float(s.get("odom_theta", 0)))
            imu_yaw.append(float(s.get("imu_yaw", 0)))
        except (ValueError, TypeError):
            pass

    if len(odom_x) < 2:
        return {
            "trial_id": trial_id, "pair_id": pair_id, "condition": condition,
            "surface": "", "desired_velocity_mps": desired,
            "command_velocity_mps": cmd, "measured_actual_velocity_mps": 0.0,
            "absolute_tracking_error_mps": abs(0.0 - desired),
            "relative_tracking_error": (0.0 - desired) / desired if desired != 0 else 0.0,
            "yaw_drift_deg": 0.0, "imu_yaw_drift_deg": 0.0,
            "extraction_status": "insufficient_samples", "n_samples": len(odom_x),
            "state_log_path": str(log_path), "notes": "",
        }

    # Compute velocity from displacement
    dx = odom_x[-1] - odom_x[0]
    dy = odom_y[-1] - odom_y[0]
    displacement = (dx**2 + dy**2)**0.5
    duration = len(odom_x) / 10.0
    if duration <= 0:
        duration = 6.0
    measured = displacement / duration

    # Yaw drift
    yaw_drift = abs(odom_theta[-1] - odom_theta[0]) if len(odom_theta) >= 2 else 0.0
    imu_drift = abs(imu_yaw[-1] - imu_yaw[0]) if len(imu_yaw) >= 2 else 0.0

    status = "ok"

    return {
        "trial_id": trial_id, "pair_id": pair_id, "condition": condition,
        "surface": "", "desired_velocity_mps": desired,
        "command_velocity_mps": cmd,
        "measured_actual_velocity_mps": round(measured, 6),
        "absolute_tracking_error_mps": round(abs(measured - desired), 6),
        "relative_tracking_error": round((measured - desired) / desired, 6) if desired != 0 else 0.0,
        "yaw_drift_deg": round(yaw_drift, 6),
        "imu_yaw_drift_deg": round(imu_drift, 6),
        "extraction_status": status, "n_samples": len(odom_x),
        "state_log_path": str(log_path), "notes": "",
    }


def _build_report(summary: dict, extracted: list, errors: list) -> str:
    lines = [
        "# M23-B Compensation Trial Extraction Report",
        "",
        f"- Total logs: {summary['total_logs']}",
        f"- Extracted: {summary['successfully_extracted']}",
        f"- Errors: {summary['extraction_errors']}",
        "",
        "**Disclaimer**: M23-B execution pack — not physical validation.",
        "",
    ]
    if extracted:
        lines.append("| Trial ID | Pair | Cond | v_desired | u_cmd | v_actual | |error| |")
        lines.append("|----------|------|------|-----------|-------|----------|---------|")
        for r in extracted[:20]:
            lines.append(f"| {r['trial_id']} | {r['pair_id']} | {r['condition']} | {r['desired_velocity_mps']} | {r['command_velocity_mps']} | {r['measured_actual_velocity_mps']:.4f} | {r['absolute_tracking_error_mps']:.4f} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
