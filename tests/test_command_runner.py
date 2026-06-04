from __future__ import annotations

import pytest

from k1_measurement.command_runner import CommandSafetyError, K1CommandRunner
from k1_measurement.trial_manager import K1TrialManager


def test_command_runner_defaults_to_dry_run() -> None:
    runner = K1CommandRunner()

    assert runner.dry_run is True


def test_safety_check_allows_safe_dry_run_inputs() -> None:
    runner = K1CommandRunner()

    assert runner.safety_check(0.3, 0.0, 0.0) is True


def test_safety_check_rejects_vx_above_limit() -> None:
    runner = K1CommandRunner()

    with pytest.raises(CommandSafetyError):
        runner.safety_check(0.5, 0.0, 0.0)


def test_safety_check_rejects_nonzero_vy_when_disabled() -> None:
    runner = K1CommandRunner()

    with pytest.raises(CommandSafetyError):
        runner.safety_check(0.2, 0.1, 0.0)


def test_safety_check_rejects_nonzero_wz_when_disabled() -> None:
    runner = K1CommandRunner()

    with pytest.raises(CommandSafetyError):
        runner.safety_check(0.2, 0.0, 0.1)


def test_send_velocity_command_dry_run_does_not_raise() -> None:
    runner = K1CommandRunner()

    runner.send_velocity_command(0.2, 0.0, 0.0)


def test_send_stop_command_dry_run_does_not_raise() -> None:
    runner = K1CommandRunner()

    runner.send_stop_command()


def test_run_single_trial_dry_run_does_not_raise() -> None:
    trial = K1TrialManager().generate_trial_plan()[0]
    runner = K1CommandRunner()

    runner.run_single_trial(trial)


def test_send_velocity_command_real_mode_raises_not_implemented() -> None:
    runner = K1CommandRunner(dry_run=False)

    with pytest.raises(NotImplementedError):
        runner.send_velocity_command(
            0.2,
            0.0,
            0.0,
            manual_confirmation=True,
            emergency_stop_ready=True,
        )


def test_run_single_trial_real_mode_raises_not_implemented() -> None:
    trial = K1TrialManager().generate_trial_plan()[0]
    runner = K1CommandRunner(dry_run=False)

    with pytest.raises(NotImplementedError):
        runner.run_single_trial(
            trial,
            manual_confirmation=True,
            emergency_stop_ready=True,
        )
