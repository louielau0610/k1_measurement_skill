import pytest

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_HARDWARE_GATE_EXPIRED,
    ERROR_K1_HARDWARE_GATE_INCOMPLETE,
)


def valid_gate(**overrides):
    data = {
        "allow_hardware": True,
        "operator_confirmed_hardware": True,
        "hardware_session_id": "session-1",
        "safety_policy_id": "k1-safe",
        "safety_policy_hash": "hash",
        "expected_robot_id": "k1-test",
        "expected_adapter_mode": K1_VENDOR_RUNTIME_MODE,
        "require_physical_estop_confirmation": True,
        "require_clear_test_area_confirmation": True,
        "require_battery_state_confirmation": True,
        "require_network_isolation_confirmation": True,
        "require_manual_operator_present": True,
        "evidence_reference": "operator-checklist-1",
        "expires_monotonic_ns": 2_000_000_000,
    }
    data.update(overrides)
    return BoosterK1HardwareGate(**data)


def gate_errors(gate, now_ns=1_000_000_000):
    return gate.validate(
        now_ns=now_ns,
        expected_robot_id="k1-test",
        expected_safety_policy_id="k1-safe",
        expected_safety_policy_hash="hash",
    )


def test_valid_explicit_gate():
    assert gate_errors(valid_gate()) == []


def test_missing_evidence_rejected():
    with pytest.raises(ValueError, match="evidence_reference"):
        valid_gate(evidence_reference="")


def test_expired_gate_rejected_with_explicit_now():
    errors = gate_errors(valid_gate(expires_monotonic_ns=999), now_ns=1_000)
    assert errors[0].code == ERROR_K1_HARDWARE_GATE_EXPIRED


def test_allow_hardware_alone_insufficient():
    errors = gate_errors(valid_gate(operator_confirmed_hardware=False))
    assert errors[0].code == ERROR_K1_HARDWARE_GATE_INCOMPLETE
    assert "operator_confirmed_hardware" in errors[0].details["missing_confirmations"]


@pytest.mark.parametrize(
    "field",
    [
        "require_physical_estop_confirmation",
        "require_clear_test_area_confirmation",
        "require_battery_state_confirmation",
        "require_network_isolation_confirmation",
        "require_manual_operator_present",
    ],
)
def test_all_confirmations_required(field):
    errors = gate_errors(valid_gate(**{field: False}))
    assert errors[0].code == ERROR_K1_HARDWARE_GATE_INCOMPLETE
    assert field in errors[0].details["missing_confirmations"]


def test_gate_validation_uses_explicit_now_not_wall_clock():
    assert gate_errors(valid_gate(expires_monotonic_ns=10), now_ns=9) == []
    assert gate_errors(valid_gate(expires_monotonic_ns=10), now_ns=10)[0].code == ERROR_K1_HARDWARE_GATE_EXPIRED


def test_no_default_enabling_values():
    with pytest.raises(TypeError):
        BoosterK1HardwareGate()  # type: ignore[call-arg]
