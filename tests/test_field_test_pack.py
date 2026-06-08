from __future__ import annotations

from pathlib import Path

from k1_measurement.field_test_pack import GROUND_TRUTH_COLUMNS, write_ground_truth_trial_sheet


def test_field_test_template_generation(tmp_path: Path) -> None:
    output = write_ground_truth_trial_sheet(tmp_path / "ground_truth_trial_sheet.csv")

    assert output.exists()
    assert output.read_text(encoding="utf-8").strip().split(",") == GROUND_TRUTH_COLUMNS


def test_m7_does_not_create_full_ros_package_files() -> None:
    assert not Path("package.xml").exists()
    assert not Path("CMakeLists.txt").exists()
    assert not Path("resource").exists()
