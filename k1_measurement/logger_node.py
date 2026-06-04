"""Logger node skeleton for K1 measurement.

TODO: Implement ROS2 subscriptions only after topic names and message types are verified.
"""

from __future__ import annotations


class LoggerNodePlaceholder:
    """Placeholder that records intended logger configuration without ROS2 side effects."""

    def __init__(self, topics: dict[str, str] | None = None) -> None:
        self.topics = topics or {}

    def verified_topics(self) -> bool:
        return bool(self.topics) and all(
            value != "TO_BE_FILLED_AFTER_ROS2_TOPIC_LIST" for value in self.topics.values()
        )
