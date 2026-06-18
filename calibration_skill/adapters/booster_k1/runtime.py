"""Runtime protocol boundary for K1 SDK-like behavior.

M27-B defines only this injected protocol. No real Booster SDK runtime is
implemented or imported here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from calibration_skill.domain.enums import MotionLifecycleState


@dataclass(frozen=True)
class BoosterK1RuntimeHealth:
    healthy: bool
    checked_monotonic_ns: int
    detail: str = ""
    scope: str = "binding_readiness"
    communication_verified: bool = False


@dataclass(frozen=True)
class BoosterK1RuntimeCommandReceipt:
    accepted: bool
    runtime_receipt_id: str
    received_monotonic_ns: int
    detail: str = ""
    zero_command_accepted: bool = False
    stop_command_accepted: bool = False
    physical_stop_verified: bool = False
    internal_command_state: str = ""


@dataclass(frozen=True)
class BoosterK1RuntimeOdometry:
    sequence_id: int
    sample_monotonic_ns: int
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0
    yaw_rad: float | None = None
    vx_mps: float | None = None
    vy_mps: float | None = None
    wz_radps: float | None = None


@dataclass(frozen=True)
class BoosterK1RuntimeState:
    motion_state: MotionLifecycleState
    mode_name: str
    source_monotonic_ns: int
    battery_percentage: float | None = None
    battery_voltage: float | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class BoosterK1RuntimeProtocol(Protocol):
    """Minimal injected runtime surface needed by BoosterK1Adapter."""

    def now_ns(self) -> int:
        ...

    def connect(self, *, timeout_s: float) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def identity_metadata(self) -> dict[str, object]:
        ...

    def current_motion_state(self) -> MotionLifecycleState:
        ...

    def enter_prepare_mode(self) -> None:
        ...

    def enter_walking_mode(self) -> None:
        ...

    def send_body_velocity(self, *, vx_mps: float, vy_mps: float, wz_radps: float) -> BoosterK1RuntimeCommandReceipt:
        ...

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        ...

    def restore_safe_state(self) -> None:
        ...

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        ...

    def read_robot_state(self) -> BoosterK1RuntimeState:
        ...

    def read_battery_state(self) -> dict[str, float] | None:
        ...

    def health_check(self) -> BoosterK1RuntimeHealth:
        ...
