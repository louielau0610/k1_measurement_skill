"""Deterministic fake Booster K1 runtime for M27-B tests."""
from __future__ import annotations

from dataclasses import dataclass, field

from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.domain.enums import MotionLifecycleState


@dataclass
class FakeBoosterK1FailureConfig:
    connect_failure: bool = False
    health_failure: bool = False
    command_rejection: bool = False
    stop_unacknowledged: bool = False
    telemetry_unavailable: bool = False


@dataclass
class FakeBoosterK1Runtime:
    """Socket-free, sleep-free fake runtime with deterministic monotonic time."""
    robot_id: str = "k1-test"
    now_value_ns: int = 1_000_000_000
    step_ns: int = 10_000_000
    failures: FakeBoosterK1FailureConfig = field(default_factory=FakeBoosterK1FailureConfig)
    calls: list[str] = field(default_factory=list)
    connected: bool = False
    motion_state: MotionLifecycleState = MotionLifecycleState.UNAVAILABLE
    odometry_sequence: list[BoosterK1RuntimeOdometry] = field(default_factory=list)
    state_sequence: list[BoosterK1RuntimeState] = field(default_factory=list)
    receipt_count: int = 0

    def __post_init__(self) -> None:
        if not self.odometry_sequence:
            self.odometry_sequence.append(BoosterK1RuntimeOdometry(
                sequence_id=1,
                sample_monotonic_ns=self.now_value_ns,
                x_m=1.0,
                y_m=2.0,
                yaw_rad=0.25,
                vx_mps=0.3,
                vy_mps=0.0,
                wz_radps=0.0,
            ))
        if not self.state_sequence:
            self.state_sequence.append(BoosterK1RuntimeState(
                motion_state=MotionLifecycleState.IDLE,
                mode_name="idle",
                source_monotonic_ns=self.now_value_ns,
                battery_percentage=88.0,
                battery_voltage=48.5,
            ))

    def now_ns(self) -> int:
        return self.now_value_ns

    def tick(self) -> int:
        self.now_value_ns += self.step_ns
        return self.now_value_ns

    def connect(self, *, timeout_s: float) -> None:
        self.calls.append(f"connect:{timeout_s}")
        if self.failures.connect_failure:
            raise RuntimeError("fake K1 connect failure")
        self.connected = True
        self.motion_state = MotionLifecycleState.IDLE
        self.tick()

    def disconnect(self) -> None:
        self.calls.append("disconnect")
        self.connected = False
        self.motion_state = MotionLifecycleState.UNAVAILABLE
        self.tick()

    def identity_metadata(self) -> dict[str, object]:
        self.calls.append("identity_metadata")
        return {
            "sdk_family": "fake_booster",
            "sdk_version": "m27b.fake",
            "firmware_version": "fake-fw",
            "hardware_serial": "fake-serial",
        }

    def current_motion_state(self) -> MotionLifecycleState:
        self.calls.append("current_motion_state")
        return self.motion_state

    def enter_prepare_mode(self) -> None:
        self.calls.append("enter_prepare_mode")
        self.motion_state = MotionLifecycleState.PREPARING
        self.tick()

    def enter_walking_mode(self) -> None:
        self.calls.append("enter_walking_mode")
        self.motion_state = MotionLifecycleState.LOCOMOTION_READY
        self.tick()

    def send_body_velocity(self, *, vx_mps: float, vy_mps: float, wz_radps: float) -> BoosterK1RuntimeCommandReceipt:
        self.calls.append(f"send_body_velocity:{vx_mps}:{vy_mps}:{wz_radps}")
        self.receipt_count += 1
        now_ns = self.tick()
        if self.failures.command_rejection:
            return BoosterK1RuntimeCommandReceipt(False, f"k1-fake-receipt-{self.receipt_count}", now_ns, "injected rejection")
        self.motion_state = MotionLifecycleState.MOVING
        return BoosterK1RuntimeCommandReceipt(True, f"k1-fake-receipt-{self.receipt_count}", now_ns, "accepted")

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        self.calls.append("stop")
        self.receipt_count += 1
        now_ns = self.tick()
        if self.failures.stop_unacknowledged:
            return BoosterK1RuntimeCommandReceipt(False, f"k1-fake-stop-{self.receipt_count}", now_ns, "injected stop failure")
        self.motion_state = MotionLifecycleState.SAFE_STOPPED
        return BoosterK1RuntimeCommandReceipt(True, f"k1-fake-stop-{self.receipt_count}", now_ns, "stopped")

    def restore_safe_state(self) -> None:
        self.calls.append("restore_safe_state")
        self.motion_state = MotionLifecycleState.SAFE_STOPPED
        self.tick()

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        self.calls.append("read_odometry")
        if self.failures.telemetry_unavailable:
            return None
        return self.odometry_sequence[0]

    def read_robot_state(self) -> BoosterK1RuntimeState:
        self.calls.append("read_robot_state")
        return self.state_sequence[0]

    def read_battery_state(self) -> dict[str, float] | None:
        self.calls.append("read_battery_state")
        return {"battery_percentage": 88.0, "battery_voltage": 48.5}

    def health_check(self) -> BoosterK1RuntimeHealth:
        self.calls.append("health_check")
        now_ns = self.tick()
        if self.failures.health_failure:
            return BoosterK1RuntimeHealth(False, now_ns, "injected fake runtime health failure")
        return BoosterK1RuntimeHealth(True, now_ns, "fake runtime healthy")
