"""Implementation readiness model for the calibration skill."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import ImplementationMaturity


@dataclass(frozen=True)
class ReadinessEntry:
    """A single readiness entry."""
    key: str
    maturity: ImplementationMaturity
    description: str
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "key": self.key,
            "maturity": self.maturity.value,
            "description": self.description,
        }
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass(frozen=True)
class ReadinessModel:
    """Full readiness model for the calibration skill.

    Tracks implementation maturity of all major components.
    """
    entries: tuple[ReadinessEntry, ...] = field(default_factory=tuple)

    def get(self, key: str) -> ReadinessEntry | None:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self.entries],
        }


# Standard readiness keys
READINESS_DOMAIN_CONTRACTS = "domain_contracts"
READINESS_PORT_INTERFACES = "port_interfaces"
READINESS_VERSIONED_SCHEMAS = "versioned_schemas"
READINESS_DETERMINISTIC_CODECS = "deterministic_codecs"
READINESS_ARCHITECTURE_ENFORCEMENT = "architecture_enforcement"
READINESS_MOCK_ADAPTER = "mock_adapter"
READINESS_K1_ADAPTER_MIGRATION = "k1_adapter_migration"
READINESS_G1_ADAPTER = "g1_adapter"
READINESS_GO1_ADAPTER = "go1_adapter"
READINESS_UNIFIED_SKILL_RUNTIME = "unified_skill_runtime"
READINESS_HARDWARE_VERIFICATION = "hardware_verification"
READINESS_RELEASE = "release"

ALL_READINESS_KEYS: tuple[str, ...] = (
    READINESS_DOMAIN_CONTRACTS,
    READINESS_PORT_INTERFACES,
    READINESS_VERSIONED_SCHEMAS,
    READINESS_DETERMINISTIC_CODECS,
    READINESS_ARCHITECTURE_ENFORCEMENT,
    READINESS_MOCK_ADAPTER,
    READINESS_K1_ADAPTER_MIGRATION,
    READINESS_G1_ADAPTER,
    READINESS_GO1_ADAPTER,
    READINESS_UNIFIED_SKILL_RUNTIME,
    READINESS_HARDWARE_VERIFICATION,
    READINESS_RELEASE,
)
