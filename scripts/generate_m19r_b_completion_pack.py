"""Generate the M19R-B replacement-trial and measurement annotation pack."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.qc_m19_real_test_records import debug_indicator, parse_bool, parse_float

OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
LOCAL_INPUT_CSV = Path("data/m19_repeated_validation_inputs/m19_trial_records.csv")
ANNOTATION_TEMPLATE = Path("data/m19_repeated_validation_inputs/m19_measurement_annotation_template.csv")
REQUIRED_VALID_COUNT = 3

ANNOTATION_COLUMNS = [
    "trial_id",
    "session_id",
    "robot_id",
    "environment_id",
    "surface_type",
    "command_velocity",
    "valid",
    "measured_actual_velocity",
    "yaw_drift_statistic",
    "measurement_source",
    "measurement_method",
    "distance_m",
    "time_sec",
    "start_yaw_deg",
    "end_yaw_deg",
    "measurement_confidence",
    "annotation_notes",
]


def default_input_csv() -> Path:
    if LOCAL_INPUT_CSV.exists():
        return LOCAL_INPUT_CSV
    return Path.cwd().resolve().parent.parent / "data" / "m19_repeated_validation_inputs" / "m19_trial_records.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def speed_code(command_velocity: float) -> str:
    return f"U{int(round(command_velocity * 100)):03d}"


def cell_key(row: dict[str, str]) -> tuple[str, float | None]:
    surface = row.get("surface_id") or row.get("environment_id") or ""
    return surface, parse_float(row.get("command_velocity"))


def derive_replacement_plan(qc_summary: dict[str, Any], rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for cell in qc_summary.get("per_surface_speed_cell", []):
        n_valid = int(cell.get("n_valid", 0))
        if n_valid >= REQUIRED_VALID_COUNT:
            continue
        surface_id = str(cell["surface_id"])
        command_velocity = float(cell["command_velocity"])
        matching_rows = [
            row for row in rows
            if cell_key(row) == (surface_id, command_velocity)
        ]
        invalid_ids = [
            row.get("trial_id", "")
            for row in matching_rows
            if (not parse_bool(row.get("valid"))) or debug_indicator(row)
        ]
        surface_type = next((row.get("surface_type", "") for row in matching_rows if row.get("surface_type")), "")
        missing_count = REQUIRED_VALID_COUNT - n_valid
        for offset in range(missing_count):
            replacement_index = REQUIRED_VALID_COUNT + offset + 1
            plan.append(
                {
                    "surface_id": surface_id,
                    "surface_type": surface_type,
                    "command_velocity": command_velocity,
                    "current_valid_count": n_valid,
                    "required_valid_count": REQUIRED_VALID_COUNT,
                    "missing_count": missing_count,
                    "invalid_debug_trial_ids": ";".join(invalid_ids),
                    "replacement_trial_id": f"M19_REP_{surface_id}_{speed_code(command_velocity)}_R{replacement_index}",
                    "recommended_command_profile": (
                        f"Prepare mode, walking mode, then Move(vx={command_velocity:.2f}, vy=0, wz=0) "
                        "for 6.0 s; analyze 1.0-6.0 s after command start."
                    ),
                    "notes": "Collect real actual velocity and yaw evidence; do not reuse command velocity as measurement.",
                }
            )
    return plan


def annotation_rows(rows: list[dict[str, str]], plan: list[dict[str, Any]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        if not parse_bool(row.get("valid")) or debug_indicator(row):
            continue
        output.append(
            {
                "trial_id": row.get("trial_id", ""),
                "session_id": row.get("session_id", ""),
                "robot_id": row.get("robot_id", ""),
                "environment_id": row.get("environment_id", ""),
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
                "annotation_notes": "pending_measurement_extraction",
            }
        )
    for replacement in plan:
        output.append(
            {
                "trial_id": replacement["replacement_trial_id"],
                "session_id": "replacement_pending",
                "robot_id": "K1_001",
                "environment_id": replacement["surface_id"],
                "surface_type": replacement["surface_type"],
                "command_velocity": f"{replacement['command_velocity']:.2f}".rstrip("0").rstrip("."),
                "valid": "REPLACEMENT_PENDING",
                "measured_actual_velocity": "",
                "yaw_drift_statistic": "",
                "measurement_source": "pending",
                "measurement_method": "pending",
                "distance_m": "",
                "time_sec": "",
                "start_yaw_deg": "",
                "end_yaw_deg": "",
                "measurement_confidence": "pending",
                "annotation_notes": "replacement trial placeholder; measurements must be filled only after execution",
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def render_plan(plan: list[dict[str, Any]]) -> str:
    lines = [
        "# M19R-B Replacement Trial Plan",
        "",
        "This plan lists only surface-speed cells with fewer than 3 valid formal trials after M19R QC.",
        "It does not modify empirical statistics and does not fabricate measurements.",
        "",
        "| surface_id | command_velocity | current_valid_count | missing_count | replacement_trial_id | invalid/debug trial IDs |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for item in plan:
        lines.append(
            "| {surface_id} | {command_velocity:.2f} | {current_valid_count} | {missing_count} | `{replacement_trial_id}` | {invalid_debug_trial_ids} |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "Recommended command profile for each replacement row: prepare mode, walking mode, then forward `Move(vx, 0, 0)` for 6.0 s with analysis over 1.0-6.0 s after command start.",
            "Replacement measurements must be collected from logs, video-assisted distance-time evidence, or documented manual distance-time/yaw readings.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_pack(input_csv: Path, qc_summary_path: Path, output_dir: Path, annotation_template: Path) -> dict[str, Any]:
    rows = read_csv(input_csv)
    qc_summary = json.loads(qc_summary_path.read_text(encoding="utf-8"))
    plan = derive_replacement_plan(qc_summary, rows)
    plan_fields = [
        "surface_id",
        "surface_type",
        "command_velocity",
        "current_valid_count",
        "required_valid_count",
        "missing_count",
        "invalid_debug_trial_ids",
        "replacement_trial_id",
        "recommended_command_profile",
        "notes",
    ]
    write_csv(output_dir / "m19r_replacement_trial_plan.csv", plan, plan_fields)
    (output_dir / "m19r_replacement_trial_plan.md").write_text(render_plan(plan), encoding="utf-8")
    annotations = annotation_rows(rows, plan)
    write_csv(annotation_template, annotations, ANNOTATION_COLUMNS)
    summary = {
        "input_csv": str(input_csv),
        "qc_summary": str(qc_summary_path),
        "missing_cells": [
            {
                "surface_id": item["surface_id"],
                "command_velocity": item["command_velocity"],
                "current_valid_count": item["current_valid_count"],
                "missing_count": item["missing_count"],
            }
            for item in plan
        ],
        "replacement_trials_required": len(plan),
        "annotation_template": str(annotation_template),
        "annotation_template_rows": len(annotations),
        "real_measurements_prefilled": 0,
    }
    (output_dir / "m19r_b_completion_pack_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=default_input_csv())
    parser.add_argument("--qc-summary", type=Path, default=OUTPUT_DIR / "m19r_qc_summary.json")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--annotation-template", type=Path, default=ANNOTATION_TEMPLATE)
    args = parser.parse_args(argv)
    if not args.input_csv.exists():
        print(f"Input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    if not args.qc_summary.exists():
        print(f"QC summary not found: {args.qc_summary}", file=sys.stderr)
        return 2
    summary = generate_pack(args.input_csv, args.qc_summary, args.output_dir, args.annotation_template)
    print(f"M19R-B replacement_trials_required={summary['replacement_trials_required']}")
    print(f"M19R-B annotation_template_rows={summary['annotation_template_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
