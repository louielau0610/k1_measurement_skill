# M26-B Core Contracts Implementation

**Status**: Implemented
**Milestone**: M26-B / M26-BR
**Version**: 1.0.0

## Package Structure

```
calibration_skill/
    __init__.py          # Package entry point, version 0.1.0
    domain/
        __init__.py      # Public exports
        enums.py         # 14 stable enums + capability constants + lifecycle transitions
        errors.py        # 20 error codes + DomainError value object
        identity.py      # RobotIdentity
        capabilities.py  # CapabilityRecord, CapabilityDescriptor, negotiate_capabilities()
        readiness.py     # ReadinessEntry, ReadinessModel + 12 standard keys
        motion.py        # VelocityCommand, CommandReceipt, validate_lifecycle_transition()
        telemetry.py     # Vector3, Quaternion, Pose3D, Twist3D, TelemetrySample, TelemetryFreshness
        safety.py        # SafetyEnvelope, OperatorAuthorization, PreflightCheck, PreflightReport
        calibration.py   # TrialPlan, TrialResult, CalibrationDataset, CalibrationModel,
                         # CalibrationProfile, CompensationDecision, ExecutionAuditRecord,
                         # EnvironmentDescriptor
    ports/
        __init__.py      # Public exports
        robot.py         # RobotAdapter Protocol
        telemetry.py     # TelemetryStream Protocol
        authorization.py # OperatorAuthorizationProvider Protocol
        emergency_stop.py# EmergencyStop Protocol
        storage.py       # ProfileRepository Protocol
        audit.py         # AuditSink Protocol
        clock.py         # MonotonicClock Protocol
        factory.py       # AdapterFactory Protocol + ConnectionConfig
    schemas/
        __init__.py      # Public exports
        codec.py         # Deterministic JSON encode/decode functions + canonical_json_dumps()
        registry.py      # SchemaInfo, SCHEMA_REGISTRY, version management
        v1/
            13 JSON Schema documents (Draft 2020-12)
```

## Public Domain Contracts

| Contract | Module | Frozen | Invariants |
|---|---|---|---|
| RobotIdentity | identity | Yes | Non-empty robot_id, adapter_name, adapter_version |
| CapabilityRecord | capabilities | Yes | Non-empty capability_id |
| CapabilityDescriptor | capabilities | Yes | Non-empty platform_id |
| VelocityCommand | motion | Yes | Finite values, expiry > issued, positive duration, no silent max |
| CommandReceipt | motion | Yes | Non-empty sequence_id, non-negative received time |
| Vector3 | telemetry | Yes | Finite x, y, z |
| Quaternion | telemetry | Yes | Finite components, non-zero norm |
| Pose3D | telemetry | Yes | Composed of Vector3 + Quaternion |
| Twist3D | telemetry | Yes | Composed of Vector3 + Vector3 |
| TelemetrySample | telemetry | Yes | Non-empty robot_id, non-negative times, missing ≠ zero |
| TelemetryFreshness | telemetry | Yes | Age-ns derived from sample vs now_ns |
| SafetyEnvelope | safety | Yes | Explicit max values, finite non-negative limits, positive timeouts |
| OperatorAuthorization | safety | Yes | Expiry > issued, non-empty operations |
| PreflightCheck | safety | Yes | Non-empty check_id, name |
| PreflightReport | safety | Yes | Warnings ≠ blockers, blockers ⇒ not ready |
| TrialPlan | calibration | Yes | Positive repetitions, non-empty commands |
| TrialResult | calibration | Yes | Non-empty trial_id, plan_id |
| CalibrationDataset | calibration | Yes | Content digest via SHA-256 |
| CalibrationModel | calibration | Yes | Non-empty model_id |
| CalibrationProfile | calibration | Yes | Content digest, non-empty profile_id |
| CompensationDecision | calibration | Yes | Finite desired_actual_mps |
| ExecutionAuditRecord | calibration | Yes | Non-empty session_id |
| DomainError | errors | Yes | Stable code, no traceback in serialization |
| ReadinessEntry | readiness | Yes | Non-empty key |
| ReadinessModel | readiness | Yes | Composed of ReadinessEntry tuples |

## Port Protocols

All 8 port interfaces use `typing.Protocol`. No concrete implementations provided.

| Protocol | Purpose | Key Methods |
|---|---|---|
| RobotAdapter | Platform-specific robot control | connect, disconnect, preflight, send_velocity_command, stop, restore_safe_state |
| TelemetryStream | Telemetry acquisition | start, stop, get_latest, get_recent, health |
| OperatorAuthorizationProvider | Operator confirmation | request_authorization, validate_authorization |
| EmergencyStop | Hardware emergency stop | trigger, is_triggered, reset, supported |
| ProfileRepository | Immutable profile storage | publish, get, list_by_platform, get_gold |
| AuditSink | Append-only audit recording | record, get, list_sessions |
| MonotonicClock | Monotonic time source | now_ns, elapsed_since_ns, is_after_ns |
| AdapterFactory | Adapter creation | supports_platform, create_adapter, list_supported_platforms |

## Schema Registry

13 versioned JSON Schema documents at `schemas/v1/`, all using `urn:calibration-skill:schema:*:v1` URN identifiers, Draft 2020-12. Registered in `schemas/registry.py` with `SchemaInfo` metadata.

## Codec Responsibilities

