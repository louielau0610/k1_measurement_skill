"""Port interface for emergency stop."""
from __future__ import annotations

from typing import Protocol


class EmergencyStop(Protocol):
    """Abstract interface for emergency stop.

    Defined separately from ordinary stop.
    Not all platforms implement this.
    """

    def trigger(self, reason: str) -> bool:
        """Trigger emergency stop. Returns True if successfully triggered."""
        ...

    def is_triggered(self) -> bool:
        """Check if emergency stop is active."""
        ...

    def reset(self) -> bool:
        """Reset emergency stop. Must require explicit operator action."""
        ...

    @property
    def supported(self) -> bool:
        """Whether this platform supports hardware emergency stop."""
        ...
