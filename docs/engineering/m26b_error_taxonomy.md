# M26-B Error Taxonomy

**Status**: Active
**Milestone**: M26-B
**Version**: 1.0.0

## Purpose

This document defines the stable error taxonomy for the calibration skill.
Each error has a stable code, meaning, retryability, expected caller action,
hardware-motion risk, and cleanup requirement.

## Error Codes

| Code | Meaning | Retryable | Caller Action | Hardware May Have Moved | Cleanup Required |
|---|---|---|---|---|---|
| `configuration_missing` | Required configuration is absent | No | Provide configuration | No | None |
| `configuration_invalid` | Configuration fails validation | No | Fix configuration | No | None |
| `unsupported_platform` | Platform is not in the supported set | No | Select a supported platform | No | None |
| `capability_unavailable` | Required capability is unsupported or missing | No | Choose different operation or platform | No | None |
| `capability_unverified` | Capability status is unknown or needs HW verification | No | Verify capability before proceeding | No | None |
| `precondition_failed` | A required precondition is not met | Sometimes | Check state and retry if transient | No | None |
| `adapter_disconnected` | Robot adapter lost connection | Yes | Reconnect adapter | Possibly | Emergency stop if in motion |
| `wrong_motion_state` | Robot is in wrong state for the operation | Yes | Transition to correct state | No | None |
| `operator_authorization_required` | Operator has not authorized the operation | No | Obtain operator authorization | No | None |
| `operator_authorization_expired` | Operator authorization has expired | No | Renew authorization | No | Stop if in motion |
| `command_expired` | Command TTL elapsed before execution | Yes | Re-issue command with later expiry | No | None |
| `command_outside_safety_envelope` | Command violates safety limits | No | Adjust command to within limits | No | None |
| `telemetry_unavailable` | No telemetry data is available | Yes | Wait for telemetry or check connection | No | Do not send commands |
| `telemetry_stale` | Telemetry age exceeds staleness threshold | Yes | Wait for fresh telemetry | No | Do not send commands; consider stop |
| `stop_unacknowledged` | Stop command was not acknowledged | No | Escalate to emergency stop | Yes | Trigger emergency stop |
| `schema_version_unsupported` | Schema version is not recognized | No | Use a supported schema version | No | None |
| `serialization_failed` | Data could not be serialized/deserialized | No | Fix data format | No | None |
| `provenance_invalid` | Artifact provenance chain is broken | No | Investigate data integrity | No | None |
| `internal_error` | Unexpected internal error | No | Report bug; do not retry automatically | Unknown | Restore safe state |
| `validation_failed` | Domain validation failed | No | Fix the invalid data | No | None |

## Error Response Format

All errors are serialized as:

```json
{
  "code": "error_code_string",
  "message": "Human-readable description",
  "retryable": true_or_false,
  "details": {}
}
```

Vendor-specific exception objects must not be embedded directly.
Tracebacks are not included by default.
