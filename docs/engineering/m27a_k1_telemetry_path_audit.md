# M27-A K1 Telemetry Path Audit

**Milestone**: M27-A
**Date**: 2026-06-17
**Audit Type**: Telemetry Path
**Method**: Repository static analysis only

## Primary Telemetry Source

**ROS2 `/odometer_state`** (`booster_interface/msg/Odometer`)
- Fields: `x`, `y`, `theta`
- Discovery: `source /opt/booster/BoosterRos2Interface/install/setup.bash`
- Used by all M19C/M23-B/M24-B/M24-H loggers

## Fallback Sources

1. **`/low_state.imu_state.rpy`** — yaw fallback (roll, pitch, yaw)
2. **IMU topics** (`sensor_msgs/Imu`) — secondary yaw fallback
3. **Booster SDK state** — read-only SDK-level state discovery (not primary)

## Logger Scripts

| Script | Layer | Topics | SDK Import |
|--------|-------|--------|------------|
| `log_k1_ros2_odometer_state.py` | M19C | `/odometer_state` | No |
| `log_m23b_k1_compensation_trial.py` | M23-B | `/odometer_state`, `/low_state` | No |
| `log_m24b_s2_profile_refresh_trial.py` | M24-B | `/odometer_state`, `/low_state` | No |
| `log_m24h_controlled_s2_replication_trial.py` | M24-H | `/odometer_state`, `/low_state` | No |
| `start_real_k1_field_logger.py` | Field | `/odometer_state`, `/low_state` | No |
| `log_k1_sdk_state_smoke.py` | M19R-C | SDK state | Yes |

## Extraction Pipeline

- **Velocity**: `dx/dt` from odometer x position
- **Yaw**: `dtheta/dt` from odometer theta (or IMU rpy yaw fallback)
- **Deadzone**: 0.20 m/s low-speed deadzone confirmed in M19C smoke tests

## Data Quality

- QC checks: pair completeness, field presence, no command copy
- QC scripts: `qc_booster_k1_measurement_session.py`, `qc_m23b_k1_compensation_session.py`

## Known Limitations

- No UTC timestamps — ROS time only
- `GetFrameTransform` downgraded (local body-part frames only)
- 0.20 m/s deadzone — low-speed measurements unreliable
- No battery/state data in telemetry
- Windows cannot import ROS2/Booster — all real telemetry on robot

## Split-Process Enforcement

- **Rule**: ROS2 logger subprocess MUST NOT import Booster SDK
- **Enforced by**: `tests/test_m23b_auto_sdk_command_subprocess.py`
- **Status**: ✅ Verified

## Mapping to `TelemetrySample`

| Legacy Field | `TelemetrySample` Field |
|-------------|------------------------|
| `odometer.x` | `position_x` |
| `odometer.y` | `position_y` |
| `odometer.theta` | `yaw` |
| `imu.rpy.yaw` | `yaw` (fallback) |
| ROS timestamp | `timestamp` |
| Computed velocity | `velocity_vx` |