- Round-trip encode/decode for 7 domain types (RobotIdentity, CapabilityDescriptor, VelocityCommand, CommandReceipt, TelemetrySample, SafetyEnvelope, OperatorAuthorization)
- One-way encode for 4 additional types (PreflightReport, CalibrationProfile, CompensationDecision, ExecutionAuditRecord)
- Canonical JSON generation: sorted keys, no whitespace, UTF-8
- NaN and Infinity rejection during encoding (checked via recursive scan)
- Content digest via SHA-256 of canonical JSON

## Capability Negotiation

`negotiate_capabilities(descriptor, required)` is a pure function:
- Returns `CapabilityNegotiationResult` with satisfied/missing/unknown/hw_verification
- No I/O, no mutation
- Unknown ≠ unsupported
- Supported ≠ hardware_verified

## Error Handling

- 20 stable error codes in `domain/errors.py`
- `DomainError` value object: frozen, code + message + retryable + details
- `to_dict()` does not include traceback
- Vendor exception objects not embedded directly
- Documented in `docs/engineering/m26b_error_taxonomy.md`

## Safety Invariants

- No silent default maximum velocity
- No silent clamping — violations produce errors, not adjusted values
- All safety limits must be explicitly provided to SafetyEnvelope
- Command expiry checked against monotonic time, not wall clock
- Operator authorization must be explicitly validated (never implicitly valid)
- Preflight: warnings ≠ blockers; blockers ⇒ not ready

## Side-Effect Boundaries

- Domain: zero I/O, zero network, zero env vars, zero subprocess, zero sleep, zero time
- Ports: Protocol definitions only, zero imports of vendor SDKs
- Schemas: codec functions are pure; no implicit state
- Architecture enforcement tests confirm these boundaries

## Limitations

- No adapter implementations (mock, K1, G1, GO1) — planned for later milestones
- No calibration execution engine
- No runtime process management
- No IPC mechanism
- Telemetry normalizers not implemented (raw platform packets → TelemetrySample)
- JSON Schema validation uses `jsonschema` library (already a project dependency)

## What Remains Legacy

- `calibration_core/` — existing K1 measurement pipeline (unchanged by M26-B)
- `k1_measurement/` — existing K1 tooling (unchanged)
- `platforms/booster_k1/` — existing K1 adapter (not migrated)
- `platforms/unitree_g1/` — scaffold (not implemented)
- `platforms/unitree_go1/` — scaffold (not implemented)

## Deliberately Not Implemented

- MockRobotAdapter (planned for M26-C)
- AdapterRegistry beyond the Protocol definition
- Skill execution service
- Calibration orchestration
- Profile fitting algorithms
- Compensation algorithms (exist in legacy code, not migrated)

## Mapping from Preliminary Contracts to Implemented Modules

| M26-A Preliminary Contract | M26-B Implementation |
|---|---|
| RobotAdapter | `ports/robot.py` (Protocol) |
| AdapterFactory | `ports/factory.py` (Protocol + ConnectionConfig) |
| CapabilityDescriptor | `domain/capabilities.py` |
| RobotIdentity | `domain/identity.py` |
| ConnectionConfig | `ports/factory.py` |
| MotionLifecycle | `domain/enums.py` (states + transitions) |
| VelocityCommand | `domain/motion.py` |
| CommandReceipt | `domain/motion.py` |
| TelemetrySample | `domain/telemetry.py` |
| TelemetryStream | `ports/telemetry.py` (Protocol) |
| PreflightReport | `domain/safety.py` |
| OperatorAuthorization | `domain/safety.py` |
| SafetyEnvelope | `domain/safety.py` |
| EmergencyStop | `ports/emergency_stop.py` (Protocol) |
| TrialPlan | `domain/calibration.py` |
| TrialResult | `domain/calibration.py` |
| CalibrationDataset | `domain/calibration.py` |
| CalibrationModel | `domain/calibration.py` |
| CalibrationProfile | `domain/calibration.py` |
| CompensationDecision | `domain/calibration.py` |
| ExecutionAuditRecord | `domain/calibration.py` |
| MonotonicClock | `ports/clock.py` (Protocol) |

## Deviations from M26-A Preliminary Design

1. **No `skill/` or `cli/` package** — deferred to later milestones (no operations to expose yet)
2. **No `runtime/` package** — deferred (no process management needed without adapters)
3. **No `application/` package** — deferred (calibration orchestration not yet implemented)
4. **`ConnectionConfig` in `ports/factory.py`** — placed with AdapterFactory rather than in a separate module
5. **`EnvironmentDescriptor` in `domain/calibration.py`** — grouped with calibration contracts
6. **ProfileRepository as Protocol** — defined in ports, not yet implemented as filesystem storage
7. **One-way codecs for complex types** — PreflightReport, CalibrationProfile, CompensationDecision, ExecutionAuditRecord have encode-only for now

## Test Coverage

| Test File | Focus | Test Count |
|---|---|---|
| test_domain_identity.py | RobotIdentity construction, validation, immutability | ~10 |
| test_domain_capabilities.py | CapabilityDescriptor, negotiate_capabilities | ~12 |
| test_domain_motion.py | VelocityCommand, CommandReceipt, lifecycle | ~18 |
| test_domain_telemetry.py | Vector3, Quaternion, TelemetrySample | ~12 |
| test_domain_safety.py | SafetyEnvelope, OperatorAuthorization, Preflight | ~15 |
| test_domain_calibration.py | TrialPlan, TrialResult, CompensationDecision, errors | ~12 |
| test_codecs.py | Round-trip codecs, canonical JSON, enum stability | ~9 |
| test_ports.py | All 8 Protocols importable, no concrete implementations | ~10 |
| test_schema_documents.py | Schema parse, $id stability, version consistency | ~23 |
| test_architecture_boundaries.py | Forbidden imports, import side effects | ~10 |
