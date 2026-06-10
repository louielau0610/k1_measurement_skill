import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_m19r_c_prep_valid_annotations import COMMAND_VELOCITIES, SURFACES, generate_prep
from scripts.validate_m19_annotation_intake import validate_annotation_intake


TRIAL_FIELDS = [
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
    "command_window_sec",
    "analysis_window_start_sec",
    "analysis_window_end_sec",
    "trial_duration_sec",
    "notes",
]
ANNOTATION_FIELDS = [
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
    "annotation_method",
    "measurement_quality_flag",
    "annotation_notes",
]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def trial_row(trial_id, command="0.2", *, valid=True, reason="", notes=""):
    return {
        "trial_id": trial_id,
        "session_id": "fixture_session",
        "robot_id": "K1_fixture",
        "environment_id": "S1_lab_hard_floor",
        "surface_id": "S1_lab_hard_floor",
        "surface_type": "lab_hard_floor",
        "command_velocity": command,
        "valid": "TRUE" if valid else "FALSE",
        "invalid_reason": reason,
        "measured_actual_velocity": "",
        "yaw_drift_statistic": "",
        "command_window_sec": "6.0",
        "analysis_window_start_sec": "1.0",
        "analysis_window_end_sec": "6.0",
        "trial_duration_sec": "11.0" if valid else "1.0",
        "notes": notes,
    }


def annotation_row(trial_id, command="0.2", **updates):
    row = {
        "trial_id": trial_id,
        "session_id": "fixture_session",
        "robot_id": "K1_fixture",
        "environment_id": "S1_lab_hard_floor",
        "surface_type": "lab_hard_floor",
        "command_velocity": command,
        "valid": "TRUE",
        "measured_actual_velocity": "",
        "yaw_drift_statistic": "",
        "measurement_source": "pending",
        "annotation_method": "pending",
        "measurement_quality_flag": "pending",
        "annotation_notes": "pending_measurement_annotation",
    }
    row.update(updates)
    return row


def compact_fixture(tmp_path):
    trial_records = tmp_path / "trials.csv"
    annotations = tmp_path / "annotations.csv"
    trials = [
        trial_row("M19_valid_1", "0.2"),
        trial_row("M19_valid_2", "0.3"),
        trial_row("M19_REP_valid_3", "0.4"),
        trial_row("M19_invalid_debug", "0.2", valid=False, reason="execution_error: Move returned 400"),
    ]
    annotation_rows = [
        annotation_row("M19_valid_1", "0.2"),
        annotation_row("M19_valid_2", "0.3"),
        annotation_row("M19_REP_valid_3", "0.4"),
    ]
    write_csv(trial_records, trials, TRIAL_FIELDS)
    write_csv(annotations, annotation_rows, ANNOTATION_FIELDS)
    return trial_records, annotations, annotation_rows


def test_pass_on_empty_but_structured_annotation_template(tmp_path):
    trial_records, annotations, _ = compact_fixture(tmp_path)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "pass"
    assert summary["row_count"] == 3
    assert summary["pending_rows"] == 3
    assert summary["measured_rows"] == 0
    assert summary["empirical_response_analysis_blocked"]


def test_pass_on_partially_filled_real_measurements(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    rows[0].update(
        {
            "measured_actual_velocity": "0.18",
            "yaw_drift_statistic": "2.5",
            "measurement_source": "video_distance_time",
            "annotation_method": "manual_frame_count",
            "measurement_quality_flag": "low",
        }
    )
    write_csv(annotations, rows, ANNOTATION_FIELDS)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "pass"
    assert summary["measured_rows"] == 1
    assert summary["complete_measurement_rows"] == 1
    assert summary["empirical_response_analysis_blocked"]
    assert not summary["statistics_computed"]


def test_fail_on_fabricated_placeholder_values(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    rows[0]["measurement_source"] = "fabricated"
    write_csv(annotations, rows, ANNOTATION_FIELDS)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "fail"
    assert any("placeholder" in issue["message"] for issue in summary["issues"])


def test_fail_on_duplicate_trial_ids(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    rows[1]["trial_id"] = rows[0]["trial_id"]
    write_csv(annotations, rows, ANNOTATION_FIELDS)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "fail"
    assert summary["duplicate_trial_ids"] == ["M19_valid_1"]


def test_fail_on_missing_required_columns(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    reduced_fields = [field for field in ANNOTATION_FIELDS if field != "measurement_source"]
    write_csv(annotations, rows, reduced_fields)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "fail"
    assert any(issue["field"] == "measurement_source" for issue in summary["issues"])


def test_fail_on_invalid_quality_flags(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    rows[0]["measurement_quality_flag"] = "excellent"
    write_csv(annotations, rows, ANNOTATION_FIELDS)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "fail"
    assert any("quality flag" in issue["message"] for issue in summary["issues"])


def test_fail_on_invalid_debug_trial_ids_included(tmp_path):
    trial_records, annotations, rows = compact_fixture(tmp_path)
    rows.append(annotation_row("M19_invalid_debug", "0.2"))
    write_csv(annotations, rows, ANNOTATION_FIELDS)

    summary = validate_annotation_intake(annotations, trial_records, tmp_path / "out")

    assert summary["status"] == "fail"
    assert summary["invalid_debug_trial_ids_included"] == ["M19_invalid_debug"]


def test_realistic_72_row_template_passes_pending_intake_qc(tmp_path):
    trial_records = tmp_path / "m19_trial_records.csv"
    template = tmp_path / "m19_valid_trial_measurement_annotation_template.csv"
    output_dir = tmp_path / "out"
    rows = []
    replacements = {
        ("S1_lab_hard_floor", 0.10): "M19_REP_S1_lab_hard_floor_U010_R4",
        ("S1_lab_hard_floor", 0.40): "M19_REP_S1_lab_hard_floor_U040_R4",
        ("S3_artificial_turf", 0.20): "M19_REP_S3_artificial_turf_U020_R4",
        ("S3_artificial_turf", 0.30): "M19_REP_S3_artificial_turf_U030_R4",
        ("S3_artificial_turf", 0.60): "M19_REP_S3_artificial_turf_U060_R4",
    }
    for surface in SURFACES:
        for command in COMMAND_VELOCITIES:
            replacement = replacements.get((surface, command))
            if replacement:
                rows.append(trial_row(replacement, str(command)))
                rows.append(trial_row(f"M19_{surface}_B2_U{int(command * 100):03d}_R2", str(command)))
                rows.append(trial_row(f"M19_{surface}_B3_U{int(command * 100):03d}_R3", str(command)))
                rows.append(trial_row(f"M19_{surface}_B1_U{int(command * 100):03d}_R1", str(command), valid=False, reason="execution_error: Move returned 400"))
            else:
                for repeat in (1, 2, 3):
                    rows.append(trial_row(f"M19_{surface}_B{repeat}_U{int(command * 100):03d}_R{repeat}", str(command)))
    write_csv(trial_records, rows, TRIAL_FIELDS)
    generate_prep(trial_records, template, output_dir)

    summary = validate_annotation_intake(template, trial_records, output_dir)

    assert summary["status"] == "pass"
    assert summary["expected_trial_id_count"] == 72
    assert summary["row_count"] == 72
    assert summary["replacement_rows"] == 5
    assert summary["pending_rows"] == 72
