import math

import pytest

from k1_measurement.metrics import (
    compute_absolute_error,
    compute_actual_velocity,
    compute_lateral_drift_rate,
    compute_relative_error,
    compute_speed_gain,
    compute_tracking_rmse,
    compute_yaw_drift_rate,
    summarize_trials,
)


def test_compute_actual_velocity_normal_case() -> None:
    assert compute_actual_velocity(0, 1.2, 0, 4) == pytest.approx(0.3)


def test_compute_actual_velocity_invalid_time_interval_raises() -> None:
    with pytest.raises(ValueError):
        compute_actual_velocity(0, 1.2, 4, 4)


def test_compute_speed_gain_normal_case() -> None:
    assert compute_speed_gain(0.24, 0.3) == pytest.approx(0.8)


def test_compute_speed_gain_zero_command_raises() -> None:
    with pytest.raises(ValueError):
        compute_speed_gain(0.24, 0.0)


def test_compute_absolute_error() -> None:
    assert compute_absolute_error(0.24, 0.3) == pytest.approx(-0.06)


def test_compute_relative_error_normal_case() -> None:
    assert compute_relative_error(0.24, 0.3) == pytest.approx(-0.2)


def test_compute_relative_error_zero_command_raises() -> None:
    with pytest.raises(ValueError):
        compute_relative_error(0.24, 0.0)


def test_compute_lateral_drift_rate_normal_case() -> None:
    assert compute_lateral_drift_rate(0, 0.15, 0, 5) == pytest.approx(0.03)


def test_compute_lateral_drift_rate_invalid_time_interval_raises() -> None:
    with pytest.raises(ValueError):
        compute_lateral_drift_rate(0, 0.15, 5, 0)


def test_compute_yaw_drift_rate_normal_case() -> None:
    assert compute_yaw_drift_rate(0, 0.1, 0, 5) == pytest.approx(0.02)


def test_compute_yaw_drift_rate_invalid_time_interval_raises() -> None:
    with pytest.raises(ValueError):
        compute_yaw_drift_rate(0, 0.1, 5, 5)


def test_compute_tracking_rmse_normal_case() -> None:
    expected = math.sqrt(((0.28 - 0.3) ** 2 + 0.0**2 + (0.32 - 0.3) ** 2) / 3)
    assert compute_tracking_rmse([0.28, 0.30, 0.32], 0.3) == pytest.approx(expected)


def test_compute_tracking_rmse_empty_input_raises() -> None:
    with pytest.raises(ValueError):
        compute_tracking_rmse([], 0.3)


def test_compute_tracking_rmse_non_numeric_input_raises() -> None:
    with pytest.raises(TypeError):
        compute_tracking_rmse([0.28, "bad", 0.32], 0.3)


def test_summarize_trials_groups_and_summarizes() -> None:
    trial_results = [
        {
            "vx_cmd_mps": 0.3,
            "vx_actual_mps": 0.24,
            "speed_gain": 0.8,
            "absolute_error_mps": -0.06,
            "relative_error": -0.2,
            "lateral_drift_rate_mps": 0.01,
            "yaw_drift_rate_radps": 0.02,
            "tracking_rmse_mps": 0.04,
        },
        {
            "vx_cmd_mps": 0.3,
            "vx_actual_mps": 0.30,
            "speed_gain": 1.0,
            "absolute_error_mps": 0.0,
            "relative_error": 0.0,
            "lateral_drift_rate_mps": 0.02,
            "yaw_drift_rate_radps": 0.03,
            "tracking_rmse_mps": 0.02,
        },
        {
            "vx_cmd_mps": 0.4,
            "vx_actual_mps": 0.32,
            "speed_gain": 0.8,
            "absolute_error_mps": -0.08,
            "relative_error": -0.2,
            "lateral_drift_rate_mps": 0.03,
            "yaw_drift_rate_radps": 0.04,
            "tracking_rmse_mps": 0.05,
        },
    ]

    summary = summarize_trials(trial_results)

    assert set(summary) == {0.3, 0.4}
    assert summary[0.3]["n_trials"] == 2
    assert summary[0.3]["vx_actual_mean_mps"] == pytest.approx(0.27)
    assert summary[0.3]["speed_gain_mean"] == pytest.approx(0.9)
    assert summary[0.3]["absolute_error_mean_mps"] == pytest.approx(-0.03)
    assert summary[0.3]["relative_error_mean"] == pytest.approx(-0.1)
    assert summary[0.3]["lateral_drift_rate_mean_mps"] == pytest.approx(0.015)
    assert summary[0.3]["yaw_drift_rate_mean_radps"] == pytest.approx(0.025)
    assert summary[0.3]["tracking_rmse_mean_mps"] == pytest.approx(0.03)
    assert summary[0.3]["vx_actual_std_mps"] >= 0
    assert summary[0.3]["speed_gain_std"] >= 0

    assert summary[0.4]["n_trials"] == 1
    assert summary[0.4]["vx_actual_std_mps"] == pytest.approx(0.0)
    assert summary[0.4]["speed_gain_std"] == pytest.approx(0.0)


def test_summarize_trials_empty_input_raises() -> None:
    with pytest.raises(ValueError):
        summarize_trials([])


def test_summarize_trials_missing_required_field_raises() -> None:
    with pytest.raises(ValueError, match="missing required field"):
        summarize_trials(
            [
                {
                    "vx_cmd_mps": 0.3,
                    "vx_actual_mps": 0.24,
                }
            ]
        )
