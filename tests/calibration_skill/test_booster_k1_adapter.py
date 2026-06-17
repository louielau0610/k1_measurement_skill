from calibration_skill.adapters.booster_k1.adapter import BoosterK1Adapter
from calibration_skill.adapters.booster_k1.errors import ERROR_K1_UNSUPPORTED_AXIS
from calibration_skill.domain.enums import CommandDisposition, ConnectionState, CoordinateFrame, MotionLifecycleState, RobotPlatform
from calibration_skill.domain.errors import (
    ERROR_ADAPTER_DISCONNECTED,
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_STOP_UNACKNOWLEDGED,
    ERROR_WRONG_MOTION_STATE,
)
from calibration_skill.domain.motion import VelocityCommand
from calibration_skill.domain.safety import OperatorAuthorization
from fakes.fake_booster_k1_runtime import FakeBoosterK1FailureConfig, FakeBoosterK1Runtime
from test_booster_k1_config import valid_config


def command(**overrides):
    data = {
        "vx_mps": 0.2,
        "vy_mps": 0.0,
        "wz_radps": 0.0,
        "sequence_id": "cmd-1",
        "issued_monotonic_ns": 1_000_000_000,
        "expiry_monotonic_ns": 2_000_000_000,
        "requested_duration_s": 0.2,
        "frame": CoordinateFrame.BODY,
        "safety_policy_id": "k1-safe",
        "safety_policy_hash": "hash",
        "source": "test",
    }
    data.update(overrides)
    return VelocityCommand(**data)


def authorization(**overrides):
    data = {
        "authorization_id": "auth",
        "operator_id": "operator",
        "platform": RobotPlatform.BOOSTER_K1,
        "robot_id": "k1-test",
        "issued_monotonic_ns": 0,
        "expiry_monotonic_ns": 3_000_000_000,
        "authorized_operations": ("k1_fake_runtime_velocity_command",),
        "safety_policy_id": "k1-safe",
        "safety_policy_hash": "hash",
        "evidence_reference": "test",
    }
    data.update(overrides)
    return OperatorAuthorization(**data)


def adapter(runtime=None, **config_overrides):
    return BoosterK1Adapter(config=valid_config(**config_overrides), runtime=runtime or FakeBoosterK1Runtime())


def ready_adapter():
    k1 = adapter()
    k1.connect()
    k1.enter_locomotion_ready()
    k1.configure_command_context(k1.safety_envelope, authorization(), "k1_fake_runtime_velocity_command")
    return k1


def test_initial_disconnected_and_connect():
    k1 = adapter()
    assert k1.connection_state == ConnectionState.DISCONNECTED
    k1.connect()
    assert k1.connection_state == ConnectionState.CONNECTED


def test_preflight_success_and_health_failure():
    assert adapter().preflight().is_ready is True
    unhealthy = adapter(runtime=FakeBoosterK1Runtime(failures=FakeBoosterK1FailureConfig(health_failure=True)))
    assert unhealthy.preflight().is_ready is False


def test_enter_locomotion_ready_sequence():
    runtime = FakeBoosterK1Runtime()
    k1 = adapter(runtime=runtime)
    k1.connect()
    k1.enter_locomotion_ready()
    assert runtime.calls[-2:] == ["enter_prepare_mode", "enter_walking_mode"]
    assert k1.motion_state == MotionLifecycleState.LOCOMOTION_READY


def test_command_rejected_when_disconnected():
    receipt = adapter().send_velocity_command(command())
    assert receipt.disposition == CommandDisposition.REJECTED
    assert receipt.rejection_error.code == ERROR_ADAPTER_DISCONNECTED


def test_command_rejected_when_wrong_state():
    k1 = adapter()
    k1.connect()
    receipt = k1.send_velocity_command(command())
    assert receipt.rejection_error.code == ERROR_WRONG_MOTION_STATE


def test_expired_command_rejected():
    k1 = ready_adapter()
    receipt = k1.send_velocity_command(command(expiry_monotonic_ns=1_000_000_001))
    assert receipt.disposition == CommandDisposition.EXPIRED
    assert receipt.rejection_error.code == ERROR_COMMAND_EXPIRED


def test_safety_violation_rejected_and_cleanup_stop_called():
    runtime = FakeBoosterK1Runtime()
    k1 = ready_adapter()
    k1.runtime = runtime
    receipt = k1.send_velocity_command(command(vx_mps=0.7))
    assert receipt.rejection_error.code == ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE
    assert "stop" in runtime.calls


def test_vy_wz_rejected_if_unsupported():
    k1 = ready_adapter()
    receipt = k1.send_velocity_command(command(vy_mps=0.01))
    assert receipt.rejection_error.code == ERROR_K1_UNSUPPORTED_AXIS


def test_valid_vx_command_accepted():
    k1 = ready_adapter()
    receipt = k1.send_velocity_command(command())
    assert receipt.disposition == CommandDisposition.ACCEPTED
    assert receipt.acknowledgement_evidence.endswith("no-physical-motion")


def test_stop_success_and_unacknowledged():
    assert ready_adapter().stop().disposition == CommandDisposition.ACCEPTED
    k1 = adapter(runtime=FakeBoosterK1Runtime(failures=FakeBoosterK1FailureConfig(stop_unacknowledged=True)))
    assert k1.stop().rejection_error.code == ERROR_STOP_UNACKNOWLEDGED


def test_restore_safe_state_and_telemetry_normalized():
    k1 = ready_adapter()
    k1.restore_safe_state()
    sample = k1.collect_telemetry_sample()
    assert k1.motion_state == MotionLifecycleState.SAFE_STOPPED
    assert sample.robot_id == "k1-test"
    assert sample.body_twist.linear.x == 0.3
    assert sample.heading_rad == 0.25
