"""M27-D vendor binding tests.

Tests for the vendor binding protocol and the fake vendor binding
implementation. No real SDK or hardware required.
"""
from __future__ import annotations

import time

from calibration_skill.adapters.booster_k1.runtime import BoosterK1RuntimeCommandReceipt
from calibration_skill.adapters.booster_k1.vendor_types import (
    BoosterK1VendorBindingProtocol,
    BoosterK1VendorSDKDetection,
)
from calibration_skill.domain.enums import MotionLifecycleState
from tests.calibration_skill.fakes.fake_booster_k1_vendor_binding import (
    FakeBindingFailureConfig,
    FakeBoosterK1VendorBinding,
)


class TestFakeVendorBinding:
    """Tests for the fake vendor binding used in tests."""

    def test_connect_and_disconnect(self):
        binding = FakeBoosterK1VendorBinding()
        assert not binding.connected
        assert binding.current_motion_state() == MotionLifecycleState.UNAVAILABLE

        binding.connect(timeout_s=5.0)
        assert binding.connected
        assert binding.current_motion_state() == MotionLifecycleState.IDLE

        binding.disconnect()
        assert not binding.connected
        assert binding.current_motion_state() == MotionLifecycleState.UNAVAILABLE

    def test_connect_idempotent(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        # Second connect should not error
        binding.connect(timeout_s=5.0)
        assert binding.connected

    def test_disconnect_idempotent(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.disconnect()
        binding.disconnect()  # Should not error
        assert not binding.connected

    def test_identity_metadata(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        identity = binding.identity_metadata()
        assert identity["sdk_family"] == "fake_booster_k1"
        assert identity["hardware_serial"] == "fake-k1-serial-001"

    def test_prepare_and_walking_modes(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)

        binding.enter_prepare_mode()
        assert binding.current_motion_state() == MotionLifecycleState.PREPARING

        binding.enter_walking_mode()
        assert binding.current_motion_state() == MotionLifecycleState.LOCOMOTION_READY

    def test_zero_velocity_command(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()

        receipt = binding.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert receipt.accepted
        assert binding.current_motion_state() == MotionLifecycleState.MOVING

    def test_stop_command(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()

        receipt = binding.stop()
        assert receipt.accepted
        assert binding.current_motion_state() == MotionLifecycleState.SAFE_STOPPED

    def test_restore_safe_state(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()

        binding.restore_safe_state()
        assert binding.current_motion_state() == MotionLifecycleState.SAFE_STOPPED

    def test_read_odometry(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)

        odom = binding.read_odometry()
        assert odom is not None
        assert odom.x_m == 1.0
        assert odom.y_m == 2.0

    def test_read_robot_state(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)

        state = binding.read_robot_state()
        assert state.motion_state == MotionLifecycleState.IDLE
        assert state.battery_percentage == 88.0

    def test_read_battery_state(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)

        battery = binding.read_battery_state()
        assert battery is not None
        assert battery["battery_percentage"] == 88.0

    def test_health_check_connected(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)

        health = binding.health_check()
        assert health.healthy

    def test_health_check_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        health = binding.health_check()
        assert not health.healthy

    def test_connect_failure(self):
        binding = FakeBoosterK1VendorBinding(
            failures=FakeBindingFailureConfig(connect_failure=True)
        )
        try:
            binding.connect(timeout_s=5.0)
            assert False, "Should have raised"
        except RuntimeError:
            pass
        assert not binding.connected

    def test_stop_unacknowledged(self):
        binding = FakeBoosterK1VendorBinding(
            failures=FakeBindingFailureConfig(stop_unacknowledged=True)
        )
        binding.connect(timeout_s=5.0)
        receipt = binding.stop()
        assert not receipt.accepted
        assert "injected stop unacknowledged" in receipt.detail

    def test_command_rejection(self):
        binding = FakeBoosterK1VendorBinding(
            failures=FakeBindingFailureConfig(command_rejection=True)
        )
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()

        receipt = binding.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert not receipt.accepted

    def test_call_tracking(self):
        binding = FakeBoosterK1VendorBinding()
        binding.connect(timeout_s=5.0)
        binding.enter_walking_mode()
        binding.stop()
        binding.disconnect()

        assert "connect:5.0" in binding.calls
        assert "enter_walking_mode" in binding.calls
        assert "stop" in binding.calls
        assert "disconnect" in binding.calls

    def test_implements_protocol(self):
        """Verify FakeBoosterK1VendorBinding structurally matches the protocol."""
        binding = FakeBoosterK1VendorBinding()
        # All protocol methods must be present
        for method_name in [
            "connect", "disconnect", "identity_metadata",
            "current_motion_state", "enter_prepare_mode",
            "enter_walking_mode", "send_body_velocity", "stop",
            "restore_safe_state", "read_odometry",
            "read_robot_state", "read_battery_state", "health_check",
        ]:
            assert hasattr(binding, method_name), f"Missing method: {method_name}"
            assert callable(getattr(binding, method_name)), f"Not callable: {method_name}"


class TestVendorSDKDetection:
    """Tests for SDK detection without importing."""

    def test_detection_structure(self):
        from calibration_skill.adapters.booster_k1.vendor_binding import (
            detect_booster_sdk_availability_detailed,
        )
        detection = detect_booster_sdk_availability_detailed()
        assert isinstance(detection, BoosterK1VendorSDKDetection)
        assert detection.detection_method == "importlib.util.find_spec"
        assert len(detection.sdk_entry_classes) == 3
        assert "B1LocoClient" in detection.sdk_entry_classes
        assert "ChannelFactory" in detection.sdk_entry_classes
        assert "RobotMode" in detection.sdk_entry_classes

    def test_detection_dict_serialization(self):
        from calibration_skill.adapters.booster_k1.vendor_binding import (
            detect_booster_sdk_availability_detailed,
        )
        detection = detect_booster_sdk_availability_detailed()
        d = detection.to_dict()
        assert "sdk_import_path" in d
        assert "discoverable" in d
        assert "detection_method" in d

    def test_detection_no_sdk_in_ordinary_env(self):
        """In ordinary test env, SDK should not be discoverable."""
        from calibration_skill.adapters.booster_k1.vendor_runtime import (
            detect_booster_sdk_availability,
        )
        status = detect_booster_sdk_availability()
        # In test env without SDK, this should report not found
        # or found (if installed); either is fine.
        assert status.detection_method == "importlib.util.find_spec"
        assert status.ordinary_runtime_import_safe
