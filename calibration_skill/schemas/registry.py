"""Schema registry: versioned external schema management."""
from __future__ import annotations

from dataclasses import dataclass, field

SCHEMA_URN_PREFIX = "urn:calibration-skill:schema"
CURRENT_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class SchemaInfo:
    """Metadata for a versioned schema."""
    schema_id: str
    version: str
    urn: str
    path: str
    description: str = ""

    @property
    def full_urn(self) -> str:
        return f"{self.urn}:v{self.version.split('.')[0]}"


# Registry of all v1 schemas
SCHEMA_REGISTRY: dict[str, SchemaInfo] = {
    "skill_request": SchemaInfo(
        schema_id="skill_request",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:skill_request",
        path="schemas/v1/skill_request.schema.json",
        description="Agent-callable skill request envelope",
    ),
    "skill_response": SchemaInfo(
        schema_id="skill_response",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:skill_response",
        path="schemas/v1/skill_response.schema.json",
        description="Agent-callable skill response envelope",
    ),
    "error": SchemaInfo(
        schema_id="error",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:error",
        path="schemas/v1/error.schema.json",
        description="Structured error response",
    ),
    "robot_identity": SchemaInfo(
        schema_id="robot_identity",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:robot_identity",
        path="schemas/v1/robot_identity.schema.json",
        description="Robot identity descriptor",
    ),
    "capability_descriptor": SchemaInfo(
        schema_id="capability_descriptor",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:capability_descriptor",
        path="schemas/v1/capability_descriptor.schema.json",
        description="Platform capability descriptor",
    ),
    "velocity_command": SchemaInfo(
        schema_id="velocity_command",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:velocity_command",
        path="schemas/v1/velocity_command.schema.json",
        description="Velocity command",
    ),
    "command_receipt": SchemaInfo(
        schema_id="command_receipt",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:command_receipt",
        path="schemas/v1/command_receipt.schema.json",
        description="Command receipt",
    ),
    "telemetry_sample": SchemaInfo(
        schema_id="telemetry_sample",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:telemetry_sample",
        path="schemas/v1/telemetry_sample.schema.json",
        description="Normalized telemetry sample",
    ),
    "preflight_report": SchemaInfo(
        schema_id="preflight_report",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:preflight_report",
        path="schemas/v1/preflight_report.schema.json",
        description="Preflight check report",
    ),
    "safety_envelope": SchemaInfo(
        schema_id="safety_envelope",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:safety_envelope",
        path="schemas/v1/safety_envelope.schema.json",
        description="Safety envelope configuration",
    ),
    "operator_authorization": SchemaInfo(
        schema_id="operator_authorization",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:operator_authorization",
        path="schemas/v1/operator_authorization.schema.json",
        description="Operator authorization record",
    ),
    "calibration_profile": SchemaInfo(
        schema_id="calibration_profile",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:calibration_profile",
        path="schemas/v1/calibration_profile.schema.json",
        description="Calibration profile",
    ),
    "execution_audit_record": SchemaInfo(
        schema_id="execution_audit_record",
        version="1.0.0",
        urn=f"{SCHEMA_URN_PREFIX}:execution_audit_record",
        path="schemas/v1/execution_audit_record.schema.json",
        description="Execution audit record",
    ),
}


def get_schema_info(schema_id: str) -> SchemaInfo | None:
    """Get schema metadata by ID."""
    return SCHEMA_REGISTRY.get(schema_id)


def list_schemas() -> list[SchemaInfo]:
    """List all registered schemas."""
    return list(SCHEMA_REGISTRY.values())


def validate_schema_version(schema_id: str, version: str) -> bool:
    """Check if a schema ID and version combination is registered."""
    info = SCHEMA_REGISTRY.get(schema_id)
    if info is None:
        return False
    return info.version == version
