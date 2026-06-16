from calibration_skill.adapters.mock import DeterministicMonotonicClock, MockFailureConfig, MockRobotAdapter
from calibration_skill.domain.enums import CommandDisposition, ConnectionState, MotionLifecycleState, RobotPlatform
from calibration_skill.ports.factory import ConnectionConfig

from test_m26c_helpers import authorization, safety_envelope, velocity_command


def _adapter(failures: MockFailureConfig | None = None) -> MockRobotAdapter:
    return MockRobotAdapter(
        config=ConnectionConfig(platform=RobotPlatform.MOCK, robot_id="mock-robot"),
        clock=DeterministicMonotonicClock(),
        failure_config=failures or MockFailureConfig(),
    )


def test_initial_disconnected_state_and_connect_disconnect():
    adapter = _adapter()
    assert adapter.connection_state == ConnectionState.DISCONNECTED
    adapter.connect()
    assert adapter.connection_state == ConnectionState.CONNECTED
    assert adapter.motion_state == MotionLifecycleState.IDLE
    adapter.disconnect()
    assert adapter.connection_state == ConnectionState.DISCONNECTED


def test_preflight_success_and_blocker():
    ok = _adapter()
    ok.connect()
    assert ok.preflight().is_ready
    blocked = _adapter(MockFailureConfig(preflight_blocker=True))
    blocked.connect()
    report = blocked.preflight()
    assert not report.is_ready
    assert report.blockers


def test_locomotion_transition_and_wrong_state_rejection():
    adapter = _adapter()
    adapter.connect()
    adapter.configure_command_context(safety_envelope(), authorization(), "dry_run_velocity_command")
    receipt = adapter.send_velocity_command(velocity_command())
    assert receipt.disposition == CommandDisposition.REJECTED
    assert receipt.rejection_error.code == "wrong_motion_state"
    adapter.enter_locomotion_ready()
    assert adapter.motion_state == MotionLifecycleState.LOCOMOTION_READY


def test_expired_command_rejection():
    adapter = _adapter()
    adapter.connect()
    adapter.enter_locomotion_ready()
    adapter.clock.advance_ns(2_000_000_000)
    adapter.configure_command_context(safety_envelope(), authorization(), "dry_run_velocity_command")
    receipt = adapter.send_velocity_command(velocity_command(expiry_ns=1_500_000_000))
    assert receipt.disposition == CommandDisposition.EXPIRED
    assert receipt.rejection_error.code == "command_expired"


def test_safety_envelope_rejection_and_valid_acceptance():
    adapter = _adapter()
    adapter.connect()
    adapter.enter_locomotion_ready()
    adapter.configure_command_context(safety_envelope(), authorization(), "dry_run_velocity_command")
    rejected = adapter.send_velocity_command(velocity_command(vx=0.9))
    assert rejected.disposition == CommandDisposition.REJECTED
    assert rejected.rejection_error.code == "command_outside_safety_envelope"
    accepted_adapter = _adapter()
    accepted_adapter.connect()
    accepted_adapter.enter_locomotion_ready()
    accepted_adapter.configure_command_context(safety_envelope(), authorization(), "dry_run_velocity_command")
    accepted = accepted_adapter.send_velocity_command(velocity_command())
    assert accepted.disposition == CommandDisposition.ACCEPTED
    assert "no-physical-motion" in accepted.acknowledgement_evidence


def test_stop_success_and_unacknowledged_failure():
    adapter = _adapter()
    adapter.connect()
    assert adapter.stop().disposition == CommandDisposition.ACCEPTED
    failing = _adapter(MockFailureConfig(stop_unacknowledged=True))
    failing.connect()
    receipt = failing.stop()
    assert receipt.disposition == CommandDisposition.REJECTED
    assert receipt.rejection_error.code == "stop_unacknowledged"


def test_deterministic_and_stale_telemetry():
    adapter = _adapter()
    adapter.connect()
    one = adapter.collect_telemetry_sample()
    two = adapter.collect_telemetry_sample()
    assert (one.sample_sequence_id, two.sample_sequence_id) == (1, 2)
    assert one.body_twist.linear.x == 0.0
    stale = _adapter(MockFailureConfig(stale_telemetry=True))
    stale.connect()
    sample = stale.collect_telemetry_sample()
    assert "stale_injected" in sample.quality_flags
    assert sample.is_stale(stale.clock.now_ns(), 1_000_000)


def test_failure_injection_connection_locomotion_and_command():
    conn = _adapter(MockFailureConfig(connection_failure=True))
    try:
        conn.connect()
    except RuntimeError:
        pass
    assert conn.connection_state == ConnectionState.FAULTED
    loco = _adapter(MockFailureConfig(locomotion_transition_failure=True))
    loco.connect()
    try:
        loco.enter_locomotion_ready()
    except RuntimeError:
        pass
    assert loco.motion_state == MotionLifecycleState.FAULTED
    cmd = _adapter(MockFailureConfig(command_rejection=True))
    cmd.connect()
    cmd.enter_locomotion_ready()
    cmd.configure_command_context(safety_envelope(), authorization(), "dry_run_velocity_command")
    assert cmd.send_velocity_command(velocity_command()).rejection_error.code == "precondition_failed"
