"""M27-D vendor runtime tests.

Tests for BoosterK1VendorRuntime with injected fake binding.
No real SDK or hardware required.
"""
from __future__ import annotations

import time

import pytest

from calibration_skill.adapters.booster_k1.config import BoosterK1HardwareGate, K1_VENDOR_RUNTIME_MODE
from calibration_skill.adapters.booster_k1.errors import (
    ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN,
    ERROR_K1_VENDOR_RUNTIME_DISCONNECTED,
    ERROR_K1_VENDOR_RUNTIME_NOT_LOCOMOTION_READY,
)
from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.adapters.booster_k1.vendor_runtime import (
    BoosterK1RuntimeUnavailable,
    BoosterK1VendorRuntime,
    BoosterK1VendorRuntimeStatus,
    create_booster_k1_vendor_runtime,
    detect_booster_sdk_availability,
)
from calibration_skill.domain.enums import MotionLifecycleState
from calibration_skill.adapters.booster_k1.errors import BoosterK1DomainError
from tests.calibration_skill.fakes.fake_booster_k1_vendor_binding import (
    FakeBindingFailureConfig,
    FakeBoosterK1VendorBinding,
)


def _valid_gate(**overrides) -> BoosterK1HardwareGate:
    """Build a valid hardware gate for testing."""
    kwargs = {
        "allow_hardware": True,
        "operator_confirmed_hardware": True,
        "hardware_session_id": "test-session",
        "safety_policy_id": "test-policy",
        "safety_policy_hash": "test-hash",
        "expected_robot_id": "k1-test",
        "expected_adapter_mode": K1_VENDOR_RUNTIME_MODE,
        "require_physical_estop_confirmation": True,
        "require_clear_test_area_confirmation": True,
        "require_battery_state_confirmation": True,
        "require_network_isolation_confirmation": True,
        "require_manual_operator_present": True,
        "evidence_reference": "test-evidence",
        "expires_monotonic_ns": 999999999999999999,
    }
    kwargs.update(overrides)
    return BoosterK1HardwareGate(**kwargs)


def _fixed_clock(start_ns: int = 1_000_000_000):
    """Return a clock function that returns fixed values."""
    current = [start_ns]

    def clock() -> int:
        val = current[0]
        current[0] += 10_000_000
        return val

    return clock


