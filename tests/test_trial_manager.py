from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
import yaml

from k1_measurement.trial_manager import K1TrialManager


def test_trial_manager_loads_config() -> None:
    manager = K1TrialManager()

    config = manager.load_config()

    assert config["experiment"]["name"] == "k1_forward_velocity_tracking_baseline_v0"


def test_generate_trial_plan_creates_expected_trials() -> None:
    manager = K1TrialManager()

    trial_plan = manager.generate_trial_plan()

    assert len(trial_plan) == 20
    assert len({trial["trial_id"] for trial in trial_plan}) == 20
    assert sorted({trial["vx_cmd_mps"] for trial in trial_plan}) == [0.1, 0.2, 0.3, 0.4]
    assert Counter(trial["vx_cmd_mps"] for trial in trial_plan) == {
        0.1: 5,
        0.2: 5,
        0.3: 5,
        0.4: 5,
    }


def test_validate_trial_plan_accepts_valid_config() -> None:
    manager = K1TrialManager()

    assert manager.validate_trial_plan(manager.generate_trial_plan()) is True


def test_validate_trial_plan_rejects_vx_above_limit() -> None:
    manager = K1TrialManager()
    trial_plan = manager.generate_trial_plan()
    trial_plan[0]["vx_cmd_mps"] = 0.5

    with pytest.raises(ValueError, match="exceeds"):
        manager.validate_trial_plan(trial_plan)


def test_validate_trial_plan_rejects_nonzero_vy_when_disabled() -> None:
    manager = K1TrialManager()
    trial_plan = manager.generate_trial_plan()
    trial_plan[0]["vy_cmd_mps"] = 0.1

    with pytest.raises(ValueError, match="vy_cmd_mps"):
        manager.validate_trial_plan(trial_plan)


def test_validate_trial_plan_rejects_nonzero_wz_when_disabled() -> None:
    manager = K1TrialManager()
    trial_plan = manager.generate_trial_plan()
    trial_plan[0]["wz_cmd_radps"] = 0.1

    with pytest.raises(ValueError, match="wz_cmd_radps"):
        manager.validate_trial_plan(trial_plan)


def test_validate_trial_plan_rejects_stable_window_outside_command_duration() -> None:
    manager = K1TrialManager()
    trial_plan = manager.generate_trial_plan()
    trial_plan[0]["stable_window_end_sec"] = 7.0

    with pytest.raises(ValueError, match="stable window"):
        manager.validate_trial_plan(trial_plan)


def test_trial_manager_uses_custom_config(tmp_path: Path) -> None:
    config = yaml.safe_load(Path("config/experiment_forward_v0.yaml").read_text(encoding="utf-8"))
    config["trial_plan"]["vx_cmd_values_mps"] = [0.1]
    config["trial_plan"]["repeats_per_speed"] = 2
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    manager = K1TrialManager(str(config_path))

    trial_plan = manager.generate_trial_plan()

    assert len(trial_plan) == 2
    assert manager.validate_trial_plan(trial_plan) is True
