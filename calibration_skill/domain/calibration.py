"""Calibration domain contracts: trial plans, results, datasets, models, profiles."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.domain.enums import (
    CompensationAction,
    CoordinateFrame,
    ProfileStatus,
    RobotPlatform,
    SkillOperationStatus,
    TrialStatus,
)
from calibration_skill.domain.errors import DomainError, validation_error


def _canonical_json(obj: Any) -> bytes:
    """Produce canonical JSON bytes for hashing (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _content_digest(obj: dict[str, Any]) -> str:
    """Compute a SHA-256 content digest of a dictionary."""
    return hashlib.sha256(_canonical_json(obj)).hexdigest()


@dataclass(frozen=True)
class EnvironmentDescriptor:
    """Describes the environment for a calibration session."""
    surface_type: str
    condition: str = "unknown"
    slope: str = "unknown"
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.surface_type or not self.surface_type.strip():
            raise ValueError("surface_type must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_type": self.surface_type,
            "condition": self.condition,
            "slope": self.slope,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TrialPlan:
    """A plan for calibration trials.

    Explicitly identifies platform, target commands, repetitions,
    required capabilities, safety policy, and environment.
    """
    plan_id: str
    platform: RobotPlatform
    robot_id: str
    target_commands: tuple[Any, ...]  # VelocityCommand objects
    repetitions: int
    required_capabilities: tuple[str, ...]
    safety_policy_id: str
    safety_policy_hash: str
    environment: EnvironmentDescriptor
    operator_authorization_required: bool = True
    timing: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must be non-empty")
        if not self.robot_id or not self.robot_id.strip():
            raise ValueError("robot_id must be non-empty")
        if self.repetitions <= 0:
            raise ValueError(f"repetitions must be positive, got {self.repetitions}")
        if not self.target_commands:
            raise ValueError("target_commands must not be empty")

    @property
    def total_trials(self) -> int:
        return len(self.target_commands) * self.repetitions

    def to_dict(self) -> dict[str, Any]:
        from calibration_skill.domain.motion import VelocityCommand
        return {
            "plan_id": self.plan_id,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "command_count": len(self.target_commands),
            "repetitions": self.repetitions,
            "total_trials": self.total_trials,
            "required_capabilities": list(self.required_capabilities),
            "safety_policy_id": self.safety_policy_id,
            "safety_policy_hash": self.safety_policy_hash,
            "environment": self.environment.to_dict(),
            "operator_authorization_required": self.operator_authorization_required,
            "timing": self.timing,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TrialResult:
    """Result of a single calibration trial.

    Distinguishes between planned, attempted, accepted, executed, valid, aborted, and failed.
    Does not infer execution solely from process return code zero.
    """
    trial_id: str
    plan_id: str
    command_sequence_id: str
    status: TrialStatus
    platform: RobotPlatform
    robot_id: str
    started_monotonic_ns: int | None = None
    completed_monotonic_ns: int | None = None
    command_accepted: bool = False
    telemetry_valid: bool = False
    abort_reason: str | None = None
    failure_reason: str | None = None
    quality_metrics: dict[str, float] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.trial_id or not self.trial_id.strip():
            raise ValueError("trial_id must be non-empty")
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "trial_id": self.trial_id,
            "plan_id": self.plan_id,
            "command_sequence_id": self.command_sequence_id,
            "status": self.status.value,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "command_accepted": self.command_accepted,
            "telemetry_valid": self.telemetry_valid,
        }
        if self.started_monotonic_ns is not None:
            result["started_monotonic_ns"] = self.started_monotonic_ns
        if self.completed_monotonic_ns is not None:
            result["completed_monotonic_ns"] = self.completed_monotonic_ns
        if self.abort_reason is not None:
            result["abort_reason"] = self.abort_reason
        if self.failure_reason is not None:
            result["failure_reason"] = self.failure_reason
        if self.quality_metrics:
            result["quality_metrics"] = self.quality_metrics
        if self.notes:
            result["notes"] = self.notes
        return result


@dataclass(frozen=True)
class CalibrationDataset:
    """A dataset of calibration trials with provenance."""
    dataset_id: str
    schema_version: str
    platform: RobotPlatform
    robot_id: str
    environment: EnvironmentDescriptor
    trial_ids: tuple[str, ...]
    data_quality_summary: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, str] = field(default_factory=dict)
    _content_digest: str = ""

    def __post_init__(self) -> None:
        if not self.dataset_id or not self.dataset_id.strip():
            raise ValueError("dataset_id must be non-empty")
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must be non-empty")

    @property
    def content_digest(self) -> str:
        """Immutable content digest. Computed once at construction."""
        if not self._content_digest:
            object.__setattr__(self, "_content_digest", _content_digest(self.to_dict()))
        return self._content_digest

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "schema_version": self.schema_version,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "environment": self.environment.to_dict(),
            "trial_count": len(self.trial_ids),
            "trial_ids": list(self.trial_ids),
            "data_quality_summary": self.data_quality_summary,
            "provenance": self.provenance,
            "content_digest": self.content_digest,
        }