class TestVendorRuntimeLifecycle:
    """Tests for vendor runtime connect/disconnect lifecycle."""

    def test_connect_and_disconnect(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        assert runtime.now_ns() > 0
        runtime.connect(timeout_s=5.0)
        assert runtime.current_motion_state() == MotionLifecycleState.IDLE

        runtime.disconnect()
        # After disconnect, state reads should return safe defaults
        state = runtime.read_robot_state()
        assert state.motion_state == MotionLifecycleState.UNAVAILABLE

    def test_connect_idempotent(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        runtime.connect(timeout_s=5.0)
        runtime.connect(timeout_s=5.0)  # Should not error
        assert runtime.current_motion_state() == MotionLifecycleState.IDLE

    def test_disconnect_idempotent(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        runtime.connect(timeout_s=5.0)
        runtime.disconnect()
        runtime.disconnect()  # Should not error

    def test_identity_metadata(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)

        identity = runtime.identity_metadata()
        assert identity["sdk_family"] == "fake_booster_k1"

    def test_identity_metadata_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.identity_metadata()
        assert exc.value.code == ERROR_K1_VENDOR_RUNTIME_DISCONNECTED

    def test_enter_prepare_mode(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)

        runtime.enter_prepare_mode()
        assert runtime.current_motion_state() == MotionLifecycleState.PREPARING

    def test_enter_walking_mode(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_prepare_mode()

        runtime.enter_walking_mode()
        assert runtime.current_motion_state() == MotionLifecycleState.LOCOMOTION_READY

    def test_reject_command_while_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_VENDOR_RUNTIME_DISCONNECTED

    def test_reject_command_before_locomotion_ready(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_VENDOR_RUNTIME_NOT_LOCOMOTION_READY

    def test_normalize_run_state_after_disconnect(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        state = runtime.read_robot_state()
        assert state.motion_state == MotionLifecycleState.UNAVAILABLE
        assert state.mode_name == "disconnected"

    def test_read_odometry_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        odom = runtime.read_odometry()
        assert odom is None

    def test_read_battery_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        battery = runtime.read_battery_state()
        assert battery is None

    def test_health_check_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        health = runtime.health_check()
        assert not health.healthy
        assert "disconnected" in health.detail.lower()

    def test_stop_while_disconnected(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        receipt = runtime.stop()
        assert not receipt.accepted

    def test_restore_safe_state_never_raises(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)

        # Should not raise even when disconnected
        runtime.restore_safe_state()

    def test_injectable_clock(self):
        clock = _fixed_clock(1000)
        binding = FakeBoosterK1VendorBinding(now_ns_fn=clock)
        runtime = BoosterK1VendorRuntime(binding=binding, clock_fn=clock)

        t1 = runtime.now_ns()
        t2 = runtime.now_ns()
        assert t2 > t1
        assert t1 == 1000


class TestVendorRuntimeZeroMotion:
    """Tests for zero-motion enforcement in vendor runtime."""

    def test_reject_nonzero_vx(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.35, vy_mps=0.0, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_reject_nonzero_vy(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.1, wz_radps=0.0)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_reject_nonzero_wz(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        with pytest.raises(BoosterK1DomainError) as exc:
            runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.3)
        assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_reject_known_k1_commands(self):
        """Verify known K1 command velocities 0.35-0.60 are rejected."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        for v in [0.35, 0.40, 0.50, 0.60]:
            with pytest.raises(BoosterK1DomainError) as exc:
                runtime.send_body_velocity(vx_mps=v, vy_mps=0.0, wz_radps=0.0)
            assert exc.value.code == ERROR_K1_M27D_NONZERO_MOTION_FORBIDDEN

    def test_accept_zero_motion(self):
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        receipt = runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert receipt.accepted

    def test_tolerance_microscopic(self):
        """Values just above epsilon should still be rejected."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        # 1e-8 > 1e-9 epsilon
        with pytest.raises(BoosterK1DomainError):
            runtime.send_body_velocity(vx_mps=1e-8, vy_mps=0.0, wz_radps=0.0)

    def test_accept_sub_epsilon(self):
        """Values within epsilon should be accepted."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        receipt = runtime.send_body_velocity(vx_mps=1e-10, vy_mps=0.0, wz_radps=0.0)
        assert receipt.accepted


class TestVendorRuntimeFailureModes:
    """Tests for various failure modes."""

    def test_runtime_catches_binding_exception(self):
        binding = FakeBoosterK1VendorBinding(
            failures=FakeBindingFailureConfig(velocity_failure=True)
        )
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        receipt = runtime.send_body_velocity(vx_mps=0.0, vy_mps=0.0, wz_radps=0.0)
        assert not receipt.accepted
        assert "Vendor binding error" in receipt.detail

    def test_safe_restoration_after_failure(self):
        """Safe restoration should still be attempted after failures."""
        binding = FakeBoosterK1VendorBinding(
            failures=FakeBindingFailureConfig(velocity_failure=True)
        )
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.enter_walking_mode()

        try:
            runtime.send_body_velocity(vx_mps=500.0, vy_mps=0.0, wz_radps=0.0)
        except BoosterK1DomainError:
            pass

        # Safe restoration should not raise
        runtime.restore_safe_state()

    def test_disconnect_attempted_in_finally(self):
        """Disconnect should succeed even if binding had issues."""
        binding = FakeBoosterK1VendorBinding()
        runtime = BoosterK1VendorRuntime(binding=binding)
        runtime.connect(timeout_s=5.0)
        runtime.disconnect()

        # After disconnect, operations return safe defaults
        odom = runtime.read_odometry()
        assert odom is None


class TestCreateVendorRuntime:
    """Tests for the create_booster_k1_vendor_runtime factory."""

    def test_missing_gate(self):
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=None,
                now_ns=0,
                expected_robot_id="test",
                expected_safety_policy_id="test",
                expected_safety_policy_hash="test",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )

    def test_expired_gate(self):
        gate = _valid_gate(expires_monotonic_ns=100)
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=1000,
                expected_robot_id="k1-test",
                expected_safety_policy_id="test-policy",
                expected_safety_policy_hash="test-hash",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )

    def test_wrong_robot_id(self):
        gate = _valid_gate(expected_robot_id="k1-test")
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=0,
                expected_robot_id="wrong-robot",
                expected_safety_policy_id="test-policy",
                expected_safety_policy_hash="test-hash",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )

    def test_wrong_safety_policy_id(self):
        gate = _valid_gate(safety_policy_id="test-policy")
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=0,
                expected_robot_id="k1-test",
                expected_safety_policy_id="wrong-policy",
                expected_safety_policy_hash="test-hash",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )

    def test_wrong_safety_policy_hash(self):
        gate = _valid_gate(safety_policy_hash="test-hash")
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=0,
                expected_robot_id="k1-test",
                expected_safety_policy_id="test-policy",
                expected_safety_policy_hash="wrong-hash",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )

    def test_not_enabled(self):
        gate = _valid_gate()
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=0,
                expected_robot_id="k1-test",
                expected_safety_policy_id="test-policy",
                expected_safety_policy_hash="test-hash",
                enable_vendor_runtime=False,
                execute_hardware=False,
            )

    def test_incomplete_confirmations(self):
        gate = _valid_gate(operator_confirmed_hardware=False)
        with pytest.raises(BoosterK1RuntimeUnavailable):
            create_booster_k1_vendor_runtime(
                hardware_gate=gate,
                now_ns=0,
                expected_robot_id="k1-test",
                expected_safety_policy_id="test-policy",
                expected_safety_policy_hash="test-hash",
                enable_vendor_runtime=True,
                execute_hardware=False,
            )
