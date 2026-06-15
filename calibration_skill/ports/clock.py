"""Port interface for monotonic clocks."""
from __future__ import annotations

from typing import Protocol


class MonotonicClock(Protocol):
    """Abstract interface for monotonic time.

    Domain objects receive time values explicitly rather than
    calling the system clock directly.
    """

    def now_ns(self) -> int:
        """Return current monotonic time in nanoseconds.

        Must be monotonically increasing. Must not use system clock.
        """
        ...

    def elapsed_since_ns(self, timestamp_ns: int) -> int:
        """Return nanoseconds elapsed since the given timestamp."""
        ...

    def is_after_ns(self, timestamp_ns: int) -> bool:
        """Return True if current time is after the given timestamp."""
        ...
