import math

import pytest

from calibration_skill.adapters.booster_k1.config import BoosterK1AdapterConfig, K1_FAKE_RUNTIME_MODE


def valid_config(**overrides):
    data = {
        "robot_id": "k1-test",
        "connection_profile_id": "fake-profile",
        "runtime_mode": K1_FAKE_RUNTIME_MODE,
        "dry_run": True,
        "allow_hardware": False,
        "safety_policy_id": "k1-safe",
        "safety_policy_hash": "hash",
        "max_abs_vx_mps": 0.6,
        "max_abs_vy_mps": 0.0,
        "max_abs_wz_radps": 0.0,
        "command_timeout_s": 0.5,
        "telemetry_timeout_s": 1.0,
        "stop_timeout_s": 0.5,
        "operator_authorization_required": True,
        "metadata": {"milestone": "m27b"},
    }
    data.update(overrides)
    return BoosterK1AdapterConfig(**data)


def test_valid_explicit_config_builds_safety_envelope():
    config = valid_config()
    envelope = config.to_safety_envelope()
    assert config.robot_id == "k1-test"
    assert envelope.max_abs_vx_mps == 0.6
    assert envelope.max_abs_vy_mps == 0.0
    assert envelope.operator_authorization_required is True


@pytest.mark.parametrize("field", ["robot_id", "safety_policy_id", "safety_policy_hash"])
def test_required_identifiers_are_non_empty(field):
    with pytest.raises(ValueError, match=field):
        valid_config(**{field: ""})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_limits_rejected(value):
    with pytest.raises(ValueError, match="max_abs_vx_mps"):
        valid_config(max_abs_vx_mps=value)


def test_negative_timeout_rejected():
    with pytest.raises(ValueError, match="telemetry_timeout_s"):
        valid_config(telemetry_timeout_s=-1.0)


def test_allow_hardware_true_rejected_in_m27b():
    with pytest.raises(ValueError, match="allow_hardware=true"):
        valid_config(allow_hardware=True)


@pytest.mark.parametrize("field", ["max_abs_vx_mps", "max_abs_vy_mps", "max_abs_wz_radps"])
def test_no_silent_speed_defaults(field):
    with pytest.raises(ValueError, match=field):
        valid_config(**{field: None})


def test_forward_only_requires_explicit_zero_lateral_and_yaw_limits():
    with pytest.raises(ValueError, match="legacy_forward_only"):
        valid_config(max_abs_vy_mps=0.1)
