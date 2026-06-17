# M27-A K1 Command Path Audit

**Milestone**: M27-A
**Date**: 2026-06-17
**Audit Type**: Command Path
**Method**: Repository static analysis only — no K1 connection, no hardware

## Verified Motion Chain

```
kPrepare → kWalking → Move(vx, 0.0, 0.0)
```

**Status**: ✅ Verified from repository evidence in `scripts/send_m23b_k1_velocity_command.py`.

## Entry Points

### Primary Command Sender: `scripts/send_m23b_k1_velocity_command.py`
- **Role**: Sends Booster SDK velocity commands to K1
- **SDK Imports**: `B1LocoClient`, `ChannelFactory`, `RobotMode`
- **Arguments**: `--trial-id`, `--command-velocity` (required), `--interface`, `--idle-sec`, `--command-sec`, `--stop-sec`, `--prepare-sec`, `--walking-sec`, `--log-dir`

### Orchestrators (subprocess launchers)
- `scripts/run_m23b_k1_compensation_trials.py` — compensation trials
- `scripts/run_booster_k1_measurement.py` — general measurement
- `scripts/run_m24b_s2_profile_refresh_trials.py` — profile refresh
- `scripts/run_m24h_controlled_s2_replication_trials.py` — controlled replication

## Argument Gates

| Gate | Default | Fail-Safe |
|------|---------|-----------|
| `--execute` flag | Dry-run (no hardware) | Omitting flag prevents all SDK calls |
| `--command-velocity` | Required; no default | Argparse enforces required argument |
| `safe_command_speed_max` | 0.6 m/s from safety config | `command_runner.py` fails closed when no max supplied |

## Lifecycle Sequence

1. **Import Check** — Verify Booster SDK available (no hardware)
2. **Channel Init** — `ChannelFactory.Instance().Init(0, interface)` → network connection
3. **Client Init** — `B1LocoClient().Init()` → robot connection
4. **kPrepare** — `RobotMode(kPrepare)`, sleep 3.0s → mode change
5. **kWalking** — `RobotMode(kWalking)`, sleep 2.0s → walking mode
6. **Idle** — `Move(0,0,0)` at 10Hz for 2.0s → no motion
7. **Command** — `Move(vx,0,0)` at 10Hz for 6.0s → **PHYSICAL MOTION**
8. **Stop** — `Move(0,0,0)` at 10Hz for 2.0s → stop motion
9. **Final Stop** — `Move(0,0,0)` in finally block → guaranteed stop attempt

## Stop Behavior

- **Normal**: `Move(0,0,0)` at 10Hz for `stop_sec` seconds
- **Finally**: `Move(0,0,0)` sent regardless of exception
- **Import Failure**: Exit code 1, no motor movement, error logged
- **Runtime Error**: Exception caught, stop attempted, exit code 1

## Hardware Motion Points

| Location | Risk |
|----------|------|
| `ChannelFactory.Instance().Init()` | Network connection to robot |
| `RobotMode(kPrepare)` | Mode change on robot |
| `RobotMode(kWalking)` | Walking mode activation |
| `Move(vx, 0.0, 0.0)` | **Physical robot motion** |
| `Move(0.0, 0.0, 0.0)` | Stop command |

## Error Handling

- SDK not importable → clear error, exit code 1, no motor movement
- Runtime exception → caught, logged, finally block sends stop
- Subprocess failure → orchestrator detects non-zero exit, trial not marked executed

## Logging & Audit Trail

Every command execution produces a JSON command log containing:
- `trial_id`, `command_velocity`, `import_status`
- `prepare_status`, `walking_status`
- Per-phase timings and velocities
- `exit_status`, `exit_code`, `error` (if any)

## Limitations

- Chain verified from source code only; no live K1 connection
- Assumes Booster SDK API behaves as documented in code
- `kPrepare`/`kWalking` are assumed valid `RobotMode` enum values
