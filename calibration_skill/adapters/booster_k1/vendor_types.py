"""Vendor binding types and protocol for Booster K1 SDK integration.

M27-D: Defines the narrow internal protocol representing only the SDK
operations required by BoosterK1RuntimeProtocol. No SDK objects are
exposed through this boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from calibration_skill.adapters.booster_k1.runtime import (
    BoosterK1RuntimeCommandReceipt,
    BoosterK1RuntimeHealth,
    BoosterK1RuntimeOdometry,
    BoosterK1RuntimeState,
)
from calibration_skill.domain.enums import MotionLifecycleState


@dataclass(frozen=True)
class BoosterK1VendorBindingMetadata:
    """Structured metadata about the vendor binding implementation."""
    binding_class: str
    sdk_family: str
    sdk_version: str | None
    binding_version: str
    sdk_import_path: str
    sdk_entry_classes: tuple[str, ...]
    verified_motion_sequence: tuple[str, ...]
    zero_motion_only: bool
    support_level: str
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "binding_class": self.binding_class,
            "sdk_family": self.sdk_family,
            "sdk_version": self.sdk_version,
            "binding_version": self.binding_version,
            "sdk_import_path": self.sdk_import_path,
            "sdk_entry_classes": list(self.sdk_entry_classes),
            "verified_motion_sequence": list(self.verified_motion_sequence),
            "zero_motion_only": self.zero_motion_only,
            "support_level": self.support_level,
            "note": self.note,
        }


class BoosterK1VendorBindingProtocol(Protocol):
    """Narrow internal protocol for SDK operations needed by the runtime.

    This protocol defines only the operations required by
    BoosterK1RuntimeProtocol. No raw vendor SDK objects escape through
    this boundary.
    """

    def connect(self, *, timeout_s: float) -> None:
        """Establish SDK channel and initialize client."""
        ...

    def disconnect(self) -> None:
        """Close SDK channel and release resources."""
        ...

    def identity_metadata(self) -> dict[str, object]:
        """Return structured identity metadata from the SDK/robot."""
        ...

    def current_motion_state(self) -> MotionLifecycleState:
        """Return the current motion lifecycle state."""
        ...

    def enter_prepare_mode(self) -> None:
        """Transition the robot into kPrepare mode."""
        ...

    def enter_walking_mode(self) -> None:
        """Transition the robot into kWalking mode."""
        ...

    def send_body_velocity(
        self,
        *,
        vx_mps: float,
        vy_mps: float,
        wz_radps: float,
    ) -> BoosterK1RuntimeCommandReceipt:
        """Send a body-frame velocity command to the robot.

        M27-D zero-motion: only (0.0, 0.0, 0.0) is permitted.
        """
        ...

    def stop(self) -> BoosterK1RuntimeCommandReceipt:
        """Issue an explicit stop/zero command."""
        ...

    def restore_safe_state(self) -> None:
        """Restore the robot to a safe non-moving state."""
        ...

    def read_odometry(self) -> BoosterK1RuntimeOdometry | None:
        """Read current odometry if available."""
        ...

    def read_robot_state(self) -> BoosterK1RuntimeState:
        """Read current robot state."""
        ...

    def read_battery_state(self) -> dict[str, float] | None:
        """Read current battery state if available."""
        ...

    def health_check(self) -> BoosterK1RuntimeHealth:
        """Check SDK and communication health."""
        ...


@dataclass(frozen=True)
class BoosterK1VendorSDKDetection:
    """Result of detecting the Booster SDK without importing it."""
    sdk_import_path: str
    discoverable: bool
    detection_method: str
    sdk_entry_classes: tuple[str, ...]
    verified_imports_found: bool
    detection_errors: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "sdk_import_path": self.sdk_import_path,
            "discoverable": self.discoverable,
            "detection_method": self.detection_method,
            "sdk_entry_classes": list(self.sdk_entry_classes),
            "verified_imports_found": self.verified_imports_found,
            "detection_errors": list(self.detection_errors),
        }
