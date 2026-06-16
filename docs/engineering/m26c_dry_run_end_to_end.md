# M26-C Dry-Run End-to-End Flow

The M26-C dry-run flow proves that the M26-B contracts can drive a complete
skill operation without hardware.

## Operation

`dry_run_end_to_end` performs:

1. resolve the mock adapter through `AdapterRegistry`;
2. connect the mock adapter;
3. run preflight;
4. enter locomotion-ready state;
5. validate the explicit `SafetyEnvelope`;
6. validate simulated `OperatorAuthorization` when required;
7. send a `VelocityCommand`;
8. collect deterministic `TelemetrySample`;
9. stop;
10. restore safe state;
11. generate an `ExecutionAuditRecord`;
12. return a schema-compatible skill response.

All time values come from an injected deterministic monotonic clock. Monotonic
timestamps remain process-local and must not be compared across processes unless
a runtime establishes an explicit clock relationship.

## Cleanup Semantics

If preflight or command dispatch fails, the service still attempts stop and
safe-state restore where applicable. Cleanup results are recorded in the audit
record. A rejected response contains a structured error and keeps warnings
separate from terminal errors.

## Audit Semantics

M26-C audit generation is in-memory and append-only inside the returned service
object. The audit record includes request ID, operation, mock platform, robot
identity, software and adapter versions, safety policy, authorization reference,
command, receipt, telemetry evidence when available, cleanup result, errors, and
canonical request digest. It explicitly records that no hardware evidence is
claimed.

No audit files are written by default.
