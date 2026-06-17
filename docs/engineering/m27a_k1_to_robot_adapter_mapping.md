# M27-A K1 to RobotAdapter Mapping

**Milestone**: M27-A
**Date**: 2026-06-17
**Status**: Planning Only — No Implementation
**Target**: M27-B (adapter implementation), M27-C (hardware integration)

## Mapping Summary

| Contract | Legacy Source | Risk |
|----------|--------------|------|
| `RobotIdentity` | Safety config `robot_id: k1`, `.env.example` | Low |
| `CapabilityDescriptor` | M21-B platform config | Low |
| `ConnectionConfig` | `.env.example` IP, `--interface` arg | Low |
| `connect` | `ChannelFactory.Init()` + `B1LocoClient.Init()` | Medium |
| `disconnect` | Implicit scope cleanup | Low |
| `preflight` | `m25_real_collection_preflight.py` | Low |
| `motion_state` | SDK `RobotMode` enum | Medium |
| `enter_locomotion_ready` | `kPrepare` → sleep → `kWalking` → sleep | **High** |
| `send_velocity_command` | `Move(vx,0,0)` loop at 10Hz | **High** |
| `stop` | `Move(0,0,0)` in stop phase + finally | **High** |
| `restore_safe_state` | No legacy equivalent | Medium |
| `TelemetryStream` | ROS2 subscriber scripts | Medium |
| `SafetyEnvelope` | `safe_command_speed_max: 0.6` | Low |
| `OperatorAuthorization` | Operator confirmation YAML | Low |
| `CommandReceipt` | Command log JSON dict | Low |
| `ExecutionAuditRecord` | Combined audit artifacts | Low |

## High-Risk Mappings

### 1. `send_velocity_command`
- **Legacy**: `Move(vx, 0.0, 0.0)` at 10Hz for `command_sec` duration
- **New**: `async send_velocity_command(VelocityCommand) → CommandReceipt`
- **Risks**: Command frame timing, SDK send rate, duration accuracy
- **Test**: Mock adapter + hardware-gated validation

### 2. `stop`
- **Legacy**: `Move(0,0,0)` in stop phase + finally block
- **New**: `async stop() → CommandReceipt` with acknowledgement
- **Risks**: Must work from any state; stop acknowledgement uncertain
- **Test**: Stop from MOVING, FAULTED, UNKNOWN states

### 3. `enter_locomotion_ready`
- **Legacy**: `kPrepare` (3s) → `kWalking` (2s) sequence
- **New**: `async enter_locomotion_ready()`
- **Risks**: Mode lifecycle timing SDK-dependent; no explicit state query API
- **Test**: Hardware-gated lifecycle transition validation

## Safety Preconditions (All Mappings)
- `SafetyEnvelope` must be explicitly provided — no silent defaults
- `OperatorAuthorization` must be valid and unexpired
- `PreflightReport` must pass before any motion command
- `dry_run` flag must be `false` for any hardware path
