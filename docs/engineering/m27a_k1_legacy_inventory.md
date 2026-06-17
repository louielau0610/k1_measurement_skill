# M27-A K1 Legacy Adapter Inventory

**Milestone**: M27-A — K1 Legacy Adapter Extraction Plan and Compatibility Boundary
**Date**: 2026-06-17
**Status**: Planning/Audit Only — No Migration Implemented

## Purpose

This inventory catalogs every repository file related to K1 legacy behavior, providing the foundation for M27-B/M27-C migration into the new `RobotAdapter` architecture.

## Summary Statistics

| Category | Count |
|----------|-------|
| Command-sending scripts | 6 |
| Telemetry/logging scripts | 10 |
| Safety configuration files | 3 |
| Analysis/reporting scripts | 12 |
| Platform modules (`platforms/booster_k1/`) | 11 |
| `k1_measurement/` modules | 23 |
| `calibration_core/` K1 references | 4 |

## Critical Hardware Path

The only file that directly sends Booster SDK motion commands:

- **`scripts/send_m23b_k1_velocity_command.py`** — imports `B1LocoClient`, `ChannelFactory`, `RobotMode`; executes `kPrepare → kWalking → Move(vx, 0.0, 0.0)`.

This file is used as a subprocess by M23-B, M24-B, and M24-H trial runners.

## Command Sending Scripts

| File | Risk | SDK Import | Migration |
|------|------|------------|-----------|
| `scripts/send_m23b_k1_velocity_command.py` | Critical | Direct B1LocoClient | → `RobotAdapter.send_velocity_command` |
| `scripts/run_booster_k1_measurement.py` | High | Subprocess only | → Skill service orchestration |
| `scripts/run_m23b_k1_compensation_trials.py` | High | Subprocess only | → Compensation experiment runner |
| `scripts/run_m24b_s2_profile_refresh_trials.py` | High | Subprocess only | → Profile refresh runner |
| `scripts/run_m24h_controlled_s2_replication_trials.py` | High | Subprocess only | → Replication runner |
| `scripts/run_m19c_ros2_odometer_trials.py` | High | Direct import | → M19C-compatible runner |

## Telemetry Scripts

All telemetry scripts use `rclpy` exclusively and explicitly avoid Booster SDK imports (enforced by split-process architecture tests).

| File | Source | Migration |
|------|--------|-----------|
| `scripts/log_m23b_k1_compensation_trial.py` | `/odometer_state`, `/low_state` | → `TelemetryStream` |
| `scripts/log_m24b_s2_profile_refresh_trial.py` | `/odometer_state`, `/low_state` | → `TelemetryStream` |
| `scripts/log_m24h_controlled_s2_replication_trial.py` | `/odometer_state`, `/low_state` | → `TelemetryStream` |
| `scripts/log_k1_ros2_odometer_state.py` | `/odometer_state` | → `TelemetryStream` |
| `scripts/log_k1_sdk_state_smoke.py` | SDK state (read-only) | → `TelemetryStream.discover_sources` |
| `scripts/start_real_k1_field_logger.py` | ROS2 field logger | → Field telemetry session |

## Safety Configuration

| File | Role | Key Value |
|------|------|-----------|
| `configs/m25_k1_safe_speed_operator_confirmation.yaml` | Authoritative safety config | `safe_command_speed_max: 0.6 m/s` |
| `configs/m25_k1_safe_speed_operator_confirmation_template.yaml` | Operator confirmation template | Template |
| `configs/m25_k1_s2_real_collection.yaml` | S2 collection domain | `[0.35, 0.60] m/s` |

## Key Findings

1. **Verified motion chain**: `kPrepare → kWalking → Move(vx, 0.0, 0.0)` confirmed in `send_m23b_k1_velocity_command.py`.
2. **Verified safe speed**: `0.6 m/s` from `configs/m25_k1_safe_speed_operator_confirmation.yaml`.
3. **Split-process isolation**: SDK command subprocess strictly separated from ROS2 logger subprocess.
4. **M26-C status**: K1 is NOT registered in `AdapterRegistry`; only `MOCK` platform is supported in new runtime.
5. **No migration implemented**: All K1 support remains in legacy paths only.
