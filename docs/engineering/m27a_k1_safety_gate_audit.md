# M27-A K1 Safety-Gate Audit

**Milestone**: M27-A
**Date**: 2026-06-17
**Audit Type**: Safety Gate
**Method**: Repository static analysis only

## Authoritative Safety Config

**File**: `configs/m25_k1_safe_speed_operator_confirmation.yaml`

| Field | Value |
|-------|-------|
| `robot_id` | `k1` |
| `safe_command_speed_max` | **0.6 m/s** |
| `evidence_type` | `operator_confirmation` |
| `confirmed_by` | `operator` |
| `confirmed_at` | `2026-06-15T00:00:00Z` |

**Verification**: ✅ Confirmed from repository file.

## Safety Mechanisms

### 1. Dry-Run Default
All trial runners default to dry-run. The `--execute` flag is required for any hardware path.

### 2. Speed Limit Enforcement
- Max speed: **0.6 m/s**
- Enforcement: `command_runner.py` fails closed when no explicit max supplied
- No silent default to unlimited speed

### 3. Operator Confirmation
- YAML configuration with operator attestation
- Hashed into preflight output, plans, collection packages, session metadata, and audit trail

### 4. Fail-Closed Behavior

| Scenario | Result |
|----------|--------|
| SDK not importable | Exit code 1, no motor movement |
| No `--execute` flag | Dry-run only, no subprocess |
| No `safe_command_speed_max` | Error raised, no command sent |
| Subprocess failure | Trial not marked executed |
| Runtime exception | Finally block sends `Move(0,0,0)` |

### 5. Stop/Restore Behavior
- Normal: `Move(0,0,0)` at 10Hz for 2.0s
- Finally: `Move(0,0,0)` in finally block regardless of exception
- No explicit state restore beyond stop

## Gaps Against M26-B `SafetyEnvelope`

| Gap | Severity | Note |
|-----|----------|------|
| No explicit max vy/wz | Medium | K1 only uses vx commands |
| No connection-loss detection | Medium | Fixed duration; no heartbeat |
| No preflight checklist in SDK path | Low | M25 preflight exists but not integrated |
| Control/gait mode null in config | Low | Fixed SDK sequence used |

### M26-B Addresses These Via:
- `SafetyEnvelope` — explicit max values for all axes
- `OperatorAuthorization` — expiry and operation gating
- `PreflightReport` — checklist integration
- `ConnectionState` — DEGRADED/FAULTED for connection loss

## No Unsafe Defaults Found ✅

- Command runner requires explicit max speed
- All orchestrators default to dry-run
- SDK import failure prevents all motion
- Required arguments have no defaults
