import socket
import subprocess
import time

from calibration_skill.domain.enums import MotionLifecycleState
from fakes.fake_booster_k1_runtime import FakeBoosterK1FailureConfig, FakeBoosterK1Runtime


def test_deterministic_connect_disconnect_and_lifecycle():
    runtime = FakeBoosterK1Runtime()
    runtime.connect(timeout_s=1.0)
    runtime.enter_prepare_mode()
    runtime.enter_walking_mode()
    runtime.disconnect()
    assert runtime.calls == [
        "connect:1.0",
        "enter_prepare_mode",
        "enter_walking_mode",
        "disconnect",
    ]
    assert runtime.motion_state == MotionLifecycleState.UNAVAILABLE


def test_command_receipt_stop_restore_and_telemetry_sequence():
    runtime = FakeBoosterK1Runtime()
    receipt = runtime.send_body_velocity(vx_mps=0.2, vy_mps=0.0, wz_radps=0.0)
    stop = runtime.stop()
    runtime.restore_safe_state()
    odom = runtime.read_odometry()
    state = runtime.read_robot_state()
    assert receipt.accepted is True
    assert stop.accepted is True
    assert odom.sequence_id == 1
    assert state.mode_name == "idle"


def test_failure_injection():
    runtime = FakeBoosterK1Runtime(failures=FakeBoosterK1FailureConfig(command_rejection=True, stop_unacknowledged=True))
    assert runtime.send_body_velocity(vx_mps=0.2, vy_mps=0.0, wz_radps=0.0).accepted is False
    assert runtime.stop().accepted is False


def test_fake_runtime_uses_no_socket_subprocess_or_sleep(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(socket, "socket", fail)
    monkeypatch.setattr(subprocess, "Popen", fail)
    monkeypatch.setattr(time, "sleep", fail)
    runtime = FakeBoosterK1Runtime()
    runtime.connect(timeout_s=1.0)
    runtime.enter_prepare_mode()
    runtime.enter_walking_mode()
    runtime.send_body_velocity(vx_mps=0.1, vy_mps=0.0, wz_radps=0.0)
    runtime.stop()
