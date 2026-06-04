"""Metric helpers for K1 forward velocity measurement."""

from __future__ import annotations

from statistics import mean, pstdev


def velocity_error(vx_cmd: float, vx_actual: float) -> float:
    """Return actual minus commanded forward velocity."""

    return vx_actual - vx_cmd


def mean_velocity(values: list[float]) -> float:
    """Return the mean of sampled velocities."""

    if not values:
        raise ValueError("values must not be empty")
    return mean(values)


def population_std(values: list[float]) -> float:
    """Return population standard deviation for sampled velocities."""

    if not values:
        raise ValueError("values must not be empty")
    return pstdev(values)


def summarize_velocity_samples(vx_cmd: float, samples: list[float]) -> dict[str, float | int]:
    """Summarize repeated actual velocity samples for one command speed."""

    actual_mean = mean_velocity(samples)
    return {
        "vx_cmd": vx_cmd,
        "vx_actual_mean": actual_mean,
        "vx_error_mean": velocity_error(vx_cmd, actual_mean),
        "vx_actual_std": population_std(samples),
        "sample_size": len(samples),
    }