@dataclass(frozen=True)
class CalibrationModel:
    """A calibration model descriptor. Does not implement fitting."""
    model_id: str
    platform: RobotPlatform
    model_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    training_dataset_digest: str = ""
    validation_metrics: dict[str, float] = field(default_factory=dict)
    domain_min_mps: float = 0.0
    domain_max_mps: float = 0.0

    def __post_init__(self) -> None:
        if not self.model_id or not self.model_id.strip():
            raise ValueError("model_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "platform": self.platform.value,
            "model_type": self.model_type,
            "parameters": self.parameters,
            "training_dataset_digest": self.training_dataset_digest,
            "validation_metrics": self.validation_metrics,
            "domain_min_mps": self.domain_min_mps,
            "domain_max_mps": self.domain_max_mps,
        }


@dataclass(frozen=True)
class CalibrationProfile:
    """A calibration profile with full provenance."""
    profile_id: str
    profile_version: str
    platform: RobotPlatform
    robot_id: str
    environment_applicability: EnvironmentDescriptor
    model: CalibrationModel
    training_dataset_digest: str
    validation_evidence: dict[str, Any] = field(default_factory=dict)
    safety_policy_compatibility: tuple[str, ...] = field(default_factory=tuple)
    creation_provenance: dict[str, str] = field(default_factory=dict)
    status: ProfileStatus = ProfileStatus.CANDIDATE
    _content_digest: str = ""

    def __post_init__(self) -> None:
        if not self.profile_id or not self.profile_id.strip():
            raise ValueError("profile_id must be non-empty")
        if not self.profile_version or not self.profile_version.strip():
            raise ValueError("profile_version must be non-empty")

    @property
    def content_digest(self) -> str:
        """Immutable content digest."""
        if not self._content_digest:
            object.__setattr__(self, "_content_digest", _content_digest(self.to_dict()))
        return self._content_digest

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "environment_applicability": self.environment_applicability.to_dict(),
            "model": self.model.to_dict(),
            "training_dataset_digest": self.training_dataset_digest,
            "validation_evidence": self.validation_evidence,
            "safety_policy_compatibility": list(self.safety_policy_compatibility),
            "creation_provenance": self.creation_provenance,
            "status": self.status.value,
            "content_digest": self.content_digest,
        }


@dataclass(frozen=True)
class CompensationDecision:
    """Compensation decision for a desired velocity.

    Distinguishes between apply_compensation, identity_fallback, reject, and unavailable.
    Includes machine-readable reasons.
    """
    desired_actual_mps: float
    action: CompensationAction
    compensated_command_mps: float | None = None
    model_id: str | None = None
    profile_id: str | None = None
    confidence: float | None = None
    risk_level: str | None = None
    fallback_reason: str | None = None
    decision_monotonic_ns: int = 0
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        import math
        if math.isnan(self.desired_actual_mps) or math.isinf(self.desired_actual_mps):
            raise ValueError("desired_actual_mps must be finite")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "desired_actual_mps": self.desired_actual_mps,
            "action": self.action.value,
            "reasons": list(self.reasons),
        }
        if self.compensated_command_mps is not None:
            result["compensated_command_mps"] = self.compensated_command_mps
        if self.model_id is not None:
            result["model_id"] = self.model_id
        if self.profile_id is not None:
            result["profile_id"] = self.profile_id
        if self.confidence is not None:
            result["confidence"] = self.confidence
        if self.risk_level is not None:
            result["risk_level"] = self.risk_level
        if self.fallback_reason is not None:
            result["fallback_reason"] = self.fallback_reason
        result["decision_monotonic_ns"] = self.decision_monotonic_ns
        return result


@dataclass(frozen=True)
class ExecutionAuditRecord:
    """Full execution audit record with enough information to reconstruct the operation."""
    session_id: str
    requested_operation: str
    platform: RobotPlatform
    robot_id: str
    software_version: str
    adapter_version: str
    safety_policy_id: str
    safety_policy_hash: str
    authorization_id: str
    started_monotonic_ns: int
    completed_monotonic_ns: int | None = None
    requested_command: dict[str, Any] | None = None
    validated_command: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None
    telemetry_evidence: dict[str, Any] | None = None
    cleanup_result: str | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)
    provenance_hashes: dict[str, str] = field(default_factory=dict)
    session_status: str = "unknown"

    def __post_init__(self) -> None:
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "session_id": self.session_id,
            "requested_operation": self.requested_operation,
            "platform": self.platform.value,
            "robot_id": self.robot_id,
            "software_version": self.software_version,
            "adapter_version": self.adapter_version,
            "safety_policy_id": self.safety_policy_id,
            "safety_policy_hash": self.safety_policy_hash,
            "authorization_id": self.authorization_id,
            "started_monotonic_ns": self.started_monotonic_ns,
            "session_status": self.session_status,
        }
        if self.completed_monotonic_ns is not None:
            result["completed_monotonic_ns"] = self.completed_monotonic_ns
        if self.requested_command is not None:
            result["requested_command"] = self.requested_command
        if self.validated_command is not None:
            result["validated_command"] = self.validated_command
        if self.receipt is not None:
            result["receipt"] = self.receipt
        if self.telemetry_evidence is not None:
            result["telemetry_evidence"] = self.telemetry_evidence
        if self.cleanup_result is not None:
            result["cleanup_result"] = self.cleanup_result
        if self.errors:
            result["errors"] = list(self.errors)
        if self.provenance_hashes:
            result["provenance_hashes"] = self.provenance_hashes
        return result
