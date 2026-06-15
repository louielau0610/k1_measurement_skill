# ADR-0003: Fail-Closed Hardware Execution

**Status**: Accepted
**Date**: 2026-06-15
**Milestone**: M26-A

## Context

Robot velocity calibration involves sending motion commands to physical robots.
A software bug, configuration error, or unexpected robot state could result in
unsafe motion. The system must default to safety: any uncertainty, error, or
missing authorization must prevent motion, not allow it.

The current K1 implementation already follows several fail-closed patterns:
- `K1CommandRunner` defaults to `dry_run=True`
- `K1MeasurementLogger` refuses unsafe setup
- Safe speed maximum is operator-confirmed and hashed into the audit trail
- Command sequences require explicit operator enablement

These patterns must be formalized as architectural invariants that apply to all
platforms.

## Decision

All hardware execution paths will follow a **fail-closed** design:

1. **Dry-run is the default**: No motion command is sent unless explicitly
   enabled by the operator through a confirmed authorization mechanism.

2. **Safety envelope enforcement**: Every velocity command is validated against
   a `SafetyEnvelope` before transmission. Commands outside the envelope are
   rejected. There is no silent clamping or default maximum.

3. **Explicit operator confirmation**: The operator must explicitly confirm the
   trial plan and safety parameters before any motion-capable state is entered.
   Confirmation expires and must be renewed.

4. **Command expiry**: Every command has an `expiry_monotonic_ns`. Expired
   commands must not be sent. If a command expires during execution, a stop
   command is sent.

5. **Telemetry-gated execution**: Motion commands are only sent when telemetry
   is current (not stale). Stale telemetry blocks command execution.

6. **Emergency stop escalation**: If a normal stop is not acknowledged, the
   system escalates to emergency stop. If emergency stop is not acknowledged,
   platform-specific hardware stop is triggered.

7. **Safe state on any error**: Any error during motion-capable states triggers
   transition to safe state (stop → exit locomotion → safe standing/sitting).

## Alternatives Considered

### A. Fail-open with operator override
- **Rejected**: Unsafe. Operator may not react quickly enough to prevent
  dangerous motion.

### B. Speed clamping (silently reduce unsafe commands)
- **Rejected**: Hides configuration errors. Operator should know when a command
  exceeds the safety envelope and explicitly decide.

### C. Trust the robot's internal safety systems
- **Rejected**: Defense in depth. The calibration skill should not rely solely
  on the robot's internal safety mechanisms, which may have different failure
  modes.

## Consequences

### Positive
- No accidental robot motion from configuration errors or software bugs
- Clear audit trail of all safety decisions
- Operator maintains explicit control over all motion-capable operations
- Safety behavior is consistent across all platforms

### Negative
- More steps required to execute trials (preflight, confirmation, etc.)
- False positives in safety checks may block legitimate operations
- Stale telemetry checks may trigger during normal network jitter

## Migration Impact

- Formalize existing K1 safety patterns as `SafetyEnvelope` and
  `OperatorAuthorization` contracts
- Apply fail-closed checks uniformly across all adapter implementations
- Add telemetry staleness monitoring to the runtime layer
- Ensure mock adapter also exercises safety checks (for testing)

## Validation Requirements

- Safety envelope rejects commands exceeding maximum velocity
- Expired commands are rejected before transmission
- Stale telemetry blocks command execution
- Stop escalation works: normal stop timeout → emergency stop
- Operator denial prevents motion
- Expired authorization prevents new trials
