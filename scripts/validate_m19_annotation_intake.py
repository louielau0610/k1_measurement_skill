"""Validate M19 filled measurement annotations before empirical analysis."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.qc_m19_real_test_records import debug_indicator, parse_bool, parse_float

DEFAULT_ANNOTATION_CSV = Path("data/m19_repeated_validation_inputs/m19_valid_trial_measurement_annotation_template.csv")
DEFAULT_TRIAL_RECORDS = Path("data/m19_repeated_validation_inputs/m19_trial_records.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
SUMMARY_NAME = "m19r_c_annotation_intake_validation_summary.json"
REPORT_NAME = "m19r_c_annotation_intake_validation_report.md"

ALLOWED_QUALITY_FLAGS = {"high", "medium", "low", "pending"}
PLACEHOLDER_TOKENS = {
    "dummy",
    "fabricated",
    "fake",
    "placeholder",
    "simulated",
    "synthetic",
    "tbd",
    "test_fixture",
    "todo",
}
REQUIRED_COLUMNS = [
    "trial_id",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "measurement_source",
]
ANNOTATION_METHOD_ALIASES = ("annotation_method", "measurement_method")
QUALITY_FLAG_ALIASES = ("measurement_quality_flag", "measurement_confidence")
PLACEHOLDER_CHECK_FIELDS = [
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "measurement_source",
    "annotation_method",
    "measurement_method",
    "measurement_quality_flag",
    "measurement_confidence",
    "annotation_notes",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def has_any_column(fieldnames: list[str], aliases: tuple[str, ...]) -> bool:
    return any(alias in fieldnames for alias in aliases)


def first_value(row: dict[str, str], aliases: tuple[str, ...]) -> str:
    for alias in aliases:
        if alias in row:
            return str(row.get(alias, ""))
    return ""


def issue(level: str, row: int | None, field: str, message: str, trial_id: str = "") -> dict[str, Any]:
    return {"level": level, "row": row, "field": field, "trial_id": trial_id, "message": message}


def expected_and_invalid_ids(trial_records_csv: Path) -> tuple[set[str], set[str]]:
    _, rows = read_csv(trial_records_csv)
    expected: set[str] = set()
    invalid: set[str] = set()
    for row in rows:
        trial_id = row.get("trial_id", "")
        if not trial_id:
            continue
        is_valid = parse_bool(row.get("valid")) and not row.get("invalid_reason", "").strip() and not debug_indicator(row)
        if is_valid:
            expected.add(trial_id)
        else:
            invalid.add(trial_id)
    return expected, invalid


def contains_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    return lowered in PLACEHOLDER_TOKENS or any(token in lowered for token in PLACEHOLDER_TOKENS)


def validate_annotation_intake(
    annotation_csv: Path = DEFAULT_ANNOTATION_CSV,
    trial_records_csv: Path = DEFAULT_TRIAL_RECORDS,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    fieldnames, rows = read_csv(annotation_csv)
    expected_ids, invalid_ids = expected_and_invalid_ids(trial_records_csv)
    issues: list[dict[str, Any]] = []

    for column in REQUIRED_COLUMNS:
        if column not in fieldnames:
            issues.append(issue("error", None, column, "required annotation column missing"))
    if not has_any_column(fieldnames, ANNOTATION_METHOD_ALIASES):
        issues.append(issue("error", None, "annotation_method", "required annotation method column missing"))
    if not has_any_column(fieldnames, QUALITY_FLAG_ALIASES):
        issues.append(issue("error", None, "measurement_quality_flag", "required measurement quality flag column missing"))

    trial_ids = [row.get("trial_id", "") for row in rows]
    counts = Counter(trial_ids)
    duplicate_ids = sorted(trial_id for trial_id, count in counts.items() if trial_id and count > 1)
    for trial_id in duplicate_ids:
        issues.append(issue("error", None, "trial_id", "duplicate trial ID", trial_id))

    observed_ids = set(trial_ids)
    missing_expected = sorted(expected_ids - observed_ids)
    unexpected_ids = sorted(observed_ids - expected_ids)
    included_invalid_ids = sorted(observed_ids & invalid_ids)
    if len(observed_ids) != len(expected_ids) or missing_expected or unexpected_ids:
        issues.append(
            issue(
                "error",
                None,
                "trial_id",
                f"annotation IDs must exactly match expected valid trial IDs; missing={len(missing_expected)}, unexpected={len(unexpected_ids)}",
            )
        )
    for trial_id in included_invalid_ids:
        issues.append(issue("error", None, "trial_id", "invalid/debug trial ID included", trial_id))

    measured_rows = 0
    complete_measurement_rows = 0
    pending_rows = 0
    replacement_rows = 0
    for index, row in enumerate(rows, start=2):
        trial_id = row.get("trial_id", "")
        if trial_id.startswith("M19_REP_"):
            replacement_rows += 1
        actual_text = str(row.get("measured_actual_velocity", "")).strip()
        yaw_text = str(row.get("yaw_drift_statistic", "")).strip()
        source = str(row.get("measurement_source", "")).strip()
        method = first_value(row, ANNOTATION_METHOD_ALIASES).strip()
        quality = first_value(row, QUALITY_FLAG_ALIASES).strip().lower()

        for field in PLACEHOLDER_CHECK_FIELDS:
            if field in row and contains_placeholder(str(row.get(field, ""))):
                issues.append(issue("error", index, field, "placeholder or fabricated token detected", trial_id))

        actual = parse_float(actual_text) if actual_text else None
        yaw = parse_float(yaw_text) if yaw_text else None
        if actual_text and actual is None:
            issues.append(issue("error", index, "measured_actual_velocity", "actual velocity must be blank or numeric", trial_id))
        if actual is not None and actual < 0:
            issues.append(issue("error", index, "measured_actual_velocity", "actual velocity must be nonnegative", trial_id))
        if yaw_text and yaw is None:
            issues.append(issue("error", index, "yaw_drift_statistic", "yaw drift must be blank or numeric", trial_id))

        has_measurement = bool(actual_text or yaw_text)
        has_complete_measurement = actual is not None and yaw is not None
        if has_measurement:
            measured_rows += 1
            if has_complete_measurement:
                complete_measurement_rows += 1
            if not source or source.lower() == "pending":
                issues.append(issue("error", index, "measurement_source", "measurement source required when measurements are present", trial_id))
            if not method or method.lower() == "pending":
                issues.append(issue("error", index, "annotation_method", "annotation method required when measurements are present", trial_id))
            if not quality or quality == "pending":
                issues.append(issue("error", index, "measurement_quality_flag", "non-pending quality flag required when measurements are present", trial_id))
        else:
            pending_rows += 1
        if quality not in ALLOWED_QUALITY_FLAGS:
            issues.append(issue("error", index, "measurement_quality_flag", "invalid measurement quality flag", trial_id))

    all_required_measurements_present = complete_measurement_rows == len(expected_ids) and len(rows) == len(expected_ids)
    status = "pass" if not issues else "fail"
    summary = {
        "annotation_csv": str(annotation_csv),
        "trial_records_csv": str(trial_records_csv),
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "expected_trial_id_count": len(expected_ids),
        "row_count": len(rows),
        "unique_trial_id_count": len(observed_ids),
        "missing_expected_trial_ids": missing_expected,
        "unexpected_trial_ids": unexpected_ids,
        "invalid_debug_trial_ids_included": included_invalid_ids,
        "duplicate_trial_ids": duplicate_ids,
        "measured_rows": measured_rows,
        "complete_measurement_rows": complete_measurement_rows,
        "pending_rows": pending_rows,
        "replacement_rows": replacement_rows,
        "all_required_measurements_present": all_required_measurements_present,
        "empirical_response_analysis_blocked": status != "pass" or not all_required_measurements_present,
        "statistics_computed": False,
        "issue_count": len(issues),
        "issues": issues,
    }
    write_outputs(output_dir, summary)
    return summary


def write_outputs(output_dir: Path, summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / SUMMARY_NAME).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    issues = "\n".join(
        f"- row {item['row']}: `{item['field']}` {item['trial_id']} - {item['message']}".strip()
        if item["row"]
        else f"- `{item['field']}` {item['trial_id']} - {item['message']}".strip()
        for item in summary["issues"]
    ) or "- None"
    report = (
        "# M19R-C Annotation Intake Validation\n\n"
        f"Status: `{summary['status']}`\n\n"
        f"Rows: {summary['row_count']}\n\n"
        f"Expected valid trial IDs: {summary['expected_trial_id_count']}\n\n"
        f"Measured rows: {summary['measured_rows']}\n\n"
        f"Complete measurement rows: {summary['complete_measurement_rows']}\n\n"
        f"Pending rows: {summary['pending_rows']}\n\n"
        f"Replacement rows: {summary['replacement_rows']}\n\n"
        f"All required measurements present: {summary['all_required_measurements_present']}\n\n"
        f"Empirical response analysis blocked: {summary['empirical_response_analysis_blocked']}\n\n"
        f"Statistics computed: {summary['statistics_computed']}\n\n"
        "## Issues\n"
        f"{issues}\n"
    )
    (output_dir / REPORT_NAME).write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation-csv", type=Path, default=DEFAULT_ANNOTATION_CSV)
    parser.add_argument("--trial-records-csv", type=Path, default=DEFAULT_TRIAL_RECORDS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    if not args.annotation_csv.exists():
        print(f"Annotation CSV not found: {args.annotation_csv}", file=sys.stderr)
        return 2
    if not args.trial_records_csv.exists():
        print(f"Trial records CSV not found: {args.trial_records_csv}", file=sys.stderr)
        return 2
    summary = validate_annotation_intake(args.annotation_csv, args.trial_records_csv, args.output_dir)
    print(f"M19R-C annotation_intake_status={summary['status']}")
    print(f"M19R-C empirical_response_analysis_blocked={summary['empirical_response_analysis_blocked']}")
    print(f"M19R-C annotation_intake_issues={summary['issue_count']}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
