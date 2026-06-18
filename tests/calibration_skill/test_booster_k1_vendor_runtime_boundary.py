import builtins
import socket
import subprocess
import time

import pytest

from calibration_skill.adapters.booster_k1.config import K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_HARDWARE_GATE_EXPIRED,
    ERROR_K1_HARDWARE_GATE_INCOMPLETE,
    ERROR_K1_HARDWARE_GATE_MISSING,
    ERROR_K1_SDK_UNAVAILABLE,
    ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED,
)
from calibration_skill.adapters.booster_k1.vendor_runtime import (
    BoosterK1RuntimeUnavailable,
    BoosterK1VendorRuntimeStatus,
    create_booster_k1_vendor_runtime,
    detect_booster_sdk_availability,
)
from test_booster_k1_hardware_gate import valid_gate


def importable_status():
    return BoosterK1VendorRuntimeStatus(
        sdk_family="booster_k1",
        sdk_importable_without_importing=True,
        detection_method="test",
        ordinary_runtime_import_safe=True,
        vendor_runtime_implemented=False,
        hardware_gate_required=True,
        hardware_enabled=False,
        reason="test importable",
    )


def test_importing_vendor_runtime_does_not_import_booster_sdk(monkeypatch):
    real_import = builtins.__import__
    seen = []

    def guarded(name, *args, **kwargs):
        seen.append(name)
        if name == "booster_robotics_sdk_python":
            raise AssertionError("SDK import attempted")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    import calibration_skill.adapters.booster_k1.vendor_runtime as vendor_runtime

    assert vendor_runtime.BOOSTER_SDK_MODULE == "booster_robotics_sdk_python"
    assert "booster_robotics_sdk_python" not in seen


def test_detection_uses_find_spec_without_importing(monkeypatch):
    import importlib.util

    calls = []
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: calls.append(name) or None)
    status = detect_booster_sdk_availability()
    assert calls == ["booster_robotics_sdk_python", "B1LocoClient", "ChannelFactory", "RobotMode"]
    assert status.sdk_importable_without_importing is False
    assert status.detection_method == "package_probe_and_direct_module_find_spec"


def test_sdk_unavailable_structured_status():
    status = detect_booster_sdk_availability()
    assert status.sdk_family == "booster_k1"
    assert status.ordinary_runtime_import_safe is True
    assert status.vendor_runtime_implemented is True
    assert status.hardware_gate_required is True
    assert status.hardware_enabled is False


def test_create_without_gate_rejected():
    with pytest.raises(BoosterK1RuntimeUnavailable) as exc:
        create_booster_k1_vendor_runtime(
            hardware_gate=None,
            now_ns=1,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
        )
    assert exc.value.error.code == ERROR_K1_HARDWARE_GATE_MISSING


def test_create_with_incomplete_gate_rejected():
    with pytest.raises(BoosterK1RuntimeUnavailable) as exc:
        create_booster_k1_vendor_runtime(
            hardware_gate=valid_gate(operator_confirmed_hardware=False),
            now_ns=1,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
        )
    assert exc.value.error.code == ERROR_K1_HARDWARE_GATE_INCOMPLETE


def test_create_with_expired_gate_rejected():
    with pytest.raises(BoosterK1RuntimeUnavailable) as exc:
        create_booster_k1_vendor_runtime(
            hardware_gate=valid_gate(expires_monotonic_ns=10),
            now_ns=10,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
        )
    assert exc.value.error.code == ERROR_K1_HARDWARE_GATE_EXPIRED


def test_missing_sdk_gives_structured_unavailable_error():
    unavailable = BoosterK1VendorRuntimeStatus(
        sdk_family="booster_k1",
        sdk_importable_without_importing=False,
        detection_method="test",
        ordinary_runtime_import_safe=True,
        vendor_runtime_implemented=False,
        hardware_gate_required=True,
        hardware_enabled=False,
        reason="missing",
    )
    with pytest.raises(BoosterK1RuntimeUnavailable) as exc:
        create_booster_k1_vendor_runtime(
            hardware_gate=valid_gate(),
            now_ns=1,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
            status=unavailable,
            enable_vendor_runtime=True,
            execute_hardware=True,
        )
    assert exc.value.error.code == ERROR_K1_SDK_UNAVAILABLE
    assert exc.value.to_dict()["status"]["hardware_enabled"] is False


def test_valid_looking_gate_still_rejected_as_not_implemented():
    with pytest.raises(BoosterK1RuntimeUnavailable) as exc:
        create_booster_k1_vendor_runtime(
            hardware_gate=valid_gate(),
            now_ns=1,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
            status=importable_status(),
        )
    assert exc.value.error.code == ERROR_K1_VENDOR_RUNTIME_NOT_IMPLEMENTED


def test_no_forbidden_side_effects(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(subprocess, "Popen", fail)
    monkeypatch.setattr(time, "sleep", fail)
    with pytest.raises(BoosterK1RuntimeUnavailable):
        create_booster_k1_vendor_runtime(
            hardware_gate=valid_gate(expected_adapter_mode=K1_VENDOR_RUNTIME_MODE),
            now_ns=1,
            expected_robot_id="k1-test",
            expected_safety_policy_id="k1-safe",
            expected_safety_policy_hash="hash",
            status=importable_status(),
        )
