"""Robot identity value object."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import RobotMorphology, RobotPlatform
from calibration_skill.domain.errors import DomainError, ERROR_INVALID_IDENTIFIER, validation_error


@dataclass(frozen=True)
class RobotIdentity:
    """Immutable robot identity.

    Does not infer identity from directory names or environment variables.
    All fields are explicit.
    """
    platform: RobotPlatform
    morphology: RobotMorphology
    robot_id: str
    adapter_name: str
    adapter_version: str
    hardware_serial: str | None = None
    firmware_version: str | None = None
    sdk_family: str | None = None
    sdk_version: str | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not self.robot_id or not self.robot_id.strip():
            errors.append("robot_id must be a non-empty string")
        if not self.adapter_name or not self.adapter_name.strip():
            errors.append("adapter_name must be a non-empty string")
        if not self.adapter_version or not self.adapter_version.strip():
            errors.append("adapter_version must be a non-empty string")
        if errors:
            raise ValueError("; ".join(errors))

    def validate(self) -> list[DomainError]:
        """Validate all identity fields. Returns list of errors (empty if valid)."""
        errors: list[DomainError] = []
        if not self.robot_id or not self.robot_id.strip():
            errors.append(validation_error("robot_id is empty", details={"field": "robot_id"}))
        if not self.adapter_name or not self.adapter_name.strip():
            errors.append(validation_error("adapter_name is empty", details={"field": "adapter_name"}))
        if not self.adapter_version or not self.adapter_version.strip():
            errors.append(validation_error("adapter_version is empty", details={"field": "adapter_version"}))
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dictionary."""
        result: dict[str, Any] = {
            "platform": self.platform.value,
            "morphology": self.morphology.value,
            "robot_id": self.robot_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
        }
        if self.hardware_serial is not None:
            result["hardware_serial"] = self.hardware_serial
        if self.firmware_version is not None:
            result["firmware_version"] = self.firmware_version
        if self.sdk_family is not None:
            result["sdk_family"] = self.sdk_family
        if self.sdk_version is not None:
            result["sdk_version"] = self.sdk_version
        if self.metadata:
            result["metadata"] = dict(self.metadata)
        return result

    def __repr__(self) -> str:
        return f"RobotIdentity(platform={self.platform.value}, robot_id={self.robot_id!r})"
