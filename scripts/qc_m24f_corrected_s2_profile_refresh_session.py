"""QC corrected M24-F S2 profile refresh extraction."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SESSION = Path("data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QC M24-F corrected extraction.")
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    summary = qc(args.session_dir)
    print(f"M24-F corrected QC pass: {summary['overall_pass']}")
    return 0 if summary["overall_pass"] else 1


def qc(session_dir: Path) -> dict[str, Any]:
    rows = read_csv(session_dir / "corrected_extracted_results.csv")
    trial_records = read_csv(session_dir / "trial_records.csv")
    errors: list[str] = []
    groups = Counter(row["command_velocity_mps"] for row in rows)
    record_conditions = {row.get("condition", "") for row in trial_records}
    record_ids = {row.get("trial_id", "") for row in trial_records}
    extracted_ids = {row.get("trial_id", "") for row in rows}
    if len(rows) != 30:
        errors.append(f"corrected_row_count:{len(rows)}")
    if record_conditions != {"direct_refresh"}:
        errors.append(f"non_direct_refresh_records:{sorted(record_conditions)}")
    if extracted_ids != record_ids:
        errors.append("corrected_trial_ids_do_not_match_trial_records")
    if len(groups) != 6:
        errors.append(f"velocity_group_count:{len(groups)}")
    bad_repeats = {k: v for k, v in groups.items() if v != 5}
    if bad_repeats:
        errors.append(f"bad_repeats:{bad_repeats}")
    if {row["surface"] for row in rows} != {"S2_marble_floor"}:
        errors.append("non_s2_surface_present")
    # condition is encoded in raw logs/refresh group; original records are direct_refresh only.
    if any(not row["measured_actual_velocity_mps"] for row in rows):
        errors.append("missing_measured_velocity")
    if any(not row["yaw_drift_deg"] for row in rows):
        errors.append("missing_yaw_drift")
    if any(row["extraction_status"] != "ok" for row in rows):
        errors.append("non_ok_extraction_status")
    moving = [abs(float(row["measured_actual_velocity_mps"])) for row in rows if float(row["command_velocity_mps"]) >= 0.35]
    near_zero = [value for value in moving if value < 0.02]
    if len(near_zero) == len(moving):
        errors.append("all_corrected_velocities_near_zero")
    summary = {
        "qc_time": datetime.now(timezone.utc).isoformat(),
        "session_dir": str(session_dir),
        "overall_pass": not errors,
        "corrected_extracted_count": len(rows),
        "trial_record_count": len(trial_records),
        "condition_values": sorted(record_conditions),
        "velocity_group_count": len(groups),
        "repeats_per_velocity": dict(sorted(groups.items())),
        "near_zero_velocity_count": len(near_zero),
        "original_faulty_extraction_used": False,
        "gold_profile_overwritten": False,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "errors": errors,
    }
    (session_dir / "corrected_qc_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (session_dir / "corrected_qc_report.md").write_text(build_report(summary), encoding="utf-8")
    return summary


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# M24-F Corrected Extraction QC Report",
        "",
        f"- Overall pass: `{str(summary['overall_pass']).lower()}`",
        f"- Corrected extracted count: {summary['corrected_extracted_count']}",
        f"- Trial record count: {summary['trial_record_count']}",
        f"- Conditions: `{', '.join(summary['condition_values'])}`",
        f"- Velocity groups: {summary['velocity_group_count']}",
        f"- Near-zero velocity count: {summary['near_zero_velocity_count']}",
        f"- Original faulty extraction used: `{str(summary['original_faulty_extraction_used']).lower()}`",
        f"- Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        "",
        "## Errors",
    ]
    lines.extend(f"- {error}" for error in summary["errors"]) if summary["errors"] else lines.append("- None")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
