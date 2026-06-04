"""Pure metric helpers for K1 forward velocity measurement."""

from __future__ import annotations

import math
from collections import defaultdict
from numbers import Real
from statistics import mean, stdev
from typing import Iterable, Mapping, Sequence


REQUIRED_TRIAL_FIELDS = (
    "vx_cmd_mps",
    "vx_actual_mps",
    "speed_gain",
    "absolute_error_mps",
    "relative_error",
    "lateral_drift_rate_mps",
    "yaw_drift_rate_radps",
    "tracking_rmse_mps",
)


def _validate_time_interval(t_start: float, t_end: float) -> float:
    duration = float(t_end) - float(t_start)
    if duration <= 0:
        raise ValueError("t_end must be greater than t_start")
    return duration


def _ensure_numeric(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{field_name} must be numeric")
    return float(value)


def _mean(values: Sequence[float]) -> float:
    return float(mean(values))


def _sample_std(values: Sequence[float]) -> float:
    if len(values) == 1:
        return 0.0
    return float(stdev(values))


def compute_actual_velocity(
    x_start: float, x_end: float, t_start: float, t_end: float
) -> float:
    """Compute actual forward velocity from position delta over time."""

    duration = _validate_time_interval(t_start, t_end)
    return (float(x_end) - float(x_start)) / duration


def compute_speed_gain(v_actual: float, v_cmd: float) -> float:
    """Compute speed gain as actual velocity divided by commanded velocity."""

    if float(v_cmd) == 0.0:
        raise ValueError("v_cmd must not be zero when computing speed gain")
    return float(v_actual) / float(v_cmd)


def compute_absolute_error(v_actual: float, v_cmd: float) -> float:
    """Compute absolute signed velocity error as actual minus commanded."""

    return float(v_actual) - float(v_cmd)


def compute_relative_error(v_actual: float, v_cmd: float) -> float:
    """Compute relative signed velocity error normalized by commanded velocity."""

    if float(v_cmd) == 0.0:
        raise ValueError("v_cmd must not be zero when computing relative error")
    return compute_absolute_error(v_actual, v_cmd) / float(v_cmd)


def compute_lateral_drift_rate(
    y_start: float, y_end: float, t_start: float, t_end: float
) -> float:
    """Compute absolute lateral drift rate in meters per second."""

    duration = _validate_time_interval(t_start, t_end)
    return abs(float(y_end) - float(y_start)) / duration


def compute_yaw_drift_rate(
    yaw_start: float, yaw_end: float, t_start: float, t_end: float
) -> float:
    """Compute absolute yaw drift rate in radians per second."""

    duration = _validate_time_interval(t_start, t_end)
    return abs(float(yaw_end) - float(yaw_start)) / duration


def compute_tracking_rmse(v_actual_series: Iterable[float], v_cmd: float) -> float:
    """Compute RMSE between actual velocity samples and one command velocity."""

    values = list(v_actual_series)
    if not values:
        raise ValueError("v_actual_series must not be empty")

    numeric_values = [
        _ensure_numeric(value, f"v_actual_series[{index}]")
        for index, value in enumerate(values)
    ]
    command = _ensure_numeric(v_cmd, "v_cmd")
    squared_errors = [(value - command) ** 2 for value in numeric_values]
    return math.sqrt(float(mean(squared_errors)))


def summarize_trials(trial_results: list[Mapping[str, object]]) -> dict[float, dict[str, float | int]]:
    """Summarize repeated measurement trials grouped by commanded forward speed."""

    if not trial_results:
        raise ValueError("trial_results must not be empty")

    grouped: dict[float, list[dict[str, float]]] = defaultdict(list)
    for index, trial in enumerate(trial_results):
        missing = [field for field in REQUIRED_TRIAL_FIELDS if field not in trial]
        if missing:
            raise ValueError(f"trial_results[{index}] is missing required field: {missing[0]}")

        numeric_trial = {
            field: _ensure_numeric(trial[field], f"trial_results[{index}].{field}")
            for field in REQUIRED_TRIAL_FIELDS
        }
        grouped[numeric_trial["vx_cmd_mps"]].append(numeric_trial)

    summary: dict[float, dict[str, float | int]] = {}
    for vx_cmd, trials in sorted(grouped.items()):
        vx_actual_values = [trial["vx_actual_mps"] for trial in trials]
        speed_gain_values = [trial["speed_gain"] for trial in trials]
        absolute_error_values = [trial["absolute_error_mps"] for trial in trials]
        relative_error_values = [trial["relative_error"] for trial in trials]
        lateral_drift_values = [trial["lateral_drift_rate_mps"] for trial in trials]
        yaw_drift_values = [trial["yaw_drift_rate_radps"] for trial in trials]
        tracking_rmse_values = [trial["tracking_rmse_mps"] for trial in trials]

        summary[vx_cmd] = {
            "n_trials": len(trials),
            "vx_actual_mean_mps": _mean(vx_actual_values),
            "vx_actual_std_mps": _sample_std(vx_actual_values),
            "speed_gain_mean": _mean(speed_gain_values),
            "speed_gain_std": _sample_std(speed_gain_values),
            "absolute_error_mean_mps": _mean(absolute_error_values),
            "relative_error_mean": _mean(relative_error_values),
            "lateral_drift_rate_mean_mps": _mean(lateral_drift_values),
            "yaw_drift_rate_mean_radps": _mean(yaw_drift_values),
            "tracking_rmse_mean_mps": _mean(tracking_rmse_values),
        }

    return summary


# Compatibility helpers kept for existing scripts until M3 rewires the pipeline.
def velocity_error(vx_cmd: float, vx_actual: float) -> float:
    """Return actual minus commanded forward velocity."""

    return compute_absolute_error(vx_actual=vx_actual, v_cmd=vx_cmd)


def mean_velocity(values: list[float]) -> float:
    """Return the mean of sampled velocities."""

    if not values:
        raise ValueError("values must not be empty")
    return _mean([_ensure_numeric(value, "values item") for value in values])


def population_std(values: list[float]) -> float:
    """Return population standard deviation for sampled velocities."""

    if not values:
        raise ValueError("values must not be empty")
    numeric_values = [_ensure_numeric(value, "values item") for value in values]
    if len(numeric_values) == 1:
        return 0.0
    population_mean = _mean(numeric_values)
    return math.sqrt(mean((value - population_mean) ** 2 for value in numeric_values))


def summarize_velocity_samples(vx_cmd: float, samples: list[float]) -> dict[str, float | int]:
    """Summarize repeated actual velocity samples for one command speed."""

    actual_mean = mean_velocity(samples)
    return {
        "vx_cmd": float(vx_cmd),
        "vx_actual_mean": actual_mean,
        "vx_error_mean": velocity_error(vx_cmd, actual_mean),
        "vx_actual_std": population_std(samples),
        "sample_size": len(samples),
    }
