from __future__ import annotations

from pathlib import Path

from k1_measurement.field_session import (
    create_field_session,
    summarize_ground_truth_sheet,
    validate_ground_truth_columns,
)


def test_field_session_directory_creation_and_manifest(tmp_path: Path) -> None:
    manifest = create_field_session("test_session", tmp_path)
    session_dir = tmp_path / "test_session"

    assert (session_dir / "session_manifest.json").exists()
    assert (session_dir / "topic_mapping.yaml").exists()
    assert (session_dir / "field_session_config.yaml").exists()
    assert (session_dir / "ground_truth_trial_sheet.csv").exists()
    assert (session_dir / "trial_notes.md").exists()
    for name in ["raw_ros", "normalized", "processed", "plots", "reports"]:
        assert (session_dir / name).is_dir()
    assert manifest["session_id"] == "test_session"
    assert manifest["planned_velocity_groups"] == [0.1, 0.2, 0.3, 0.4]
    assert manifest["repeats_per_speed"] == 3


def test_ground_truth_sheet_required_column_validation(tmp_path: Path) -> None:
    manifest = create_field_session("test_session", tmp_path)
    summary = validate_ground_truth_columns(manifest["paths"]["ground_truth_trial_sheet"])

    assert summary["valid"] is True
    assert summary["missing_columns"] == []


def test_ground_truth_sheet_missing_planned_trials_summary(tmp_path: Path) -> None:
    manifest = create_field_session("test_session", tmp_path)
    summary = summarize_ground_truth_sheet(manifest["paths"]["ground_truth_trial_sheet"])

    assert summary["row_count"] == 0
    assert len(summary["missing_planned_trials"]) == 12


def test_m8_does_not_create_full_ros_package_layout(tmp_path: Path) -> None:
    create_field_session("test_session", tmp_path)

    assert not (tmp_path / "test_session" / "package.xml").exists()
    assert not (tmp_path / "test_session" / "CMakeLists.txt").exists()
    assert not (tmp_path / "test_session" / "resource").exists()
