"""Port interface for profile storage."""
from __future__ import annotations

from typing import Protocol

from calibration_skill.domain.calibration import CalibrationProfile


class ProfileRepository(Protocol):
    """Abstract interface for immutable profile storage.

    Defines publication and retrieval semantics.
    Does not implement filesystem storage.
    """

    def publish(self, profile: CalibrationProfile) -> None:
        """Publish a calibration profile. Immutable: once published, cannot be overwritten."""
        ...

    def get(self, profile_id: str) -> CalibrationProfile | None:
        """Retrieve a profile by ID."""
        ...

    def list_by_platform(self, platform_id: str) -> list[CalibrationProfile]:
        """List all profiles for a given platform."""
        ...

    def get_gold(self, platform_id: str) -> CalibrationProfile | None:
        """Get the gold profile for a platform, if one exists."""
        ...
