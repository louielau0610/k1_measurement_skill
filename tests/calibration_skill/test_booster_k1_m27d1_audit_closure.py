"""M27-D.1 audit-closure regression tests.

All tests are offline and use fake modules, fake bindings, or monkeypatches.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    BoosterK1DomainError,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
    ERROR_K1_SDK_IMPORT_FAILED,
)
from calibration_skill.adapters.booster_k1.runtime import BoosterK1RuntimeCommandReceipt
from calibration_skill.adapters.booster_k1.vendor_binding import (
    PACKAGE_PROBE_MODULE,
    VERIFIED_DIRECT_ENTRY_MODULES,
    _import_verified_sdk,
    create_vendor_binding,
    detect_booster_sdk_availability_detailed,
)
from calibration_skill.adapters.booster_k1.vendor_runtime import (
    BoosterK1VendorRuntime,
    create_booster_k1_vendor_runtime,
    detect_booster_sdk_availability,
)
from calibration_skill.domain.enums import MotionLifecycleState, RobotPlatform
from tests.calibration_skill.fakes.fake_booster_k1_vendor_binding import FakeBoosterK1VendorBinding


def _valid_gate(**overrides) -> BoosterK1HardwareGate:
    data = {
        "allow_hardware": True,
        "operator_confirmed_hardware": True,
        "hardware_session_id": "m27d1-test",
        "safety_policy_id": "policy",
        "safety_policy_hash": "hash",
        "expected_robot_id": "k1-test",
        "expected_adapter_mode": K1_VENDOR_RUNTIME_MODE,
        "require_physical_estop_confirmation": True,
        "require_clear_test_area_confirmation": True,
        "require_battery_state_confirmation": True,
        "require_network_isolation_confirmation": True,
        "require_manual_operator_present": True,
        "evidence_reference": "m27d1-test",
        "expires_monotonic_ns": 999999999999999999,
    }
    data.update(overrides)
    return BoosterK1HardwareGate(**data)


def _patch_specs(monkeypatch, present: set[str]) -> None:
    import calibration_skill.adapters.booster_k1.vendor_binding as vendor_binding

    def fake_find_spec(name: str):
        return object() if name in present else None

    monkeypatch.setattr(vendor_binding.importlib.util, "find_spec", fake_find_spec)


def _install_fake_direct_modules(monkeypatch, *, missing_class: str | None = None) -> None:
    for module_name, class_name in zip(VERIFIED_DIRECT_ENTRY_MODULES, VERIFIED_DIRECT_ENTRY_MODULES):
        module = types.ModuleType(module_name)
        if class_name != missing_class:
            setattr(module, class_name, type(class_name, (), {}))
        monkeypatch.setitem(sys.modules, module_name, module)


def test_historical_direct_import_module_names_are_exact():
    assert VERIFIED_DIRECT_ENTRY_MODULES == ("B1LocoClient", "ChannelFactory", "RobotMode")
    source = Path("scripts/send_m23b_k1_velocity_command.py").read_text(encoding="utf-8")
    assert "from B1LocoClient import B1LocoClient" in source
    assert "from ChannelFactory import ChannelFactory" in source
    assert "from RobotMode import RobotMode" in source
    assert 'find_spec("booster_robotics_sdk_python")' in source


def test_package_probe_success_does_not_verify_direct_imports(monkeypatch):
    _patch_specs(monkeypatch, {PACKAGE_PROBE_MODULE})
    detection = detect_booster_sdk_availability_detailed()
    assert detection.package_probe_discoverable is True
    assert detection.direct_entry_modules_discoverable is False
    assert detection.direct_imports_verified is False


def test_package_probe_failure_does_not_override_direct_discovery(monkeypatch):
    _patch_specs(monkeypatch, set(VERIFIED_DIRECT_ENTRY_MODULES))
    detection = detect_booster_sdk_availability_detailed()
    assert detection.package_probe_discoverable is False
    assert detection.direct_entry_modules_discoverable is True
    assert detect_booster_sdk_availability().sdk_importable_without_importing is True


def test_one_missing_direct_module_fails_closed_detection(monkeypatch):
    _patch_specs(monkeypatch, {PACKAGE_PROBE_MODULE, "B1LocoClient", "ChannelFactory"})
    detection = detect_booster_sdk_availability_detailed()
    assert detection.direct_entry_module_specs["RobotMode"] is False
    assert detection.direct_entry_modules_discoverable is False


def test_direct_imports_not_attempted_before_every_gate_passes(monkeypatch):
    import calibration_skill.adapters.booster_k1.vendor_binding as vendor_binding

    calls: list[str] = []
    monkeypatch.setattr(vendor_binding.importlib, "import_module", lambda name: calls.append(name))
    with pytest.raises(BoosterK1DomainError):
        create_vendor_binding(
            hardware_gate=_valid_gate(),
            now_ns=0,
            expected_robot_id="k1-test",
            expected_safety_policy_id="policy",
            expected_safety_policy_hash="hash",
            enable_vendor_runtime=True,
            execute_hardware=False,
        )
    assert calls == []


def test_direct_import_succeeds_through_injected_modules(monkeypatch):
    _install_fake_direct_modules(monkeypatch)
    B1LocoClient, ChannelFactory, RobotMode = _import_verified_sdk()
    assert B1LocoClient.__name__ == "B1LocoClient"
    assert ChannelFactory.__name__ == "ChannelFactory"
    assert RobotMode.__name__ == "RobotMode"


@pytest.mark.parametrize("missing", ["B1LocoClient", "ChannelFactory", "RobotMode"])
def test_missing_direct_class_fails_closed(monkeypatch, missing):
    _install_fake_direct_modules(monkeypatch, missing_class=missing)
    with pytest.raises(ImportError) as exc:
        _import_verified_sdk()
    assert missing in str(exc.value)


def test_missing_hardware_gate_has_gate_error_code():
    with pytest.raises(BoosterK1DomainError) as exc:
        create_vendor_binding(
            hardware_gate=None,
            now_ns=0,
            expected_robot_id="k1-test",
            expected_safety_policy_id="policy",
            expected_safety_policy_hash="hash",
            enable_vendor_runtime=True,
            execute_hardware=True,
        )
    assert exc.value.code == ERROR_K1_HARDWARE_GATE_MISSING


def test_zero_velocity_never_transitions_to_moving():
    binding = FakeBoosterK1VendorBinding()
    runtime = BoosterK1VendorRuntime(binding=binding)
    runtime.connect(timeout_s=1.0)
    runtime.enter_walking_mode()
    receipt = runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
    assert receipt.accepted
    assert receipt.zero_command_accepted is True
    assert runtime.current_motion_state() == MotionLifecycleState.LOCOMOTION_READY


@pytest.mark.parametrize("kwargs", [
    {"vx_mps": 0.1, "vy_mps": 0.0, "wz_radps": 0.0},
    {"vx_mps": 0.0, "vy_mps": 0.1, "wz_radps": 0.0},
    {"vx_mps": 0.0, "vy_mps": 0.0, "wz_radps": 0.1},
])
def test_nonzero_axes_remain_independently_forbidden(kwargs):
    runtime = BoosterK1VendorRuntime(binding=FakeBoosterK1VendorBinding())
    runtime.connect(timeout_s=1.0)
    runtime.enter_walking_mode()
    with pytest.raises(BoosterK1DomainError) as exc:
        runtime.send_body_velocity(**kwargs)
    assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN


def test_stop_receipt_separates_acceptance_from_physical_observation():
    runtime = BoosterK1VendorRuntime(binding=FakeBoosterK1VendorBinding())
    runtime.connect(timeout_s=1.0)
    receipt = runtime.stop()
    assert receipt.accepted
    assert receipt.stop_command_accepted
    assert receipt.physical_stop_verified is False
    assert runtime.current_motion_state() == MotionLifecycleState.SAFE_STOPPED


class _NoOdometryRuntime:
    def __init__(self):
        self.connected = False

    def connect(self, *, timeout_s: float) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def restore_safe_state(self) -> None:
        pass

    def identity_metadata(self) -> dict[str, object]:
        return {"sdk_family": "fake"}

    def current_motion_state(self) -> MotionLifecycleState:
        return MotionLifecycleState.SAFE_STOPPED

    def read_robot_state(self):
        return SimpleNamespace(motion_state=MotionLifecycleState.SAFE_STOPPED, mode_name="internal", source_monotonic_ns=1)

    def read_odometry(self):
        return None

    def read_battery_state(self):
        return None

    def health_check(self):
        return SimpleNamespace(
            healthy=True,
            detail="binding readiness only",
            scope="binding_readiness",
            communication_verified=False,
        )

    def stop(self):
        return BoosterK1RuntimeCommandReceipt(
            accepted=True,
            runtime_receipt_id="stop",
            received_monotonic_ns=1,
            stop_command_accepted=True,
            internal_command_state="safe_stopped",
        )


def _bench_args(tmp_path):
    return SimpleNamespace(
        robot_id="k1-test",
        hardware_session_id="m27d1",
        safety_policy_id="policy",
        safety_policy_hash="hash",
        evidence_reference="m27d1",
        gate_expiry_monotonic_ns=999999999999999999,
        output_dir=str(tmp_path),
        operator_confirmed_hardware=True,
        physical_estop_confirmed=True,
        clear_test_area_confirmed=True,
        battery_state_confirmed=True,
        network_isolation_confirmed=True,
        manual_operator_present=True,
        enable_vendor_runtime=True,
        execute_hardware=True,
        interface="lo",
    )


def test_internal_safe_stopped_cannot_satisfy_physical_safe_state(monkeypatch, tmp_path):
    import calibration_skill.adapters.booster_k1.vendor_runtime as vendor_runtime
    import scripts.run_m27d_k1_zero_motion_bench as bench

    monkeypatch.setattr(vendor_runtime, "detect_booster_sdk_availability", lambda: SimpleNamespace(sdk_importable_without_importing=True))
    monkeypatch.setattr(vendor_runtime, "create_booster_k1_vendor_runtime", lambda **_: _NoOdometryRuntime())
    result = bench.run_bench(_bench_args(tmp_path))
    assert result.stop_command_accepted is True
    assert result.internal_safe_state_claim is True
    assert result.physical_safe_state_observed is False
    assert result.physical_safe_state_verification == "unavailable"
    assert result.status == bench.STATUS_SAFE_STATE_UNVERIFIED


def test_health_result_is_binding_readiness_not_transport_health():
    binding = FakeBoosterK1VendorBinding()
    binding.connect(timeout_s=1.0)
    health = binding.health_check()
    assert health.scope == "binding_readiness"
    assert health.communication_verified is False


def test_unverified_get_mode_is_optional_and_not_physical_evidence():
    binding = FakeBoosterK1VendorBinding()
    runtime = BoosterK1VendorRuntime(binding=binding)
    runtime.connect(timeout_s=1.0)
    state = runtime.read_robot_state()
    assert state.metadata == {} or state.metadata.get("physical_safe_state_evidence") is not True


def test_default_imports_do_not_import_direct_sdk_modules():
    import calibration_skill.adapters.booster_k1.vendor_runtime  # noqa: F401
    import calibration_skill.adapters.booster_k1.registry  # noqa: F401

    for module_name in VERIFIED_DIRECT_ENTRY_MODULES:
        assert module_name not in sys.modules


def test_default_registry_remains_mock_only():
    from calibration_skill.adapters.registry import AdapterRegistry

    assert RobotPlatform.BOOSTER_K1 not in AdapterRegistry()._records


def test_fake_k1_path_remains_supported():
    binding = FakeBoosterK1VendorBinding()
    runtime = BoosterK1VendorRuntime(binding=binding)
    runtime.connect(timeout_s=1.0)
    runtime.enter_prepare_mode()
    runtime.enter_walking_mode()
    assert runtime.stop().accepted


def test_artifacts_are_deterministic_and_readiness_matrix_corrected():
    readiness = json.loads(Path("outputs/engineering/m27d_readiness_summary.json").read_text(encoding="utf-8"))
    assert readiness["readiness"]["k1_vendor_runtime"] == "zero_motion_unit_test_verified"
    assert readiness["readiness"]["k1_zero_motion_bench"] == "not_executed"
    assert readiness["readiness"]["k1_physical_safe_state"] == "not_verified"


def test_sanitized_exception_serialization():
    from calibration_skill.adapters.booster_k1.errors import sanitize_vendor_message
    from scripts.run_m27d_k1_zero_motion_bench import _error_to_dict

    class Bad:
        def __str__(self):
            return "token=abc123 object=<SDK at 0xDEADBEEF>\nTraceback (most recent call last): secret=abc"

    message = sanitize_vendor_message(Bad())
    assert "abc123" not in message
    assert "0xDEADBEEF" not in message
    assert "\n" not in message
    error_dict = _error_to_dict(RuntimeError(str(Bad())))
    assert "abc123" not in str(error_dict)
