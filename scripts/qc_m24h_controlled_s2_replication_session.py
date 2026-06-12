"""QC a M24-H controlled S2 replication session.

Verifies: 20 trials, S2 only, direct_refresh_controlled only, 4 velocity
groups × 5 repeats, no compensated rows, corrected extraction output,
metadata file, gold profile not overwritten.

Usage:
  python scripts/qc_m24h_controlled_s2_replication_session.py \\
    --session-dir data/compensation_experiments/m24h_controlled_s2_replication/<id>/
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QC M24-H controlled S2 replication session.")
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    session_dir = Path(args.session_dir)
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def _check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": ok, "detail": detail})
        if not ok:
            errors.append(f"{name}:{detail}")

    # Session metadata
    meta_path = session_dir / "session_metadata.json"
    _check("session_metadata_exists", meta_path.exists())
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        _check("surface_is_S2", meta.get("surface") == "S2_marble_floor", str(meta.get("surface")))
        _check("condition_is_direct_refresh_controlled", meta.get("condition") == "direct_refresh_controlled")
        _check("gold_profile_not_overwritten", meta.get("gold_profile_overwritten", False) is False)
        _check("profile_not_adopted", meta.get("profile_adoption_status") == "not_adopted")
        _check("deployment_ready_false", meta.get("deployment_ready") is False)
        _check("go1_g1_blocked", meta.get("go1_g1_blocked") is True)

    # Controlled metadata
    cmeta_path = session_dir / "controlled_metadata.json"
    _check("controlled_metadata_exists", cmeta_path.exists())

    # Trial records
    records_path = session_dir / "trial_records.csv"
    _check("trial_records_exists", records_path.exists())
    records = []
    if records_path.exists():
        with records_path.open(newline="", encoding="utf-8-sig") as f:
            records = list(csv.DictReader(f))
        n = len(records)
        _check("trial_count_is_20", n == 20, f"got {n}")
        executed = sum(1 for r in records if r.get("physical_run_status") == "executed")
        skipped = sum(1 for r in records if r.get("physical_run_status") == "skipped")
        invalid = sum(1 for r in records if r.get("valid", "").lower() != "true")
        _check("all_20_executed", executed == 20 and skipped == 0, f"exec={executed} skip={skipped}")
        _check("no_invalid_trials", invalid == 0, f"invalid={invalid}")

        # Check conditions
        for r in records:
            if r.get("condition") != "direct_refresh_controlled":
                _check("condition_check", False, f"{r['trial_id']}: {r.get('condition')}")
                break
        else:
            _check("all_direct_refresh_controlled", True)

        # Velocity groups
        vel_groups: dict[str, int] = {}
        for r in records:
            vel_groups[r.get("command_velocity_mps", "?")] = vel_groups.get(r.get("command_velocity_mps", "?"), 0) + 1
        _check("four_velocity_groups", len(vel_groups) == 4, str(vel_groups))
        for vel, count in vel_groups.items():
            _check(f"velocity_{vel}_5_repeats", count == 5, f"got {count}")

        # No compensated
        compensated = [r for r in records if r.get("condition", "").startswith("compensated")]
        _check("no_compensated_rows", len(compensated) == 0, str(len(compensated)))

    # State logs
    state_dir = session_dir / "state_logs"
    _check("state_logs_dir_exists", state_dir.is_dir())
    if state_dir.is_dir():
        csv_count = len(list(state_dir.glob("*.csv")))
        _check("state_log_count_20", csv_count == 20, f"got {csv_count}")

    # Corrected extraction
    ext_path = session_dir / "corrected_extracted_results.csv"
    _check("corrected_extraction_exists", ext_path.exists())
    if ext_path.exists():
        with ext_path.open(newline="", encoding="utf-8-sig") as f:
            ext_rows = list(csv.DictReader(f))
        _check("extraction_count_20", len(ext_rows) == 20, f"got {len(ext_rows)}")
        missing_vel = [r["trial_id"] for r in ext_rows if not r.get("measured_actual_velocity_mps")]
        _check("no_missing_measured_velocity", len(missing_vel) == 0, str(missing_vel[:5]))
        missing_yaw = [r["trial_id"] for r in ext_rows if not r.get("yaw_drift_deg")]
        _check("no_missing_yaw_drift", len(missing_yaw) == 0, str(missing_yaw[:5]))
        non_ok = [r for r in ext_rows if r.get("extraction_status") != "ok"]
        _check("all_extraction_ok", len(non_ok) == 0, str(len(non_ok)))

    # Summary
    all_pass = len(errors) == 0
    summary = {
        "qc_time": datetime.now(timezone.utc).isoformat(),
        "overall_pass": all_pass,
        "checks_passed": sum(1 for c in checks if c["pass"]),
        "checks_total": len(checks),
        "errors": errors, "warnings": warnings, "checks": checks,
        "disclaimer": "M24-H controlled replication QC — not physical validation",
    }
    (session_dir / "qc_summary.json").write_text(json.dumps(summary, indent=2))
    (session_dir / "qc_report.md").write_text(_build_qc_md(summary), encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\nM24-H QC: {'PASSED' if all_pass else 'FAILED'} ({summary['checks_passed']}/{summary['checks_total']})")
        for e in errors:
            print(f"  - {e}")

    return 0 if all_pass else 1


def _build_qc_md(summary: dict) -> str:
    lines = ["# M24-H QC Report", "", f"Overall: {'PASSED' if summary['overall_pass'] else 'FAILED'}",
             f"Checks: {summary['checks_passed']}/{summary['checks_total']}", ""]
    for c in summary["checks"]:
        icon = "PASS" if c["pass"] else "FAIL"
        lines.append(f"- [{icon}] {c['check']} {c.get('detail','')}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
