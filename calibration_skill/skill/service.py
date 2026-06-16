"""Hardware-free M26-C skill service skeleton."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from calibration_skill.adapters.registry import AdapterRegistry
from calibration_skill.domain.calibration import ExecutionAuditRecord
from calibration_skill.domain.enums import (
    CAPABILITY_BODY_VELOCITY_TELEMETRY,
    CAPABILITY_COMMAND_ACKNOWLEDGEMENT,
    CAPABILITY_DRY_RUN,
    CAPABILITY_EXPLICIT_STOP,
    CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND,
    CAPABILITY_LOCOMOTION_MODE_TRANSITION,
    CAPABILITY_STATE_STREAM,
    CommandDisposition,
    RobotPlatform,
    SkillOperationStatus,
)
from calibration_skill.domain.errors import (
    DomainError,
    ERROR_COMMAND_EXPIRED,
    ERROR_CONFIGURATION_INVALID,
    ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
    ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
    ERROR_SCHEMA_VERSION_UNSUPPORTED,
    ERROR_UNSUPPORTED_PLATFORM,
)
from calibration_skill.domain.motion import CommandReceipt
from calibration_skill.ports.factory import ConnectionConfig
from calibration_skill.schemas.codec import (
    canonical_json_dumps,
    decode_operator_authorization,
    decode_safety_envelope,
    decode_velocity_command,
    encode_command_receipt,
    encode_execution_audit_record,
    encode_preflight_report,
    encode_safety_envelope,
    encode_telemetry_sample,
    encode_velocity_command,
)
from calibration_skill.schemas.registry import CURRENT_SCHEMA_VERSION
from calibration_skill.schemas.validation import validate_skill_request, validate_skill_response
from calibration_skill.skill.envelopes import SkillRequestEnvelope, response_envelope
from calibration_skill.skill.operations import (
    COMMAND_OPERATIONS,
    OP_DRY_RUN_COLLECT_TELEMETRY,
    OP_DRY_RUN_END_TO_END,
    OP_DRY_RUN_STOP,
    OP_DRY_RUN_VELOCITY_COMMAND,
    OP_PREFLIGHT,
    SUPPORTED_OPERATIONS,
)

REQUIRED_DRY_RUN_CAPABILITIES = (
    CAPABILITY_DRY_RUN,
    CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND,
    CAPABILITY_COMMAND_ACKNOWLEDGEMENT,
)


@dataclass
class SkillService:
    """Deterministic service layer for M26-C mock dry-run operations."""
    registry: AdapterRegistry
    software_version: str = "m26c.skill.1"
    audit_records: list[dict[str, Any]] = field(default_factory=list)

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = str(request.get("request_id", ""))
        operation = str(request.get("operation", ""))
        try:
            validation = validate_skill_request(request)
            if not validation.get("valid"):
                return self._reject(request_id, operation, DomainError(
                    code=ERROR_CONFIGURATION_INVALID,
                    message="Skill request schema validation failed",
                    retryable=False,
                    details=validation,
                ))
            envelope = SkillRequestEnvelope.from_dict(request)
            gate_error = self._validate_envelope_gate(envelope)
            if gate_error is not None:
                return self._reject(envelope.request_id, envelope.operation, gate_error)
            if envelope.operation == OP_PREFLIGHT:
                response = self._preflight(envelope)
            elif envelope.operation == OP_DRY_RUN_VELOCITY_COMMAND:
                response = self._velocity_command(envelope)
            elif envelope.operation == OP_DRY_RUN_COLLECT_TELEMETRY:
                response = self._collect_telemetry(envelope)
            elif envelope.operation == OP_DRY_RUN_STOP:
                response = self._stop(envelope)
            elif envelope.operation == OP_DRY_RUN_END_TO_END:
                response = self._end_to_end(envelope)
            else:
                response = self._reject(envelope.request_id, envelope.operation, DomainError(
                    code=ERROR_CONFIGURATION_INVALID,
                    message=f"Unsupported M26-C operation: {envelope.operation}",
                    retryable=False,
                ))
            response_validation = validate_skill_response(response)
            if not response_validation.get("valid"):
                return self._fail(envelope.request_id, envelope.operation, DomainError(
                    code=ERROR_CONFIGURATION_INVALID,
                    message="Generated response failed schema validation",
                    retryable=False,
                    details=response_validation,
                ))
            return response
        except Exception as exc:
            return self._fail(request_id, operation, DomainError(
                code=ERROR_CONFIGURATION_INVALID,
                message=str(exc),
                retryable=False,
                cause_type=type(exc).__name__,
            ))

    def _validate_envelope_gate(self, envelope: SkillRequestEnvelope) -> DomainError | None:
        if envelope.schema_version != CURRENT_SCHEMA_VERSION:
            return DomainError(ERROR_SCHEMA_VERSION_UNSUPPORTED, "Unsupported schema_version", retryable=False)
        if not envelope.request_id.strip():
            return DomainError(ERROR_CONFIGURATION_INVALID, "request_id is required", retryable=False)
        if envelope.operation not in SUPPORTED_OPERATIONS:
            return DomainError(ERROR_CONFIGURATION_INVALID, f"Unknown operation {envelope.operation}", retryable=False)
        if not envelope.dry_run:
            return DomainError(ERROR_UNSUPPORTED_PLATFORM, "M26-C operations require dry_run=true", retryable=False)
        if envelope.platform != RobotPlatform.MOCK:
            return DomainError(ERROR_UNSUPPORTED_PLATFORM, "M26-C supports only mock platform", retryable=False)
        if envelope.operation in COMMAND_OPERATIONS and "safety_envelope" not in envelope.payload:
            return DomainError(ERROR_CONFIGURATION_INVALID, "safety_envelope is required for command operations", retryable=False)
        return None

    def _connection_config(self, envelope: SkillRequestEnvelope) -> ConnectionConfig:
        return ConnectionConfig(
            platform=envelope.platform,
            robot_id=envelope.robot_id or envelope.payload.get("robot_id") or "mock-robot",
            timeout_s=float(envelope.payload.get("timeout_s", 10.0)),
            extra=envelope.payload.get("connection_extra", {}),
        )

    def _create_adapter(self, envelope: SkillRequestEnvelope, required: tuple[str, ...] = ()):
        config = self._connection_config(envelope)
        errors = self.registry.validate_request(envelope.platform, config, dry_run=envelope.dry_run, required_capabilities=required)
        if errors:
            raise ValueError(errors[0].message)
        return self.registry.create_adapter(envelope.platform, config, dry_run=envelope.dry_run, required_capabilities=required)

    def _preflight(self, envelope: SkillRequestEnvelope) -> dict[str, Any]:
        adapter = self._create_adapter(envelope, (CAPABILITY_DRY_RUN,))
        adapter.connect()
        report = adapter.preflight()
        adapter.restore_safe_state()
        status = SkillOperationStatus.SUCCESS if report.is_ready else SkillOperationStatus.REJECTED
        error = None if report.is_ready else DomainError(ERROR_CONFIGURATION_INVALID, "Preflight contains blockers", retryable=False)
        return response_envelope(
            envelope.request_id,
            envelope.operation,
            status,
            result={"preflight_report": encode_preflight_report(report)},
            error=error,
            warnings=tuple(c.detail for c in report.warnings),
        )

    def _velocity_command(self, envelope: SkillRequestEnvelope) -> dict[str, Any]:
        adapter = self._create_adapter(envelope, REQUIRED_DRY_RUN_CAPABILITIES)
        adapter.connect()
        adapter.enter_locomotion_ready()
        safety = decode_safety_envelope(envelope.payload["safety_envelope"])
        command = decode_velocity_command(envelope.payload["velocity_command"])
        authorization = self._decode_authorization(envelope)
        self._validate_authorization_for_service(safety, authorization, envelope.operation, adapter.identity.robot_id, adapter.clock.now_ns())
        adapter.configure_command_context(safety, authorization, envelope.operation)
        receipt = adapter.send_velocity_command(command)
        stop_receipt = adapter.stop()
        adapter.restore_safe_state()
        audit = self._audit(envelope, adapter, safety, authorization, command, receipt, None, "stop_then_restore", ())
        status = SkillOperationStatus.SUCCESS if receipt.disposition == CommandDisposition.ACCEPTED else SkillOperationStatus.REJECTED
        return response_envelope(
            envelope.request_id,
            envelope.operation,
            status,
            result={
                "receipt": encode_command_receipt(receipt),
                "stop_receipt": encode_command_receipt(stop_receipt),
                "audit_record": audit,
            },
            error=receipt.rejection_error,
            audit_reference=audit["session_id"],
        )

    def _collect_telemetry(self, envelope: SkillRequestEnvelope) -> dict[str, Any]:
        adapter = self._create_adapter(envelope, (CAPABILITY_DRY_RUN, CAPABILITY_BODY_VELOCITY_TELEMETRY))
        adapter.connect()
        sample = adapter.collect_telemetry_sample()
        adapter.restore_safe_state()
        return response_envelope(
            envelope.request_id,
            envelope.operation,
            SkillOperationStatus.SUCCESS,
            result={"telemetry_sample": encode_telemetry_sample(sample)},
        )

    def _stop(self, envelope: SkillRequestEnvelope) -> dict[str, Any]:
        adapter = self._create_adapter(envelope, (CAPABILITY_DRY_RUN, CAPABILITY_EXPLICIT_STOP))
        adapter.connect()
        receipt = adapter.stop()
        adapter.restore_safe_state()
        status = SkillOperationStatus.SUCCESS if receipt.disposition == CommandDisposition.ACCEPTED else SkillOperationStatus.REJECTED
        return response_envelope(
            envelope.request_id,
            envelope.operation,
            status,
            result={"receipt": encode_command_receipt(receipt)},
            error=receipt.rejection_error,
        )

    def _end_to_end(self, envelope: SkillRequestEnvelope) -> dict[str, Any]:
        adapter = self._create_adapter(envelope, (
            CAPABILITY_DRY_RUN,
            CAPABILITY_HIGH_LEVEL_BODY_VELOCITY_COMMAND,
            CAPABILITY_BODY_VELOCITY_TELEMETRY,
            CAPABILITY_EXPLICIT_STOP,
            CAPABILITY_LOCOMOTION_MODE_TRANSITION,
            CAPABILITY_STATE_STREAM,
        ))
        safety = decode_safety_envelope(envelope.payload["safety_envelope"])
        command = decode_velocity_command(envelope.payload["velocity_command"])
        authorization = self._decode_authorization(envelope)
        receipt: CommandReceipt | None = None
        telemetry = None
        errors: list[str] = []
        cleanup = "not_started"
        try:
            adapter.connect()
            adapter.configure_command_context(safety, authorization, envelope.operation)
            preflight = adapter.preflight()
            if not preflight.is_ready:
                raise ValueError("preflight blocked dry-run end-to-end")
            adapter.enter_locomotion_ready()
            self._validate_authorization_for_service(safety, authorization, envelope.operation, adapter.identity.robot_id, adapter.clock.now_ns())
            receipt = adapter.send_velocity_command(command)
            if receipt.rejection_error is not None:
                raise ValueError(receipt.rejection_error.message)
            telemetry = adapter.collect_telemetry_sample()
            stop_receipt = adapter.stop()
            cleanup = "stop_then_restore"
            adapter.restore_safe_state()
            audit = self._audit(envelope, adapter, safety, authorization, command, receipt, telemetry, cleanup, tuple(errors))
            return response_envelope(
                envelope.request_id,
                envelope.operation,
                SkillOperationStatus.SUCCESS,
                result={
                    "receipt": encode_command_receipt(receipt),
                    "telemetry_sample": encode_telemetry_sample(telemetry),
                    "stop_receipt": encode_command_receipt(stop_receipt),
                    "audit_record": audit,
                },
                audit_reference=audit["session_id"],
            )
        except Exception as exc:
            errors.append(str(exc))
            try:
                stop_receipt = adapter.stop()
                cleanup = "stop_attempted_then_restore"
            except Exception as stop_exc:
                stop_receipt = None
                cleanup = f"stop_failed:{type(stop_exc).__name__}"
            adapter.restore_safe_state()
            audit = self._audit(envelope, adapter, safety, authorization, command, receipt, telemetry, cleanup, tuple(errors))
            result: dict[str, Any] = {"audit_record": audit}
            if receipt is not None:
                result["receipt"] = encode_command_receipt(receipt)
            if stop_receipt is not None:
                result["stop_receipt"] = encode_command_receipt(stop_receipt)
            return response_envelope(
                envelope.request_id,
                envelope.operation,
                SkillOperationStatus.REJECTED,
                result=result,
                error=receipt.rejection_error if receipt and receipt.rejection_error else DomainError(
                    ERROR_CONFIGURATION_INVALID,
                    str(exc),
                    retryable=False,
                ),
                audit_reference=audit["session_id"],
            )

    def _decode_authorization(self, envelope: SkillRequestEnvelope):
        data = envelope.payload.get("operator_authorization")
        return decode_operator_authorization(data) if data else None

    def _validate_authorization_for_service(self, safety, authorization, operation: str, robot_id: str, now_ns: int) -> None:
        if not safety.operator_authorization_required:
            return
        if authorization is None:
            raise ValueError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED)
        errors = authorization.validate(now_ns)
        if errors:
            raise ValueError(ERROR_OPERATOR_AUTHORIZATION_EXPIRED)
        if not authorization.matches_platform(RobotPlatform.MOCK, robot_id):
            raise ValueError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED)
        if not authorization.check_operation(operation):
            raise ValueError(ERROR_OPERATOR_AUTHORIZATION_REQUIRED)

    def _audit(
        self,
        envelope: SkillRequestEnvelope,
        adapter,
        safety,
        authorization,
        command,
        receipt,
        telemetry,
        cleanup_result: str,
        errors: tuple[str, ...],
    ) -> dict[str, Any]:
        started_ns = command.issued_monotonic_ns if command is not None else adapter.clock.now_ns()
        completed_ns = adapter.clock.now_ns()
        audit = ExecutionAuditRecord(
            session_id=f"audit-{envelope.request_id}",
            requested_operation=envelope.operation,
            platform=RobotPlatform.MOCK,
            robot_id=adapter.identity.robot_id,
            software_version=self.software_version,
            adapter_version=adapter.identity.adapter_version,
            safety_policy_id=safety.policy_id,
            safety_policy_hash=safety.policy_hash,
            authorization_id=authorization.authorization_id if authorization else "none",
            started_monotonic_ns=started_ns,
            completed_monotonic_ns=completed_ns,
            requested_command=encode_velocity_command(command) if command else None,
            validated_command=encode_velocity_command(command) if command and not errors else None,
            receipt=encode_command_receipt(receipt) if receipt else None,
            telemetry_evidence=encode_telemetry_sample(telemetry) if telemetry else None,
            cleanup_result=cleanup_result,
            errors=errors,
            provenance_hashes={"canonical_request_sha256": hashlib.sha256(canonical_json_dumps(envelope.payload).encode("utf-8")).hexdigest()},
            session_status="success" if not errors else "rejected",
        )
        audit_dict = encode_execution_audit_record(audit)
        audit_dict["hardware_evidence_claimed"] = False
        audit_dict["audit_digest"] = hashlib.sha256(canonical_json_dumps(audit_dict).encode("utf-8")).hexdigest()
        self.audit_records.append(audit_dict)
        return audit_dict

    def _reject(self, request_id: str, operation: str, error: DomainError) -> dict[str, Any]:
        return response_envelope(request_id or "unknown", operation or "unknown", SkillOperationStatus.REJECTED, error=error)

    def _fail(self, request_id: str, operation: str, error: DomainError) -> dict[str, Any]:
        return response_envelope(request_id or "unknown", operation or "unknown", SkillOperationStatus.FAILED, error=error)
