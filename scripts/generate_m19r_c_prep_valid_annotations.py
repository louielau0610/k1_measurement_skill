"""Generate M19R-C valid-only measurement annotation prep artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_m19r_b_completion_pack import ANNOTATION_COLUMNS
from scripts.qc_m19_real_test_records import debug_indicator, parse_bool, parse_float

INPUT_CSV = Path("data/m19_repeated_validation_inputs/m19_trial_records.csv")
VALID_TEMPLATE_CSV = Path("data/m19_repeated_validation_inputs/m19_valid_trial_measurement_annotation_template.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
COMMAND_VELOCITIES = [0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]
SURFACES = ["S1_lab_hard_floor", "S2_marble_floor", "S3_artificial_turf"]
OPTIONAL_COLUMNS = [
    "raw_log_path",
    "normalized_record_path",
    "timestamp",
    "command_window_sec",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "block_index",
    "repeat_index",
    "trial_duration_sec",
]
VALID_TEMPLATE_COLUMNS = ANNOTATION_COLUMNS + OPTIONAL_COLUMNS


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def is_execution_valid(row: dict[str, str]) -> bool:
    return parse_bool(row.get("valid")) and not row.get("invalid_reason", "").strip() and not debug_indicator(row)


def surface_id(row: dict[str, str]) -> str:
    return row.get("surface_id") or row.get("environment_id") or ""


def build_valid_annotation_rows(valid_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    annotations: list[dict[str, str]] = []
    for row in valid_rows:
        item = {
            "trial_id": row.get("trial_id", ""),
            "session_id": row.get("session_id", ""),
            "robot_id": row.get("robot_id", ""),
            "environment_id": row.get("environment_id", surface_id(row)),
            "surface_type": row.get("surface_type", ""),
            "command_velocity": row.get("command_velocity", ""),
            "valid": "TRUE",
            "measured_actual_velocity": "",
            "yaw_drift_statistic": "",
            "measurement_source": "pending",
            "measurement_method": "pending",
            "distance_m": "",
            "time_sec": "",
            "start_yaw_deg": "",
            "end_yaw_deg": "",
            "measurement_confidence": "pending",
            "annotation_notes": "pending_measurement_annotation",
        }
        for column in OPTIONAL_COLUMNS:
            item[column] = row.get(column, "")
        annotations.append(item)
    return annotations


def build_worklist(valid_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in valid_rows:
        command = parse_float(row.get("command_velocity"))
        if command is not None:
            grouped[(surface_id(row), command)].append(row)
    worklist: list[dict[str, Any]] = []
    for surface in SURFACES:
        for command in COMMAND_VELOCITIES:
            trials = sorted(grouped.get((surface, command), []), key=lambda row: row.get("trial_id", ""))
            worklist.append(
                {
                    "surface_id": surface,
                    "environment_id": surface,
                    "command_velocity": command,
                    "n_valid_trials": len(trials),
                    "trial_ids": ";".join(row.get("trial_id", "") for row in trials),
                    "has_replacement": "yes" if any(row.get("trial_id", "").startswith("M19_REP_") for row in trials) else "no",
                    "measurement_status": "pending_measurement_annotation",
                }
            )
    return worklist


def summarize(rows: list[dict[str, str]], valid_rows: list[dict[str, str]], worklist: list[dict[str, Any]], annotation_rows: list[dict[str, str]], input_csv: Path, template_csv: Path) -> dict[str, Any]:
    invalid_debug_rows = len(rows) - len(valid_rows)
    replacement_rows = sum(1 for row in valid_rows if row.get("trial_id", "").startswith("M19_REP_"))
    per_surface: dict[str, dict[str, int]] = {}
    for surface in SURFACES:
        surface_rows = [row for row in rows if surface_id(row) == surface]
        surface_valid = [row for row in valid_rows if surface_id(row) == surface]
        per_surface[surface] = {"total": len(surface_rows), "valid": len(surface_valid)}
    measurements_filled = any(row["measured_actual_velocity"] or row["yaw_drift_statistic"] for row in annotation_rows)
    return {
        "milestone": "M19R-C-prep",
        "timestamp": datetime.now().isoformat(),
        "branch": "feature/m19r-c-prep-valid-annotation-template",
        "trial_records_csv": str(input_csv),
        "valid_template_csv": str(template_csv),
        "total_trial_record_rows": len(rows),
        "execution_valid_rows": len(valid_rows),
        "invalid_debug_rows": invalid_debug_rows,
        "replacement_rows": replacement_rows,
        "valid_template_rows": len(annotation_rows),
        "cells_with_3_valid": sum(1 for item in worklist if item["n_valid_trials"] == 3),
        "total_cells": len(worklist),
        "all_cells_have_3_valid_trials": all(item["n_valid_trials"] == 3 for item in worklist),
        "per_surface": per_surface,
        "real_measurements_filled": measurements_filled,
        "measured_actual_velocity_available": False,
        "yaw_drift_statistic_available": False,
        "empirical_response_analysis_blocked": True,
        "worklist_rows": len(worklist),
    }


def render_worklist(worklist: list[dict[str, Any]]) -> str:
    lines = [
        "# M19R-C Annotation Worklist",
        "",
        f"**Total valid trials**: {sum(item['n_valid_trials'] for item in worklist)}",
        f"**Surface-speed cells**: {len(worklist)}",
        "",
        "Each cell below requires manual or video-assisted measurement annotation.",
        "Fill `measured_actual_velocity` and `yaw_drift_statistic` from acceptable evidence.",
        "",
        "| surface_id | command_velocity | n_valid | trial_ids | has_replacement | measurement_status |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for item in worklist:
        lines.append(
            f"| {item['surface_id']} | {item['command_velocity']:.2g} | {item['n_valid_trials']} | {item['trial_ids']} | {item['has_replacement']} | {item['measurement_status']} |"
        )
    lines.extend(
        [
            "",
            "## Instructions",
            "",
            "1. For each trial, extract actual forward velocity from log, video, or manual distance/time.",
            "2. Extract yaw drift from log or manual compass reading.",
            "3. Fill only the `measured_actual_velocity` and `yaw_drift_statistic` columns.",
            "4. Update `measurement_source`, `measurement_method`, and `measurement_confidence`.",
            "5. Do NOT copy command velocity as measured velocity.",
            "6. Run `scripts/qc_m19_measurement_annotations.py` after filling to validate.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_report(summary: dict[str, Any]) -> str:
    surface_lines = "\n".join(
        f"| {surface} | {counts['total']} | {counts['valid']} |"
        for surface, counts in summary["per_surface"].items()
    )
    return (
        "# M19R-C Prep Summary\n\n"
        f"**Milestone**: {summary['milestone']}\n"
        f"**Timestamp**: {summary['timestamp']}\n"
        f"**Branch**: `{summary['branch']}`\n\n"
        "## Status\n\n"
        "- Replacement trials completed execution-level M19 design.\n"
        f"- **{summary['execution_valid_rows']}** execution-valid trials are available.\n"
        f"- Annotation template has **{summary['valid_template_rows']}** rows.\n"
        f"- **{summary['invalid_debug_rows']}** invalid/debug rows remain excluded.\n"
        "- Measured actual velocity and yaw drift remain **missing**.\n"
        "- Empirical response analysis is still **blocked** pending annotation.\n\n"
        "## Data Integrity\n\n"
        "| metric | value |\n"
        "| --- | ---: |\n"
        f"| Total trial record rows | {summary['total_trial_record_rows']} |\n"
        f"| Execution-valid rows | {summary['execution_valid_rows']} |\n"
        f"| Invalid/debug rows | {summary['invalid_debug_rows']} |\n"
        f"| Replacement rows | {summary['replacement_rows']} |\n"
        f"| Valid template rows | {summary['valid_template_rows']} |\n"
        f"| Surface-speed cells | {summary['total_cells']} |\n"
        f"| Cells with 3 valid trials | {summary['cells_with_3_valid']} |\n"
        f"| All cells have 3 valid | {summary['all_cells_have_3_valid_trials']} |\n\n"
        "## Per-Surface Breakdown\n\n"
        "| surface | total rows | valid rows |\n"
        "| --- | ---: | ---: |\n"
        f"{surface_lines}\n\n"
        "No response statistics, response plots, or empirical risk-map claims are generated by this prep step.\n"
    )


def generate_prep(input_csv: Path, template_csv: Path, output_dir: Path) -> dict[str, Any]:
    rows = read_csv(input_csv)
    valid_rows = [row for row in rows if is_execution_valid(row)]
    annotation_rows = build_valid_annotation_rows(valid_rows)
    worklist = build_worklist(valid_rows)
    write_csv(template_csv, annotation_rows, VALID_TEMPLATE_COLUMNS)
    worklist_fields = ["surface_id", "environment_id", "command_velocity", "n_valid_trials", "trial_ids", "has_replacement", "measurement_status"]
    write_csv(output_dir / "m19r_c_prep_annotation_worklist.csv", worklist, worklist_fields)
    (output_dir / "m19r_c_prep_annotation_worklist.md").write_text(render_worklist(worklist), encoding="utf-8")
    summary = summarize(rows, valid_rows, worklist, annotation_rows, input_csv, template_csv)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19r_c_prep_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19r_c_prep_report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=INPUT_CSV)
    parser.add_argument("--template-csv", type=Path, default=VALID_TEMPLATE_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    if not args.input_csv.exists():
        print(f"Input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    summary = generate_prep(args.input_csv, args.template_csv, args.output_dir)
    print(f"M19R-C total_rows={summary['total_trial_record_rows']}")
    print(f"M19R-C valid_template_rows={summary['valid_template_rows']}")
    print(f"M19R-C all_cells_have_3_valid_trials={summary['all_cells_have_3_valid_trials']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
