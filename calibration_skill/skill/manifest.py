"""Stable skill manifest for agent-callable M26-D dry-run invocation."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from calibration_skill.domain.errors import (
    ERROR_COMMAND_EXPIRED,
    ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
    ERROR_CONFIGURATION_INVALID,
    ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
    ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
    ERROR_SCHEMA_VERSION_UNSUPPORTED,
    ERROR_UNSUPPORTED_PLATFORM,
    ERROR_WRONG_MOTION_STATE,
)
from calibration_skill.schemas.registry import CURRENT_SCHEMA_VERSION
from calibration_skill.skill.operations import (
    OP_DRY_RUN_COLLECT_TELEMETRY,
    OP_DRY_RUN_END_TO_END,
    OP_DRY_RUN_STOP,
    OP_DRY_RUN_VELOCITY_COMMAND,
    OP_PREFLIGHT,
)

SKILL_NAME = "calibration_skill"
SKILL_VERSION = "0.1.0-m26d"

EXIT_CODES: dict[str, int] = {
    "success": 0,
    "request_rejected": 1,
    "usage_error": 2,
    "malformed_input_json": 3,
    "output_write_failure": 4,
    "internal_error": 5,
    "hermeticity_or_forbidden_runtime_violation": 6,
}


def build_skill_manifest() -> dict[str, Any]:
    """Return a deterministic machine-readable skill manifest."""
    operations = operation_catalog()
    return {
        "skill_name": SKILL_NAME,
        "skill_version": SKILL_VERSION,
        "contract_version": CURRENT_SCHEMA_VERSION,
        "dry_run_only": True,
        "hardware_support": "not_supported",
        "input_schema_ids": ["urn:calibration-skill:schema:skill_request:v1"],
        "output_schema_ids": ["urn:calibration-skill:schema:skill_response:v1"],
        "supported_operations": [op["name"] for op in operations],
        "operations": operations,
        "platform_support": {
            "mock": {"status": "supported", "dry_run_only": True, "maturity": "bench_verified"},
            "booster_k1": {"status": "not_available_new_runtime", "dry_run_only": false_value(), "maturity": "legacy_existing"},
            "unitree_g1": {"status": "not_available", "dry_run_only": false_value(), "maturity": "scaffolded"},
            "unitree_go1": {"status": "not_available", "dry_run_only": false_value(), "maturity": "scaffolded"},
        },
        "safety_requirements": {
            "dry_run_required": True,
            "platform_must_be": "mock",
            "safety_envelope_required_for": [OP_DRY_RUN_VELOCITY_COMMAND, OP_DRY_RUN_END_TO_END],
            "operator_authorization_required_when_safety_envelope_requires_it": True,
        },
        "examples": {
            OP_PREFLIGHT: "examples/calibration_skill/preflight_request.mock.json",
            OP_DRY_RUN_VELOCITY_COMMAND: "examples/calibration_skill/dry_run_velocity_command.mock.json",
            OP_DRY_RUN_COLLECT_TELEMETRY: "examples/calibration_skill/dry_run_collect_telemetry.mock.json",
            OP_DRY_RUN_STOP: "examples/calibration_skill/dry_run_stop.mock.json",
            OP_DRY_RUN_END_TO_END: "examples/calibration_skill/dry_run_end_to_end.mock.json",
            "invalid_real_platform": "examples/calibration_skill/invalid_real_platform_request.json",
            "invalid_dry_run_false": "examples/calibration_skill/invalid_dry_run_false_request.json",
            "invalid_missing_safety": "examples/calibration_skill/invalid_missing_safety_request.json",
        },
        "error_codes": [
            ERROR_CONFIGURATION_INVALID,
            ERROR_UNSUPPORTED_PLATFORM,
            ERROR_SCHEMA_VERSION_UNSUPPORTED,
            ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
            ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
            ERROR_COMMAND_EXPIRED,
            ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
            ERROR_WRONG_MOTION_STATE,
        ],
        "exit_codes": EXIT_CODES,
        "readiness_status": {
            "agent_cli": "bench_verified",
            "json_io_contract": "bench_verified",
            "hardware_verification": "not_started",
            "release": "not_started",
        },
        "non_goals": [
            "No K1 migration in M26-D.",
            "No G1 or GO1 runtime support.",
            "No hardware connection, DDS, UDP, socket, or vendor SDK runtime.",
            "No physical motion operation.",
        ],
    }


def operation_catalog() -> list[dict[str, Any]]:
    """Return the M26-D operation catalog."""
    return deepcopy([
        {
            "name": OP_PREFLIGHT,
            "description": "Run mock dry-run preflight checks.",
            "required_request_payload_fields": [],
            "required_capabilities": ["dry_run"],
            "dry_run_required": True,
            "adapter_requirement": "mock",
            "expected_response_result_fields": ["preflight_report"],
            "possible_error_codes": [ERROR_CONFIGURATION_INVALID, ERROR_UNSUPPORTED_PLATFORM],
            "cleanup_behavior": "restore_safe_state",
            "audit_behavior": "no execution audit record",
            "hardware_motion_possible": False,
        },
        {
            "name": OP_DRY_RUN_VELOCITY_COMMAND,
            "description": "Validate and dispatch a mock velocity command.",
            "required_request_payload_fields": ["safety_envelope", "velocity_command", "operator_authorization_when_required"],
            "required_capabilities": ["dry_run", "high_level_body_velocity_command", "command_acknowledgement"],
            "dry_run_required": True,
            "adapter_requirement": "mock",
            "expected_response_result_fields": ["receipt", "stop_receipt", "audit_record"],
            "possible_error_codes": [
                ERROR_CONFIGURATION_INVALID,
                ERROR_COMMAND_EXPIRED,
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
                ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
            ],
            "cleanup_behavior": "stop_then_restore",
            "audit_behavior": "in_memory_execution_audit_record",
            "hardware_motion_possible": False,
        },
        {
            "name": OP_DRY_RUN_COLLECT_TELEMETRY,
            "description": "Collect deterministic mock telemetry.",
            "required_request_payload_fields": [],
            "required_capabilities": ["dry_run", "body_velocity_telemetry"],
            "dry_run_required": True,
            "adapter_requirement": "mock",
            "expected_response_result_fields": ["telemetry_sample"],
            "possible_error_codes": [ERROR_CONFIGURATION_INVALID, ERROR_UNSUPPORTED_PLATFORM],
            "cleanup_behavior": "restore_safe_state",
            "audit_behavior": "no execution audit record",
            "hardware_motion_possible": False,
        },
        {
            "name": OP_DRY_RUN_STOP,
            "description": "Issue a mock stop command.",
            "required_request_payload_fields": [],
            "required_capabilities": ["dry_run", "explicit_stop"],
            "dry_run_required": True,
            "adapter_requirement": "mock",
            "expected_response_result_fields": ["receipt"],
            "possible_error_codes": [ERROR_CONFIGURATION_INVALID, ERROR_UNSUPPORTED_PLATFORM],
            "cleanup_behavior": "restore_safe_state",
            "audit_behavior": "no execution audit record",
            "hardware_motion_possible": False,
        },
        {
            "name": OP_DRY_RUN_END_TO_END,
            "description": "Run the full mock dry-run flow with audit generation.",
            "required_request_payload_fields": ["safety_envelope", "velocity_command", "operator_authorization_when_required"],
            "required_capabilities": [
                "dry_run",
                "high_level_body_velocity_command",
                "body_velocity_telemetry",
                "explicit_stop",
                "locomotion_mode_transition",
                "state_stream",
            ],
            "dry_run_required": True,
            "adapter_requirement": "mock",
            "expected_response_result_fields": ["receipt", "telemetry_sample", "stop_receipt", "audit_record"],
            "possible_error_codes": [
                ERROR_CONFIGURATION_INVALID,
                ERROR_COMMAND_EXPIRED,
                ERROR_COMMAND_OUTSIDE_SAFETY_ENVELOPE,
                ERROR_OPERATOR_AUTHORIZATION_REQUIRED,
                ERROR_OPERATOR_AUTHORIZATION_EXPIRED,
            ],
            "cleanup_behavior": "stop_attempted_then_restore_on_failure",
            "audit_behavior": "in_memory_execution_audit_record",
            "hardware_motion_possible": False,
        },
    ])


def false_value() -> bool:
    """Readable false literal for manifest tables."""
    return False
