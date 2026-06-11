"""Booster K1 measurement session QC.

Validates the integrity and completeness of a K1 measurement session.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BoosterK1MeasurementQC:
    """Quality control checker for Booster K1 measurement sessions.

    Checks:
    - session metadata exists
    - trial plan exists
    - trial records exist
    - state logs exist
    - extraction output exists
    - no duplicate trial IDs
    - command_velocity is present
    - measured_actual_velocity is present
    - yaw_drift_statistic is present
    - extraction_status is present
    - expected repeats per surface-speed cell
    - no command_velocity copied into measured_actual_velocity
    - invalid trial records are explicit and reasoned
    """

    platform_id = "booster_k1"

    def run_qc(self, session_dir: Path) -> dict[str, Any]:
        """Run all QC checks on a session directory.

        Returns a QC summary dict with pass/fail status and details.
        """
        session_dir = Path(session_dir)
        checks: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        # Check session metadata
        metadata_path = session_dir / "session_metadata.json"
        check = _check_file(metadata_path, "session_metadata.json")
        checks.append(check)
        if not check["pass"]:
            errors.append(check["error"])

        # Check trial plan
        plan_path = session_dir / "trial_plan.csv"
        check = _check_file(plan_path, "trial_plan.csv")
        checks.append(check)
        if not check["pass"]:
            errors.append(check["error"])

        # Check trial records
        records_path = session_dir / "trial_records.csv"
        check = _check_file(records_path, "trial_records.csv")
        checks.append(check)
        if not check["pass"]:
            errors.append(check["error"])

        # Check state logs directory
        state_logs_dir = session_dir / "state_logs"
        check = _check_dir(state_logs_dir, "state_logs/")
        checks.append(check)
        if not check["pass"]:
            errors.append(check["error"])

        # Check extraction output
        extracted_path = session_dir / "extracted_measurements.csv"
        check = _check_file(extracted_path, "extracted_measurements.csv")
        checks.append(check)
        if not check["pass"]:
            warnings.append(check.get("error", "extracted_measurements.csv missing"))

        # Load data for deeper checks
        metadata = _load_json(metadata_path)
        trial_records = _load_csv(records_path)
        extracted = _load_csv(extracted_path)

        # Check for duplicate trial IDs
        if trial_records:
            trial_ids = [r.get("trial_id", "") for r in trial_records]
            dupes = [tid for tid in set(trial_ids) if trial_ids.count(tid) > 1]
            if dupes:
                errors.append(f"duplicate_trial_ids:{','.join(dupes)}")
                checks.append({"check": "no_duplicate_trial_ids", "pass": False, "duplicates": dupes})
            else:
                checks.append({"check": "no_duplicate_trial_ids", "pass": True})

        # Check trial record fields
        if trial_records:
            field_checks = _check_trial_record_fields(trial_records)
            checks.extend(field_checks)
            for fc in field_checks:
                if not fc["pass"]:
                    errors.append(fc.get("error", ""))

        # Check extraction fields
        if extracted:
            extract_checks = _check_extraction_fields(extracted)
            checks.extend(extract_checks)
            for ec in extract_checks:
                if not ec["pass"]:
                    errors.append(ec.get("error", ""))

        # Check expected repeats per surface-speed cell
        if metadata and trial_records:
            repeat_check = _check_expected_repeats(metadata, trial_records)
            checks.append(repeat_check)
            if not repeat_check["pass"]:
                errors.append(repeat_check.get("error", ""))

        # Check no command_velocity == measured_actual_velocity (copy-paste guard)
        if extracted:
            copy_check = _check_no_velocity_copy(extracted)
            checks.append(copy_check)
            if not copy_check["pass"]:
                errors.append(copy_check.get("error", ""))

        # Check invalid trials are explicit
        if trial_records:
            invalid_check = _check_invalid_trials_explicit(trial_records)
            checks.append(invalid_check)
            if not invalid_check["pass"]:
                errors.append(invalid_check.get("error", ""))

        summary = {
            "qc_time": datetime.now(timezone.utc).isoformat(),
            "session_dir": str(session_dir),
            "platform": self.platform_id,
            "overall_pass": len(errors) == 0,
            "checks_passed": sum(1 for c in checks if c.get("pass", False)),
            "checks_total": len(checks),
            "errors": errors,
            "warnings": warnings,
            "checks": checks,
        }

        # Write QC summary
        qc_path = session_dir / "qc_summary.json"
        qc_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        # Write QC report
        report_path = session_dir / "qc_report.md"
        report_path.write_text(_build_qc_report(summary), encoding="utf-8")

        return summary


def _check_file(path: Path, label: str) -> dict[str, Any]:
    if path.exists():
        return {"check": f"{label}:exists", "pass": True, "path": str(path)}
    return {"check": f"{label}:exists", "pass": False, "error": f"{label}:missing"}


def _check_dir(path: Path, label: str) -> dict[str, Any]:
    if path.is_dir():
        file_count = len(list(path.glob("*.csv")))
        return {"check": f"{label}:exists", "pass": True, "path": str(path), "csv_count": file_count}
    return {"check": f"{label}:exists", "pass": False, "error": f"{label}:missing"}


def _load_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _check_trial_record_fields(
    records: list[dict[str, str]],
) -> list[dict[str, Any]]:
    checks = []
    required = ["command_velocity", "valid", "trial_id"]
    for field in required:
        missing = [r.get("trial_id", "?") for r in records if field not in r or not r[field]]
        if missing:
            checks.append({
                "check": f"trial_record:{field}:present",
                "pass": False,
                "error": f"trial_record:{field}:missing_in:{','.join(missing[:5])}",
            })
        else:
            checks.append({"check": f"trial_record:{field}:present", "pass": True})
    return checks


def _check_extraction_fields(
    records: list[dict[str, str]],
) -> list[dict[str, Any]]:
    checks = []
    required = ["command_velocity", "measured_actual_velocity", "yaw_drift_statistic", "extraction_status"]
    for field in required:
        missing = [r.get("trial_id", "?") for r in records if field not in r or not r[field]]
        if missing:
            checks.append({
                "check": f"extraction:{field}:present",
                "pass": False,
                "error": f"extraction:{field}:missing_in:{','.join(missing[:5])}",
            })
        else:
            checks.append({"check": f"extraction:{field}:present", "pass": True})

    # Check extraction_status values
    non_ok = [r for r in records if r.get("extraction_status", "") != "ok"]
    if non_ok:
        checks.append({
            "check": "extraction:all_status_ok",
            "pass": False,
            "error": f"extraction:non_ok_status:{len(non_ok)}_trials",
        })
    else:
        checks.append({"check": "extraction:all_status_ok", "pass": True})

    return checks


def _check_expected_repeats(
    metadata: dict[str, Any],
    records: list[dict[str, str]],
) -> dict[str, Any]:
    """Check that each surface-speed cell has the expected number of repeats."""
    expected_repeats = metadata.get("repeats", 3)
    cells: dict[str, int] = {}
    for r in records:
        if r.get("valid", "").lower() != "true":
            continue
        surface = r.get("surface_type", "unknown")
        speed = r.get("command_velocity", "unknown")
        key = f"{surface}:{speed}"
        cells[key] = cells.get(key, 0) + 1

    underfilled = [f"{k}({v}/{expected_repeats})" for k, v in cells.items() if v < expected_repeats]
    if underfilled:
        return {
            "check": "expected_repeats_per_cell",
            "pass": False,
            "error": f"underfilled_cells:{','.join(underfilled)}",
        }
    return {"check": "expected_repeats_per_cell", "pass": True}


def _check_no_velocity_copy(
    records: list[dict[str, str]],
) -> dict[str, Any]:
    """Guard against command_velocity being copied into measured_actual_velocity."""
    suspect = []
    for r in records:
        try:
            cmd = float(r.get("command_velocity", 0))
            meas = float(r.get("measured_actual_velocity", 0))
            if cmd > 0 and abs(cmd - meas) < 0.0001:
                suspect.append(r.get("trial_id", "?"))
        except (ValueError, TypeError):
            pass
    if suspect:
        return {
            "check": "no_command_velocity_copy",
            "pass": False,
            "error": f"suspected_copy_paste:{','.join(suspect[:5])}",
        }
    return {"check": "no_command_velocity_copy", "pass": True}


def _check_invalid_trials_explicit(
    records: list[dict[str, str]],
) -> dict[str, Any]:
    """Ensure invalid trials have an explicit reason."""
    invalid_without_reason = []
    for r in records:
        if r.get("valid", "").lower() == "false":
            reason = r.get("invalid_reason", "").strip()
            if not reason:
                invalid_without_reason.append(r.get("trial_id", "?"))
    if invalid_without_reason:
        return {
            "check": "invalid_trials_have_reason",
            "pass": False,
            "error": f"invalid_without_reason:{','.join(invalid_without_reason[:5])}",
        }
    return {"check": "invalid_trials_have_reason", "pass": True}


def _build_qc_report(summary: dict[str, Any]) -> str:
    """Build a Markdown QC report."""
    status = "✅ PASSED" if summary["overall_pass"] else "❌ FAILED"
    lines = [
        "# Booster K1 Measurement Session QC Report",
        "",
        f"**Overall**: {status}",
        f"- **Session**: {summary['session_dir']}",
        f"- **Platform**: {summary['platform']}",
        f"- **QC time**: {summary['qc_time']}",
        f"- **Checks passed**: {summary['checks_passed']}/{summary['checks_total']}",
        "",
    ]

    if summary["errors"]:
        lines.append("## Errors")
        for e in summary["errors"]:
            lines.append(f"- ❌ {e}")

    if summary["warnings"]:
        lines.append("")
        lines.append("## Warnings")
        for w in summary["warnings"]:
            lines.append(f"- ⚠️ {w}")

    lines.append("")
    lines.append("## All Checks")
    lines.append("")
    for c in summary.get("checks", []):
        icon = "✅" if c.get("pass") else "❌"
        lines.append(f"- {icon} {c.get('check', '?')}")

    return "\n".join(lines) + "\n"
