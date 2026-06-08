from __future__ import annotations

from pathlib import Path

from k1_measurement.visualization import generate_measurement_plots


def test_visualization_generation_with_minimal_data(tmp_path: Path) -> None:
    velocity_profile = [
        {"vx_cmd_mps": 0.1, "vx_actual_mean_mps": 0.09, "speed_gain_mean": 0.9},
        {"vx_cmd_mps": 0.2, "vx_actual_mean_mps": 0.18, "speed_gain_mean": 0.9},
    ]
    trial = [
        {"timestamp": 0.0, "vx_cmd": 0.1, "odom_vx": 0.0, "odom_y": 0.0},
        {"timestamp": 1.0, "vx_cmd": 0.1, "odom_vx": 0.09, "odom_y": 0.01},
    ]

    outputs = generate_measurement_plots(velocity_profile, trial, tmp_path)

    assert outputs["velocity_error_plot"] is not None
    assert outputs["speed_gain_plot"] is not None
    assert outputs["trial_timeseries_plot"] is not None
    assert outputs["drift_plot"] is not None
    for output in outputs.values():
        assert output is not None
        assert Path(output).exists()


def test_visualization_graceful_degradation_when_columns_missing(tmp_path: Path) -> None:
    outputs = generate_measurement_plots(
        velocity_profile=[{"vx_cmd_mps": 0.1}],
        trial_timeseries=[{"timestamp": 0.0}],
        output_dir=tmp_path,
    )

    assert outputs["velocity_error_plot"] is None
    assert outputs["speed_gain_plot"] is None
    assert outputs["trial_timeseries_plot"] is None
    assert outputs["drift_plot"] is None
