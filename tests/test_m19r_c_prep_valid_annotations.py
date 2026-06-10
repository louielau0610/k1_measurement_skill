import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_m19r_c_prep_valid_annotations import (
    COMMAND_VELOCITIES,
    SURFACES,
    generate_prep,
    is_execution_valid,
)
from scripts.qc_m19_measurement_annotations import qc_annotations


FIELDS = [
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
    "raw_log_path",
    "normalized_record_path",
    "timestamp",
    "command_window_sec",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "block_index",
    "repeat_index",
    "trial_duration_sec",
    "notes",
]

REPLACEMENTS = {
    ("S1_lab_hard_floor", 0.10): "M19_REP_S1_lab_hard_floor_U010_R4",
    ("S1_lab_hard_floor", 0.40): "M19_REP_S1_lab_hard_floor_U040_R4",
    ("S3_artificial_turf", 0.20): "M19_REP_S3_artificial_turf_U020_R4",
    ("S3_artificial_turf", 0.30): "M19_REP_S3_artificial_turf_U030_R4",
    ("S3_artificial_turf", 0.60): "M19_REP_S3_artificial_turf_U060_R4",
}


def speed_code(command):
    return f"U{int(round(command * 100)):03d}"


def row(surface, command, repeat, *, trial_id=None, valid=True, reason="", notes=""):
    return {
        "trial_id": trial_id or f"M19_{surface}_B{repeat}_{speed_code(command)}_R{repeat}",
        "session_id": "fixture_session",
        "robot_id": "K1_fixture",
        "environment_id": surface,
        "surface_id": surface,
        "surface_type": surface.split("_", 1)[1],
        "command_velocity": str(command),
        "valid": "TRUE" if valid else "FALSE",
        "invalid_reason": reason,
        "measured_actual_velocity": "",
        "yaw_drift_statistic": "",
        "raw_log_path": "",
        "normalized_record_path": "",
        "timestamp": "",
        "command_window_sec": "6.0",
        "analysis_window_start_sec": "1.0",
        "analysis_window_end_sec": "6.0",
        "block_index": str(repeat),
        "repeat_index": str(repeat),
        "trial_duration_sec": "11.0" if valid else "1.0",
        "notes": notes,
    }


def fixture_rows():
    rows = []
    for surface in SURFACES:
        for command in COMMAND_VELOCITIES:
            replacement_id = REPLACEMENTS.get((surface, command))
            if replacement_id:
                rows.append(row(surface, command, 4, trial_id=replacement_id))
                rows.append(row(surface, command, 2))
                rows.append(row(surface, command, 3))
                rows.append(
                    row(
                        surface,
                        command,
                        1,
                        valid=False,
                        reason="execution_error:RuntimeError:Move(vx=0.0, vy=0.0, wz=0.0) returned 400",
                        notes="script caught execution error",
                    )
                )
            else:
                rows.extend(row(surface, command, repeat) for repeat in (1, 2, 3))
    return rows


def write_records(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_execution_valid_excludes_invalid_debug_row():
    invalid = row("S1_lab_hard_floor", 0.1, 1, valid=False, reason="execution_error: Move returned 400")
    valid = row("S1_lab_hard_floor", 0.1, 2)
    assert not is_execution_valid(invalid)
    assert is_execution_valid(valid)


def test_generate_valid_only_template_and_worklist(tmp_path):
    input_csv = tmp_path / "m19_trial_records.csv"
    template_csv = tmp_path / "m19_valid_trial_measurement_annotation_template.csv"
    output_dir = tmp_path / "out"
    rows = fixture_rows()
    write_records(input_csv, rows)

    summary = generate_prep(input_csv, template_csv, output_dir)

    assert summary["total_trial_record_rows"] == 77
    assert summary["execution_valid_rows"] == 72
    assert summary["invalid_debug_rows"] == 5
    assert summary["replacement_rows"] == 5
    assert summary["valid_template_rows"] == 72
    assert summary["all_cells_have_3_valid_trials"]
    template_rows = list(csv.DictReader(template_csv.open(encoding="utf-8")))
    assert len(template_rows) == 72
    assert all(item["valid"] == "TRUE" for item in template_rows)
    assert all(not item["measured_actual_velocity"] for item in template_rows)
    assert all(not item["yaw_drift_statistic"] for item in template_rows)
    assert sum(1 for item in template_rows if item["trial_id"].startswith("M19_REP_")) == 5
    assert not any("returned 400" in item.get("invalid_reason", "") for item in template_rows)


def test_worklist_has_24_complete_cells(tmp_path):
    input_csv = tmp_path / "m19_trial_records.csv"
    template_csv = tmp_path / "template.csv"
    output_dir = tmp_path / "out"
    write_records(input_csv, fixture_rows())

    generate_prep(input_csv, template_csv, output_dir)

    worklist = list(csv.DictReader((output_dir / "m19r_c_prep_annotation_worklist.csv").open(encoding="utf-8")))
    assert len(worklist) == 24
    assert all(item["n_valid_trials"] == "3" for item in worklist)
    assert sum(1 for item in worklist if item["has_replacement"] == "yes") == 5
    assert all(item["measurement_status"] == "pending_measurement_annotation" for item in worklist)


def test_valid_only_template_passes_pending_annotation_qc(tmp_path):
    input_csv = tmp_path / "m19_trial_records.csv"
    template_csv = tmp_path / "template.csv"
    output_dir = tmp_path / "out"
    write_records(input_csv, fixture_rows())
    generate_prep(input_csv, template_csv, output_dir)

    qc = qc_annotations(
        template_csv,
        output_dir,
        "m19r_c_annotation_qc_summary.json",
        "m19r_c_annotation_qc_report.md",
        "M19R-C Measurement Annotation QC Report",
    )

    assert qc["status"] == "pass"
    assert qc["row_count"] == 72
    assert qc["measured_rows"] == 0
    assert qc["pending_rows"] == 72
    assert qc["replacement_rows"] == 5
    assert (output_dir / "m19r_c_annotation_qc_summary.json").exists()
    assert (output_dir / "m19r_c_annotation_qc_report.md").exists()


def test_no_empirical_statistics_are_generated(tmp_path):
    input_csv = tmp_path / "m19_trial_records.csv"
    template_csv = tmp_path / "template.csv"
    output_dir = tmp_path / "out"
    write_records(input_csv, fixture_rows())

    generate_prep(input_csv, template_csv, output_dir)

    generated = {path.name for path in output_dir.iterdir()}
    assert "surface_response_statistics.csv" not in generated
    assert "region_classification.csv" not in generated
    assert "yaw_drift_summary.csv" not in generated
