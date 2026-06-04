from __future__ import annotations

from pathlib import Path

import pytest

from k1_measurement.report_generator import (
    generate_markdown_report,
    generate_report_from_profile,
    load_profile,
    save_markdown_report,
)


DUMMY_PROFILE = "examples/dummy_processed_environment_profile.json"


def test_load_profile_can_load_dummy_profile() -> None:
    profile = load_profile(DUMMY_PROFILE)

    assert profile["metadata"]["robot"] == "Booster K1"


def test_generate_markdown_report_is_non_empty() -> None:
    report = generate_markdown_report(load_profile(DUMMY_PROFILE))

    assert report
    assert "K1 Measurement Report" in report


def test_report_contains_dummy_warning() -> None:
    report = generate_markdown_report(load_profile(DUMMY_PROFILE))

    assert "不是真实 K1 测量结果" in report
    assert "Dummy data only" in report


def test_report_contains_velocity_profile_table_fields() -> None:
    report = generate_markdown_report(load_profile(DUMMY_PROFILE))

    assert "v_x_cmd (m/s)" in report
    assert "v_x_actual_mean (m/s)" in report
    assert "speed_gain_mean" in report
    assert "absolute_error_mean (m/s)" in report


def test_report_contains_downstream_usage_section() -> None:
    report = generate_markdown_report(load_profile(DUMMY_PROFILE))

    assert "## 下游使用说明" in report
    assert "recommended_for_compensation" in report
    assert "extrapolation_allowed" in report


def test_report_states_compensation_not_implemented() -> None:
    report = generate_markdown_report(load_profile(DUMMY_PROFILE))

    assert "不实现 velocity compensation" in report


def test_save_markdown_report_writes_file(tmp_path: Path) -> None:
    output = tmp_path / "report.md"

    save_markdown_report("# Report\n", str(output))

    assert output.read_text(encoding="utf-8") == "# Report\n"


def test_generate_report_from_profile_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "report.md"

    result = generate_report_from_profile(DUMMY_PROFILE, str(output))

    assert result == str(output)
    assert output.exists()
    assert "K1 Measurement Report" in output.read_text(encoding="utf-8")


def test_invalid_profile_path_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_profile("missing_profile.json")
