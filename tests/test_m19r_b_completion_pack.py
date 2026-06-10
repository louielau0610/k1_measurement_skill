import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_m19r_b_completion_pack import (
    ANNOTATION_COLUMNS,
    derive_replacement_plan,
    generate_pack,
)
from scripts.qc_m19_measurement_annotations import qc_annotations


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def trial(surface, command, repeat, *, valid="TRUE", reason="", actual="", yaw=""):
    return {
        "trial_id": f"M19_{surface}_B1_U{int(command * 100):03d}_R{repeat}",
        "session_id": "fixture_session",
        "robot_id": "K1_fixture",
        "environment_id": surface,
        "surface_id": surface,
        "surface_type": surface.split("_", 1)[1],
        "command_velocity": str(command),
        "valid": valid,
        "invalid_reason": reason,
        "measured_actual_velocity": actual,
        "yaw_drift_statistic": yaw,
    }


def qc_summary():
    return {
        "per_surface_speed_cell": [
            {"surface_id": "S1_lab_hard_floor", "command_velocity": 0.1, "n_total": 3, "n_valid": 2, "complete": False},
            {"surface_id": "S1_lab_hard_floor", "command_velocity": 0.2, "n_total": 3, "n_valid": 3, "complete": True},
        ]
    }


def annotation_row(**updates):
    row = {column: "" for column in ANNOTATION_COLUMNS}
    row.update(
        {
            "trial_id": "M19_fixture",
            "command_velocity": "0.3",
            "valid": "TRUE",
            "measurement_source": "pending",
            "measurement_method": "pending",
            "measurement_confidence": "pending",
        }
    )
    row.update(updates)
    return row


def test_missing_cell_detection_and_replacement_plan():
    rows = [
        trial("S1_lab_hard_floor", 0.1, 1),
        trial("S1_lab_hard_floor", 0.1, 2),
        trial("S1_lab_hard_floor", 0.1, 3, valid="FALSE", reason="execution_error: Move returned 400"),
        trial("S1_lab_hard_floor", 0.2, 1),
        trial("S1_lab_hard_floor", 0.2, 2),
        trial("S1_lab_hard_floor", 0.2, 3),
    ]
    plan = derive_replacement_plan(qc_summary(), rows)

    assert len(plan) == 1
    assert plan[0]["surface_id"] == "S1_lab_hard_floor"
    assert plan[0]["current_valid_count"] == 2
    assert plan[0]["replacement_trial_id"] == "M19_REP_S1_lab_hard_floor_U010_R4"
    assert "M19_S1_lab_hard_floor_B1_U010_R3" in plan[0]["invalid_debug_trial_ids"]


def test_generate_pack_outputs_template_and_plan(tmp_path):
    input_csv = tmp_path / "m19_trial_records.csv"
    summary_path = tmp_path / "m19r_qc_summary.json"
    output_dir = tmp_path / "out"
    annotation_template = tmp_path / "data" / "m19_measurement_annotation_template.csv"
    fields = [
        "trial_id",
        "session_id",
        "robot_id",
        "environment_id",
        "surface_id",
        "surface_type",
        "command_velocity",
        "valid",
        "invalid_reason",
        "measured_actual_velocity",
        "yaw_drift_statistic",
    ]
    rows = [
        trial("S1_lab_hard_floor", 0.1, 1),
        trial("S1_lab_hard_floor", 0.1, 2),
        trial("S1_lab_hard_floor", 0.1, 3, valid="FALSE", reason="execution_error: Move returned 400"),
    ]
    write_csv(input_csv, rows, fields)
    summary_path.write_text(json.dumps(qc_summary()), encoding="utf-8")

    summary = generate_pack(input_csv, summary_path, output_dir, annotation_template)

    assert summary["replacement_trials_required"] == 1
    assert summary["annotation_template_rows"] == 3
    assert summary["real_measurements_prefilled"] == 0
    assert (output_dir / "m19r_replacement_trial_plan.csv").exists()
    assert (output_dir / "m19r_replacement_trial_plan.md").exists()
    assert annotation_template.exists()
    template_rows = list(csv.DictReader(annotation_template.open(encoding="utf-8")))
    assert template_rows[0]["measured_actual_velocity"] == ""
    assert template_rows[-1]["trial_id"].startswith("M19_REP_")


def test_annotation_qc_accepts_pending_template(tmp_path):
    annotation_csv = tmp_path / "annotation.csv"
    write_csv(annotation_csv, [annotation_row()], ANNOTATION_COLUMNS)

    summary = qc_annotations(annotation_csv, tmp_path / "out")

    assert summary["status"] == "pass"
    assert summary["pending_rows"] == 1
    assert (tmp_path / "out" / "m19r_b_annotation_qc_summary.json").exists()
    assert (tmp_path / "out" / "m19r_b_annotation_qc_report.md").exists()


def test_annotation_qc_rejects_bad_numeric_fields(tmp_path):
    annotation_csv = tmp_path / "annotation.csv"
    write_csv(annotation_csv, [annotation_row(measured_actual_velocity="-0.1", yaw_drift_statistic="-2")], ANNOTATION_COLUMNS)

    summary = qc_annotations(annotation_csv, tmp_path / "out")

    assert summary["status"] == "fail"
    messages = [issue["message"] for issue in summary["issues"]]
    assert "actual velocity must be nonnegative" in messages
    assert "yaw drift must be nonnegative" in messages


def test_annotation_qc_rejects_all_actuals_equal_command(tmp_path):
    annotation_csv = tmp_path / "annotation.csv"
    rows = [
        annotation_row(trial_id="a", command_velocity="0.3", measured_actual_velocity="0.3", yaw_drift_statistic="1", measurement_source="normalized_log", measurement_method="velocity_field", measurement_confidence="high"),
        annotation_row(trial_id="b", command_velocity="0.4", measured_actual_velocity="0.4", yaw_drift_statistic="1", measurement_source="normalized_log", measurement_method="velocity_field", measurement_confidence="high"),
    ]
    write_csv(annotation_csv, rows, ANNOTATION_COLUMNS)

    summary = qc_annotations(annotation_csv, tmp_path / "out")

    assert summary["status"] == "fail"
    assert any("exactly equal command velocity" in issue["message"] for issue in summary["issues"])


def test_annotation_qc_rejects_fabricated_source_labels(tmp_path):
    annotation_csv = tmp_path / "annotation.csv"
    rows = [
        annotation_row(
            measured_actual_velocity="0.21",
            yaw_drift_statistic="1.0",
            measurement_source="fabricated",
            measurement_method="manual_distance_time",
            measurement_confidence="low",
        )
    ]
    write_csv(annotation_csv, rows, ANNOTATION_COLUMNS)

    summary = qc_annotations(annotation_csv, tmp_path / "out")

    assert summary["status"] == "fail"
    assert any("synthetic/fabricated" in issue["message"] for issue in summary["issues"])
