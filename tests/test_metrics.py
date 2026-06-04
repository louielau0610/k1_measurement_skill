from k1_measurement.metrics import mean_velocity, summarize_velocity_samples, velocity_error


def test_velocity_error_is_actual_minus_commanded() -> None:
    assert velocity_error(0.2, 0.18) == -0.020000000000000018


def test_mean_velocity() -> None:
    assert mean_velocity([0.1, 0.2, 0.3]) == 0.2


def test_summarize_velocity_samples() -> None:
    summary = summarize_velocity_samples(0.2, [0.18, 0.20, 0.22])
    assert summary["vx_cmd"] == 0.2
    assert summary["vx_actual_mean"] == 0.2
    assert summary["sample_size"] == 3
