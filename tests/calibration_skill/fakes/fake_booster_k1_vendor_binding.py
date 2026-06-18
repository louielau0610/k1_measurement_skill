"""Fake vendor binding for M27-D tests.

Implements BoosterK1VendorBindingProtocol with deterministic behavior.
No SDK, no hardware, no network required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.domain.enums import MotionLifecycleState


@dataclass
class FakeBindingFailureConfig:
    connect_failure: bool = False
    disconnect_failure: bool = False
    identity_failure: bool = False
    prepare_failure: bool = False
    walking_failure: bool = False
    velocity_failure: bool = False
    stop_failure: bool = False
    restore_failure: bool = False
    odometry_failure: bool = False
    robot_state_failure: bool = False
    battery_failure: bool = False
    health_failure: bool = False
    command_rejection: bool = False
    stop_unacknowledged: bool = False


@dataclass
class FakeBoosterK1VendorBinding:
    """Deterministic fake vendor binding for M27-D tests.

    Implements BoosterK1VendorBindingProtocol with injectable failures.
    No SDK imports, no hardware, no network.
    """

    interface: str = "fake"
    now_ns_fn: Any = None
    failures: FakeBindingFailureConfig = field(default_factory=FakeBindingFailureConfig)
    connected: bool = field(default=False, init=False)
    motion_state: MotionLifecycleState = field(default=MotionLifecycleState.UNAVAILABLE, init=False)
    _receipt_counter: int = field(default=0, init=False)
    _sequence_counter: int = field(default=0, init=False)
    calls: list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.now_ns_fn is None:
            import time
            self.now_ns_fn = time.monotonic_ns

    def _tick(self) -> int:
        self._sequence_counter += 1
        return self.now_ns_fn()

    def connect(self, *, timeout_s: float) -> None:
        self.calls.append(f"connect:{timeout_s}")
        if self.failures.connect_failure:
            raise RuntimeError("fake K1 binding connect failure")
        self.connected = True
        self.motion_state = MotionLifecycleState.IDLE

    def disconnect(self) -> None:
        self.calls.append("disconnect")
        if self.failures.disconnect_failure:
            raise RuntimeError("fake K1 binding disconnect failure")
        self.connected = False
        self.motion_state = MotionLifecycleState.UNAVAILABLE

    def identity_metadata(self) -> dict[str, object]:
        self.calls.append("identity_metadata")
        if self.failures.identity_failure:
            raise RuntimeError("fake K1 binding identity failure")
        return {
            "sdk_family": "fake_booster_k1",
            "sdk_version": "m27d.fake.1",
            "firmware_version": "fake-fw-v2",
            "hardware_serial": "fake-k1-serial-001",
        }

    def current_motion_state(self) -> MotionLifecycleState:
        self.calls.append("current_motion_state")
        return self.motion_state

    def enter_prepare_mode(self) -> None:
        self.calls.append("enter_prepare_mode")
        if self.failures.prepare_failure:
            raise RuntimeError("fake K1 binding prepare failure")
        self.motion_state = MotionLifecycleState.PREPARING

    def enter_walking_mode(self) -> None:
        self.calls.append("enter_walking_mode")
        if self.failures.walking_failure:
            raise RuntimeError("fake K1 binding walking failure")
        self.motion_state = MotionLifecycleState.LOCOMOTION_READY

    def send_body_velocity(
        self, *, vx_mps: float, vy_mps: float, wz_radps: float
    ) -> BoosterK1RuntimeCommandReceipt:
        self.calls.append(f"send_body_velocity:{vx_mps}:{vy_mps}:{wz_radps}")
        self._receipt_counter += 1
        now_ns = self._tick()
        if self.failures.velocity_failure:
            raise RuntimeError("fake K1 binding velocity failure")
        if self.failures.command_rejection:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"fake-receipt-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail="injected rejection",
            )
        self.motion_state = MotionLifecycleState.MOVING
        return BoosterK1RuntimeCommandReceipt(
            accepted=True,
            runtime_receipt_id=f"fake-receipt-{self._receipt_counter}",
            received_monotonic_ns=now_ns,
            detail="accepted",
        )

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        self.calls.append("stop")
        self._receipt_counter += 1
        now_ns = self._tick()
        if self.failures.stop_failure:
            raise RuntimeError("fake K1 binding stop failure")
        if self.failures.stop_unacknowledged:
            return BoosterK1RuntimeCommandReceipt(
                accepted=False,
                runtime_receipt_id=f"fake-stop-{self._receipt_counter}",
                received_monotonic_ns=now_ns,
                detail="injected stop unacknowledged",
            )
        self.motion_state = MotionLifecycleState.SAFE_STOPPED
        return BoosterK1RuntimeCommandReceipt(
            accepted=True,
            runtime_receipt_id=f"fake-stop-{self._receipt_counter}",
            received_monotonic_ns=now_ns,
            detail="stopped",
        )

    def restore_safe_state(self) -> None:
        self.calls.append("restore_safe_state")
        if self.failures.restore_failure:
            raise RuntimeError("fake K1 binding restore failure")
        self.motion_state = MotionLifecycleState.SAFE_STOPPED

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        self.calls.append("read_odometry")
        if self.failures.odometry_failure:
            raise RuntimeError("fake K1 binding odometry failure")
        return BoosterK1RuntimeOdometry(
            sequence_id=self._sequence_counter,
            sample_monotonic_ns=self.now_ns_fn(),
            x_m=1.0,
            y_m=2.0,
            yaw_rad=0.25,
            vx_mps=0.0,
            vy_mps=0.0,
            wz_radps=0.0,
        )

    def read_robot_state(self) -> BoosterK1RuntimeState:
        self.calls.append("read_robot_state")
        if self.failures.robot_state_failure:
            raise RuntimeError("fake K1 binding robot state failure")
        return BoosterK1RuntimeState(
            motion_state=self.motion_state,
            mode_name="idle" if self.motion_state == MotionLifecycleState.IDLE else str(self.motion_state.value),
            source_monotonic_ns=self.now_ns_fn(),
            battery_percentage=88.0,
            battery_voltage=48.5,
        )

    def read_battery_state(self) -> dict[str, float] | None:
        self.calls.append("read_battery_state")
        if self.failures.battery_failure:
            raise RuntimeError("fake K1 binding battery failure")
        return {"battery_percentage": 88.0, "battery_voltage": 48.5}

    def health_check(self) -> BoosterK1RuntimeHealth:
        self.calls.append("health_check")
        now_ns = self.now_ns_fn()
        if self.failures.health_failure:
            return BoosterK1RuntimeHealth(
                healthy=False,
                checked_monotonic_ns=now_ns,
                detail="injected fake binding health failure",
            )
        return BoosterK1RuntimeHealth(
            healthy=self.connected,
            checked_monotonic_ns=now_ns,
            detail="fake binding healthy" if self.connected else "fake binding not connected",
        )
