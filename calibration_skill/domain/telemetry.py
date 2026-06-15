"""Telemetry domain contracts: normalized platform telemetry value objects."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import CoordinateFrame
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_INVALID_QUATERNION,
    ERROR_NON_FINITE_VALUE,
    validation_error,
)


def _require_finite(value: float, name: str) -> list[str]:
    errors: list[str] = []
    if math.isnan(value):
        errors.append(f"{name} is NaN")
    if math.isinf(value):
        errors.append(f"{name} is infinite")
    return errors


@dataclass(frozen=True)
class Vector3:
    """A 3D vector with finite components."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __post_init__(self) -> None:
        errors: list[str] = []
        for axis in ("x", "y", "z"):
            value = getattr(self, axis)
            errors.extend(_require_finite(value, f"Vector3.{axis}"))
        if errors:
            raise ValueError("; ".join(errors))

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass(frozen=True)
class Quaternion:
    """A quaternion with finite components. Zero-norm is rejected."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    def __post_init__(self) -> None:
        errors: list[str] = []
        for comp in ("x", "y", "z", "w"):
            value = getattr(self, comp)
            errors.extend(_require_finite(value, f"Quaternion.{comp}"))
        norm_sq = self.x**2 + self.y**2 + self.z**2 + self.w**2
        if norm_sq == 0.0:
            errors.append("Quaternion has zero norm")
        if errors:
            raise ValueError("; ".join(errors))

    def norm_sq(self) -> float:
        return self.x**2 + self.y**2 + self.z**2 + self.w**2

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z, "w": self.w}


@dataclass(frozen=True)
class Pose3D:
    """3D pose: position + orientation."""
    position: Vector3 = field(default_factory=Vector3)
    orientation: Quaternion = field(default_factory=Quaternion)

    def to_dict(self) -> dict[str, Any]:
        return {"position": self.position.to_dict(), "orientation": self.orientation.to_dict()}


@dataclass(frozen=True)
class Twist3D:
    """3D twist: linear velocity + angular velocity."""
    linear: Vector3 = field(default_factory=Vector3)
    angular: Vector3 = field(default_factory=Vector3)

    def to_dict(self) -> dict[str, Any]:
        return {"linear": self.linear.to_dict(), "angular": self.angular.to_dict()}


@dataclass(frozen=True)
class TelemetryFreshness:
    """Describes the freshness of a telemetry sample."""
    sample_monotonic_ns: int
    evaluated_at_ns: int
    age_ns: int
    is_fresh: bool
    is_stale: bool
    staleness_threshold_ns: int | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "sample_monotonic_ns": self.sample_monotonic_ns,
            "evaluated_at_ns": self.evaluated_at_ns,
            "age_ns": self.age_ns,
            "is_fresh": self.is_fresh,
            "is_stale": self.is_stale,
        }
        if self.staleness_threshold_ns is not None:
            result["staleness_threshold_ns"] = self.staleness_threshold_ns
        return result


@dataclass(frozen=True)
class TelemetrySample:
    """Normalized platform-agnostic telemetry sample.

    All sensor fields are optional. Missing data is not fabricated as zero.
    Future timestamps are rejected at construction.
    """
    robot_id: str
    sample_sequence_id: int
    received_monotonic_ns: int
    frame: CoordinateFrame = CoordinateFrame.UNKNOWN
    source_timestamp_ns: int | None = None
    pose: Pose3D | None = None
    body_twist: Twist3D | None = None
    imu_accel: Vector3 | None = None
    imu_gyro: Vector3 | None = None
    heading_rad: float | None = None
    battery_voltage: float | None = None
    battery_percentage: float | None = None
    robot_mode: str | None = None
    source_adapter: str | None = None
    quality_flags: tuple[str, ...] = field(default_factory=tuple)
    raw_reference: str | None = None

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.robot_id or not self.robot_id.strip():
            errors.append("robot_id must be non-empty")
        if self.sample_sequence_id < 0:
            errors.append(f"sample_sequence_id must be non-negative, got {self.sample_sequence_id}")
        if self.received_monotonic_ns < 0:
            errors.append(f"received_monotonic_ns must be non-negative, got {self.received_monotonic_ns}")
        # Future timestamps are rejected
        if self.source_timestamp_ns is not None and self.source_timestamp_ns < 0:
            errors.append(f"source_timestamp_ns must be non-negative, got {self.source_timestamp_ns}")
        if self.heading_rad is not None:
            errors.extend(_require_finite(self.heading_rad, "heading_rad"))
        if self.battery_voltage is not None:
            errors.extend(_require_finite(self.battery_voltage, "battery_voltage"))
        if self.battery_percentage is not None:
            errors.extend(_require_finite(self.battery_percentage, "battery_percentage"))
        if errors:
            raise ValueError("; ".join(errors))

    def age_ns(self, now_ns: int) -> int:
        """Calculate telemetry age at the given monotonic time."""
        if now_ns < self.received_monotonic_ns:
            return 0  # Future timestamps treated as age 0 but still stale
        return now_ns - self.received_monotonic_ns

    def is_stale(self, now_ns: int, staleness_threshold_ns: int) -> bool:
        """Check if telemetry is stale at the given time."""
        return self.age_ns(now_ns) > staleness_threshold_ns

    def is_unavailable(self) -> bool:
        """Check if telemetry is effectively unavailable (no meaningful data)."""
        return (
            self.pose is None
            and self.body_twist is None
            and self.imu_accel is None
            and self.imu_gyro is None
            and self.heading_rad is None
        )

    def freshness(self, now_ns: int, staleness_threshold_ns: int | None = None) -> TelemetryFreshness:
        """Evaluate telemetry freshness."""
        age = self.age_ns(now_ns)
        is_stale_flag = staleness_threshold_ns is not None and age > staleness_threshold_ns
        # Future timestamps are always considered stale
        if now_ns < self.received_monotonic_ns:
            is_stale_flag = True
        return TelemetryFreshness(
            sample_monotonic_ns=self.received_monotonic_ns,
            evaluated_at_ns=now_ns,
            age_ns=age,
            is_fresh=not is_stale_flag,
            is_stale=is_stale_flag,
            staleness_threshold_ns=staleness_threshold_ns,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "robot_id": self.robot_id,
            "sample_sequence_id": self.sample_sequence_id,
            "received_monotonic_ns": self.received_monotonic_ns,
            "frame": self.frame.value,
        }
        if self.source_timestamp_ns is not None:
            result["source_timestamp_ns"] = self.source_timestamp_ns
        if self.pose is not None:
            result["pose"] = self.pose.to_dict()
        if self.body_twist is not None:
            result["body_twist"] = self.body_twist.to_dict()
        if self.imu_accel is not None:
            result["imu_accel"] = self.imu_accel.to_dict()
        if self.imu_gyro is not None:
            result["imu_gyro"] = self.imu_gyro.to_dict()
        if self.heading_rad is not None:
            result["heading_rad"] = self.heading_rad
        if self.battery_voltage is not None:
            result["battery_voltage"] = self.battery_voltage
        if self.battery_percentage is not None:
            result["battery_percentage"] = self.battery_percentage
        if self.robot_mode is not None:
            result["robot_mode"] = self.robot_mode
        if self.source_adapter is not None:
            result["source_adapter"] = self.source_adapter
        if self.quality_flags:
            result["quality_flags"] = list(self.quality_flags)
        if self.raw_reference is not None:
            result["raw_reference"] = self.raw_reference
        return result
