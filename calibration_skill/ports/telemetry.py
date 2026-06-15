"""Port interface for telemetry streams."""
from __future__ import annotations

from typing import Protocol

from calibration_skill.domain.telemetry import TelemetrySample


class TelemetryStream(Protocol):
    """Abstract interface for telemetry acquisition.

    Defines explicit start, read, stop, health, and freshness semantics.
    """

    def start(self) -> None:
        """Start the telemetry stream."""
        ...

    def stop(self) -> None:
        """Stop the telemetry stream. Must be callable from any state."""
        ...

    def is_active(self) -> bool:
        """Check if the stream is currently active."""
        ...

    def get_latest(self) -> TelemetrySample | None:
        """Get the most recent sample, or None if no data."""
        ...

    def get_recent(self, duration_ns: int) -> list[TelemetrySample]:
        """Get samples within the last duration_ns nanoseconds."""
        ...

    def health(self) -> dict[str, object]:
        """Get stream health information (active, sample count, error count, etc.)."""
        ...
