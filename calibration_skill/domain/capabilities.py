"""Capability descriptor and negotiation for platform capabilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import (
    ALL_KNOWN_CAPABILITIES,
    CapabilitySupport,
    EvidenceLevel,
    ImplementationMaturity,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_CAPABILITY_UNAVAILABLE,
    ERROR_CAPABILITY_UNVERIFIED,
    validation_error,
)


@dataclass(frozen=True)
class CapabilityRecord:
    """A single capability record for a platform.

    Unknown must remain distinct from unsupported.
    A capability marked 'supported' does not automatically imply 'hardware_verified'.
    """
    capability_id: str
    support: CapabilitySupport = CapabilitySupport.UNKNOWN
    evidence: EvidenceLevel = EvidenceLevel.NONE
    maturity: ImplementationMaturity = ImplementationMaturity.NOT_STARTED
    constraints: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.capability_id or not self.capability_id.strip():
            raise ValueError("capability_id must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "capability_id": self.capability_id,
            "support": self.support.value,
            "evidence": self.evidence.value,
            "maturity": self.maturity.value,
        }
        if self.constraints is not None:
            result["constraints"] = self.constraints
        if self.evidence_refs:
            result["evidence_refs"] = list(self.evidence_refs)
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass(frozen=True)
class CapabilityDescriptor:
    """Describes the capabilities of a specific platform.

    Capabilities are represented explicitly and individually.
    """
    platform_id: str
    capabilities: tuple[CapabilityRecord, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.platform_id or not self.platform_id.strip():
            raise ValueError("platform_id must be a non-empty string")

    def get_capability(self, capability_id: str) -> CapabilityRecord | None:
        """Get a specific capability record by ID."""
        for cap in self.capabilities:
            if cap.capability_id == capability_id:
                return cap
        return None

    def has_capability(self, capability_id: str) -> bool:
        """Check if a capability is explicitly supported."""
        cap = self.get_capability(capability_id)
        return cap is not None and cap.support == CapabilitySupport.SUPPORTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "capabilities": [c.to_dict() for c in self.capabilities],
        }


@dataclass(frozen=True)
class CapabilityNegotiationResult:
    """Result of capability negotiation.

    Produced by negotiate_capabilities() — a pure function with no I/O.
    """
    satisfied: bool
    required_missing: tuple[str, ...] = field(default_factory=tuple)
    required_unknown: tuple[str, ...] = field(default_factory=tuple)
    requires_hardware_verification: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def errors(self) -> list[DomainError]:
        """Convert negotiation failures to domain errors."""
        result: list[DomainError] = []
        for cap_id in self.required_missing:
            result.append(DomainError(
                code=ERROR_CAPABILITY_UNAVAILABLE,
                message=f"Required capability '{cap_id}' is unavailable",
                retryable=False,
                details={"capability_id": cap_id},
            ))
        for cap_id in self.required_unknown:
            result.append(DomainError(
                code=ERROR_CAPABILITY_UNVERIFIED,
                message=f"Required capability '{cap_id}' status is unknown",
                retryable=False,
                details={"capability_id": cap_id},
            ))
        for cap_id in self.requires_hardware_verification:
            result.append(DomainError(
                code=ERROR_CAPABILITY_UNVERIFIED,
                message=f"Capability '{cap_id}' requires hardware verification",
                retryable=False,
                details={"capability_id": cap_id},
            ))
        return result


def negotiate_capabilities(
    descriptor: CapabilityDescriptor,
    required: tuple[str, ...],
) -> CapabilityNegotiationResult:
    """Pure function: check if a descriptor satisfies required capabilities.

    Does not perform I/O.
    Does not mutate the descriptor.
    """
    required_missing: list[str] = []
    required_unknown: list[str] = []
    requires_hw_verification: list[str] = []
    notes: list[str] = []

    for cap_id in required:
        record = descriptor.get_capability(cap_id)
        if record is None:
            required_missing.append(cap_id)
            continue

        if record.support == CapabilitySupport.UNSUPPORTED:
            required_missing.append(cap_id)
        elif record.support == CapabilitySupport.UNKNOWN:
            required_unknown.append(cap_id)
        elif record.support == CapabilitySupport.REQUIRES_HARDWARE_VERIFICATION:
            requires_hw_verification.append(cap_id)
        elif record.support == CapabilitySupport.SUPPORTED:
            pass  # OK
        else:
            required_unknown.append(cap_id)

    satisfied = (
        len(required_missing) == 0
        and len(required_unknown) == 0
        and len(requires_hw_verification) == 0
    )

    return CapabilityNegotiationResult(
        satisfied=satisfied,
        required_missing=tuple(required_missing),
        required_unknown=tuple(required_unknown),
        requires_hardware_verification=tuple(requires_hw_verification),
        notes=tuple(notes),
    )
