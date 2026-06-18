# M27-D: K1 Runtime Failure Matrix

## Construction Failures

| Condition | Error Code | Recovery |
|-----------|-----------|----------|
| Missing hardware gate | `k1_hardware_gate_missing` | Provide explicit gate |
| Expired gate | `k1_hardware_gate_expired` | Create new session gate |
| Incomplete confirmations | `k1_hardware_gate_incomplete` | Complete all confirmations |
| Wrong robot ID | `k1_hardware_gate_incomplete` | Match robot ID to gate |
| Wrong safety policy ID | `k1_hardware_gate_incomplete` | Match policy ID |
| Wrong safety policy hash | `k1_hardware_gate_incomplete` | Match policy hash |
| Wrong adapter mode | `k1_hardware_gate_incomplete` | Set expected_adapter_mode |
| Vendor runtime not enabled | `k1_vendor_runtime_not_implemented` | Set --enable-vendor-runtime |
| Hardware execution disabled | `k1_hardware_execution_disabled` | Set --execute-hardware |
| SDK not discoverable | `k1_sdk_unavailable` | Install SDK on robot |
| SDK import failed | `k1_sdk_import_failed` | Verify SDK installation |
| Binding construction failed | `k1_binding_construction_failed` | Check SDK version compatibility |

## Runtime Operation Failures

| Operation | Error Code | Behavior |
|-----------|-----------|----------|
| Connect failure | `k1_connection_failed` | Runtime not connected; retryable |
| Identity read error | `k1_binding_operation_failed` | Operation fails; runtime stays connected |
| Motion state read error | `k1_binding_operation_failed` | Returns UNAVAILABLE state |
| Prepare mode failure | `k1_binding_operation_failed` | Operation fails; state unchanged |
| Walking mode failure | `k1_binding_operation_failed` | Operation fails; state unchanged |
| Nonzero velocity command | `k1_m27d_nonzero_motion_forbidden` | Rejected before SDK call |
| Command while disconnected | `k1_vendor_runtime_disconnected` | Rejected; retryable |
| Command before locomotion-ready | `k1_vendor_runtime_not_locomotion_ready` | Rejected; retryable |
| Stop unacknowledged | `k1_m27d_stop_unacknowledged` | Runtime attempts safe restoration |
| Odometry unavailable | (returns None) | Graceful; no error raised |
| Battery unavailable | (returns None) | Graceful; no error raised |
| Health check failure | (returns unhealthy) | Structured health report |

## Cleanup Behavior

- `restore_safe_state()` — Best-effort, never raises
- `disconnect()` — Idempotent, safe to call multiple times
- All cleanup in `try/finally` blocks in bench runner

## Structured Error Format

All errors use `DomainError` with:
- `code` — Stable error code string
- `message` — Human-readable message
- `retryable` — Whether retry is appropriate
- `details` — Structured context (no tracebacks, no SDK object reprs)
- `cause_type` — Original exception class name (sanitized)

## M27-D.1 Failure-Matrix Corrections

SDK availability is split into distinct evidence:

- `package_probe_discoverable`: only
  `find_spec("booster_robotics_sdk_python")`.
- `direct_entry_modules_discoverable`: all of `B1LocoClient`,
  `ChannelFactory`, and `RobotMode` specs found without importing.
- `direct_imports_verified`: true only after explicit direct imports and class
  resolution succeed.

`k1_sdk_unavailable` is reserved for direct SDK entry-module discovery failures.
It must not be used for missing gates, policy mismatches, authorization, or
configuration failures. A missing hardware gate is `k1_hardware_gate_missing`.

Direct import failures use `k1_sdk_import_failed`; missing
`B1LocoClient.B1LocoClient`, `ChannelFactory.ChannelFactory`, or
`RobotMode.RobotMode` fails closed.

Structured vendor errors must not serialize uncontrolled raw SDK reprs, memory
addresses, credentials, network secrets, or full tracebacks. Allowed evidence is
stable error code, sanitized operation/message, exception class name, and
retryable flag.
