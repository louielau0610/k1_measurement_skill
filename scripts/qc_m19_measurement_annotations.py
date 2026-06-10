"""QC a completed M19 measurement annotation CSV."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_m19r_b_completion_pack import ANNOTATION_COLUMNS, ANNOTATION_TEMPLATE
from scripts.qc_m19_real_test_records import parse_float

OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
ALLOWED_CONFIDENCE = {"high", "medium", "low", "pending"}
FORBIDDEN_SOURCE_LABELS = {"synthetic", "simulated", "dummy", "fabricated", "test_fixture", "fixture"}
NUMERIC_FIELDS = [
    "command_velocity",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "distance_m",
    "time_sec",
    "start_yaw_deg",
    "end_yaw_deg",
]


def read_annotations(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def has_measurement(row: dict[str, str]) -> bool:
    return bool(str(row.get("measured_actual_velocity", "")).strip() or str(row.get("yaw_drift_statistic", "")).strip())


def qc_annotations(
    annotation_csv: Path,
    output_dir: Path = OUTPUT_DIR,
    summary_name: str = "m19r_b_annotation_qc_summary.json",
    report_name: str = "m19r_b_annotation_qc_report.md",
    report_title: str = "M19R-B Measurement Annotation QC Report",
) -> dict[str, Any]:
    fieldnames, rows = read_annotations(annotation_csv)
    issues: list[dict[str, Any]] = []
    missing_columns = [column for column in ANNOTATION_COLUMNS if column not in fieldnames]
    for column in missing_columns:
        issues.append({"level": "error", "row": None, "field": column, "message": "required column missing"})

    measured_rows = 0
    pending_rows = 0
    measured_equal_command = 0
    replacement_rows = 0
    for index, row in enumerate(rows, start=2):
        trial_id = row.get("trial_id", "")
        is_replacement = trial_id.startswith("M19_REP_") or row.get("valid") == "REPLACEMENT_PENDING"
        if is_replacement:
            replacement_rows += 1
        for field in NUMERIC_FIELDS:
            value = str(row.get(field, "")).strip()
            if value and parse_float(value) is None:
                issues.append({"level": "error", "row": index, "field": field, "message": "numeric field does not parse"})
        actual = parse_float(row.get("measured_actual_velocity"))
        command = parse_float(row.get("command_velocity"))
        yaw = parse_float(row.get("yaw_drift_statistic"))
        if actual is not None and actual < 0:
            issues.append({"level": "error", "row": index, "field": "measured_actual_velocity", "message": "actual velocity must be nonnegative"})
        if yaw is not None and yaw < 0:
            issues.append({"level": "error", "row": index, "field": "yaw_drift_statistic", "message": "yaw drift must be nonnegative"})
        confidence = str(row.get("measurement_confidence", "")).strip().lower()
        if confidence not in ALLOWED_CONFIDENCE:
            issues.append({"level": "error", "row": index, "field": "measurement_confidence", "message": "invalid confidence label"})
        source = str(row.get("measurement_source", "")).strip().lower()
        method = str(row.get("measurement_method", "")).strip().lower()
        if source in FORBIDDEN_SOURCE_LABELS or method in FORBIDDEN_SOURCE_LABELS:
            issues.append({"level": "error", "row": index, "field": "measurement_source", "message": "synthetic/fabricated source labels are forbidden"})
        if has_measurement(row):
            measured_rows += 1
            if not source or source == "pending":
                issues.append({"level": "error", "row": index, "field": "measurement_source", "message": "measurement source required when measurements are present"})
            if not method or method == "pending":
                issues.append({"level": "error", "row": index, "field": "measurement_method", "message": "measurement method required when measurements are present"})
            if actual is not None and command is not None and abs(actual - command) < 1e-9:
                measured_equal_command += 1
        else:
            pending_rows += 1
            if confidence != "pending":
                issues.append({"level": "error", "row": index, "field": "measurement_confidence", "message": "rows missing measurements must be marked pending"})
    if measured_rows and measured_equal_command == measured_rows:
        issues.append(
            {
                "level": "error",
                "row": None,
                "field": "measured_actual_velocity",
                "message": "all measured actual velocities exactly equal command velocity",
            }
        )
    summary = {
        "annotation_csv": str(annotation_csv),
        "row_count": len(rows),
        "measured_rows": measured_rows,
        "pending_rows": pending_rows,
        "replacement_rows": replacement_rows,
        "issue_count": len(issues),
        "status": "pass" if not issues else "fail",
        "issues": issues,
    }
    write_outputs(output_dir, summary, summary_name, report_name, report_title)
    return summary


def write_outputs(
    output_dir: Path,
    summary: dict[str, Any],
    summary_name: str,
    report_name: str,
    report_title: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / summary_name).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    issue_lines = "\n".join(
        f"- row {issue['row']}: `{issue['field']}` - {issue['message']}" if issue["row"] else f"- `{issue['field']}` - {issue['message']}"
        for issue in summary["issues"]
    ) or "- None"
    report = (
        f"# {report_title}\n\n"
        f"Status: `{summary['status']}`\n\n"
        f"Rows: {summary['row_count']}\n\n"
        f"Measured rows: {summary['measured_rows']}\n\n"
        f"Pending rows: {summary['pending_rows']}\n\n"
        f"Replacement rows: {summary['replacement_rows']}\n\n"
        "## Issues\n"
        f"{issue_lines}\n"
    )
    (output_dir / report_name).write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation-csv", type=Path, default=ANNOTATION_TEMPLATE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--summary-name", default="m19r_b_annotation_qc_summary.json")
    parser.add_argument("--report-name", default="m19r_b_annotation_qc_report.md")
    parser.add_argument("--report-title", default="M19R-B Measurement Annotation QC Report")
    args = parser.parse_args(argv)
    if not args.annotation_csv.exists():
        print(f"Annotation CSV not found: {args.annotation_csv}", file=sys.stderr)
        return 2
    summary = qc_annotations(args.annotation_csv, args.output_dir, args.summary_name, args.report_name, args.report_title)
    print(f"M19R-B annotation_qc_status={summary['status']}")
    print(f"M19R-B annotation_qc_issues={summary['issue_count']}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
