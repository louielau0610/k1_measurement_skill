"""QC an M24-B S2 profile refresh session."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_TRIALS = 30
EXPECTED_GROUPS = 6
EXPECTED_REPEATS = 5
EXPECTED_SURFACE = "S2_marble_floor"
EXPECTED_CONDITION = "direct_refresh"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QC an M24-B S2 profile refresh session.")
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    summary = qc_session(args.session_dir)
    (args.session_dir / "qc_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.session_dir / "qc_report.md").write_text(build_report(summary), encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"M24-B QC {'PASSED' if summary['overall_pass'] else 'FAILED'}")
        for error in summary["errors"]:
            print(f"- {error}")
    return 0 if summary["overall_pass"] else 1


def qc_session(session_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []
    metadata = _read_json(session_dir / "session_metadata.json")
    records = _read_csv(session_dir / "trial_records.csv")
    extracted = _read_csv(session_dir / "extracted_results.csv")

    _check(checks, errors, "session_metadata_exists", bool(metadata), "session_metadata.json:missing")
    _check(checks, errors, "trial_records_exists", bool(records), "trial_records.csv:missing")
    _check(checks, errors, "extracted_results_exists", bool(extracted), "extracted_results.csv:missing")

    executed = [r for r in records if r.get("physical_run_status") == "executed" and r.get("valid", "").lower() == "true"]
    skipped = [r for r in records if r.get("physical_run_status") == "skipped"]
    _check(checks, errors, "planned_trial_count_30", len(records) == EXPECTED_TRIALS, f"planned_trial_count:{len(records)}")
    _check(checks, errors, "executed_trial_count_30", len(executed) == EXPECTED_TRIALS, f"executed_trial_count:{len(executed)}")
    _check(checks, errors, "skipped_trial_count_0", len(skipped) == 0, f"skipped_trial_count:{len(skipped)}")

    surfaces = {r.get("surface") for r in records + extracted if r}
    conditions = {r.get("condition") for r in records if r}
    _check(checks, errors, "s2_only", surfaces <= {EXPECTED_SURFACE}, f"unexpected_surfaces:{sorted(surfaces)}")
    _check(checks, errors, "direct_refresh_only", conditions <= {EXPECTED_CONDITION}, f"unexpected_conditions:{sorted(conditions)}")
    _check(checks, errors, "no_compensated_condition", "compensated" not in conditions, "compensated_condition_present")

    group_counts = Counter(r.get("refresh_group_id") for r in records if r.get("refresh_group_id"))
    _check(checks, errors, "six_velocity_groups", len(group_counts) == EXPECTED_GROUPS, f"group_count:{len(group_counts)}")
    bad_repeats = {group: count for group, count in group_counts.items() if count != EXPECTED_REPEATS}
    _check(checks, errors, "five_repeats_per_velocity", not bad_repeats, f"bad_repeat_counts:{bad_repeats}")

    ok_rows = [r for r in extracted if r.get("extraction_status") == "ok"]
    missing_measured = [r.get("trial_id", "?") for r in extracted if not r.get("measured_actual_velocity_mps")]
    missing_yaw = [r.get("trial_id", "?") for r in extracted if not r.get("yaw_drift_deg")]
    _check(checks, errors, "extraction_status_ok", len(ok_rows) == EXPECTED_TRIALS, f"ok_extractions:{len(ok_rows)}")
    _check(checks, errors, "no_missing_measured_velocity", not missing_measured, f"missing_measured:{missing_measured[:5]}")
    _check(checks, errors, "no_missing_yaw_drift", not missing_yaw, f"missing_yaw:{missing_yaw[:5]}")

    profile_update_status = metadata.get("profile_update_status", "not_updated")
    deployment_ready = metadata.get("deployment_ready", False)
    go1_g1_blocked = metadata.get("go1_g1_blocked", True)
    _check(checks, errors, "gold_profile_not_overwritten", profile_update_status == "not_updated", f"profile_update_status:{profile_update_status}")
    _check(checks, errors, "deployment_ready_false", deployment_ready is False, f"deployment_ready:{deployment_ready}")
    _check(checks, errors, "go1_g1_blocked", go1_g1_blocked is True, f"go1_g1_blocked:{go1_g1_blocked}")

    return {
        "qc_time": datetime.now(timezone.utc).isoformat(),
        "session_dir": str(session_dir),
        "overall_pass": not errors,
        "expected_trial_count": EXPECTED_TRIALS,
        "executed_trial_count": len(executed),
        "skipped_trial_count": len(skipped),
        "velocity_group_count": len(group_counts),
        "expected_repeats_per_velocity": EXPECTED_REPEATS,
        "profile_update_status": profile_update_status,
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "claim_boundary": "QC only; no K1 gold profile overwrite and no compensation improvement claim",
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _check(checks: list[dict[str, Any]], errors: list[str], name: str, passed: bool, error: str) -> None:
    checks.append({"check": name, "pass": passed})
    if not passed:
        errors.append(error)


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# M24-B S2 Profile Refresh QC Report",
        "",
        f"- Overall pass: `{str(summary['overall_pass']).lower()}`",
        f"- Expected trial count: {summary['expected_trial_count']}",
        f"- Executed trial count: {summary['executed_trial_count']}",
        f"- Skipped trial count: {summary['skipped_trial_count']}",
        f"- Velocity groups: {summary['velocity_group_count']}",
        f"- Repeats per velocity: {summary['expected_repeats_per_velocity']}",
        f"- Profile update status: `{summary['profile_update_status']}`",
        f"- Deployment ready: `{str(summary['deployment_ready']).lower()}`",
        f"- GO1/G1 blocked: `{str(summary['go1_g1_blocked']).lower()}`",
        "",
        "## Errors",
    ]
    if summary["errors"]:
        lines.extend(f"- {error}" for error in summary["errors"])
    else:
        lines.append("- None")
    lines += [
        "",
        "M24-B QC does not overwrite `k1_gold_profile_v1` and does not claim compensation improvement.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
