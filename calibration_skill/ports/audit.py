"""Port interface for audit recording."""
from __future__ import annotations

from typing import Protocol

from calibration_skill.domain.calibration import ExecutionAuditRecord


class AuditSink(Protocol):
    """Abstract interface for append-only audit recording."""

    def record(self, record: ExecutionAuditRecord) -> None:
        """Append an audit record. Must be append-only."""
        ...

    def get(self, session_id: str) -> ExecutionAuditRecord | None:
        """Retrieve an audit record by session ID."""
        ...

    def list_sessions(self) -> list[str]:
        """List all recorded session IDs."""
        ...
