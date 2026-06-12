# M24-A S2 Profile Refresh Result Schema

M24-B/M24-C should fill this schema only from real Booster K1 S2 refresh logs. M24-A creates no physical results.

| Field | Required | Description |
|-------|----------|-------------|
| `trial_id` | yes | Trial ID from `m24a_s2_profile_refresh_plan.csv`. |
| `refresh_group_id` | yes | Group for one command velocity across repeats. |
| `surface` | yes | Must be `S2_marble_floor`. |
| `command_velocity_mps` | yes | Direct command sent to K1. |
| `desired_velocity_mps` | yes | Desired velocity for comparison; equals direct command in this refresh. |
| `measured_actual_velocity_mps` | yes when extraction succeeds | Actual velocity extracted from real state logs. |
| `tracking_error_mps` | yes when extraction succeeds | `measured_actual_velocity_mps - desired_velocity_mps`. |
| `yaw_drift_deg` | yes when extraction succeeds | Yaw drift from odometer theta. |
| `imu_yaw_drift_deg` | optional | IMU yaw drift if available from synchronized low-state or IMU logs. |
| `extraction_status` | yes | `ok`, `invalid`, or `missing_log`. |
| `invalid_reason` | required if invalid | Reason the trial cannot be used. |
| `state_log_path` | yes | Path to the real state log used for extraction. |
| `physical_run_status` | yes | `planned`, `run`, `invalid`, or `not_run`. |
| `notes` | optional | Operator or extraction notes. |

No field may be copied from command velocity as a replacement for a missing physical measurement.
