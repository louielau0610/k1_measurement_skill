# M19C ROS2 Odometer Measurement Protocol

M19C uses `/odometer_state [booster_interface/msg/Odometer]` as the primary measurement source because robot-side discovery confirmed that it publishes `x`, `y`, and `theta` at approximately 499 Hz after sourcing the Booster ROS2 interface.

## Required Shell Setup

```bash
source /opt/ros/humble/setup.bash
source /opt/booster/BoosterRos2Interface/install/setup.bash
```

## State Sources

- Primary: `/odometer_state`, fields `x`, `y`, `theta`.
- Yaw cross-check: `/low_state.imu_state.rpy[2]`.
- Fallback yaw topics: `/booster/ros2_k2_imu` and `/send_imu`, only if useful output is confirmed.
- Do not use `GetFrameTransform` as the primary global displacement source because available frames are local body-part frames.

## Trial Plan

Run surfaces separately:

```bash
python3 scripts/run_m19c_ros2_odometer_trials.py --surface S1_lab_hard_floor --interface lo --execute
python3 scripts/run_m19c_ros2_odometer_trials.py --surface S2_marble_floor --interface lo --execute
python3 scripts/run_m19c_ros2_odometer_trials.py --surface S3_artificial_turf --interface lo --execute
```

Dry-run one surface without robot commands:

```bash
python3 scripts/run_m19c_ros2_odometer_trials.py --surface S1_lab_hard_floor
```

Each trial uses 2 seconds idle, 6 seconds command, and 2 seconds stop. The command path is `kPrepare`, `kWalking`, then `Move(vx, 0, 0)`.

## Analysis Window

The extractor uses `t_rel = 3.0` to `8.0` seconds. The command begins after the 2 second idle period, so this corresponds to command-window seconds 1 to 6 and excludes the first 1 second startup transient.

## Measurement Formula

```text
dx = x_end - x_start
dy = y_end - y_start
distance_m = dot([dx, dy], [cos(theta_start), sin(theta_start)])
measured_actual_velocity = distance_m / time_sec
yaw_drift_statistic = abs(wrap_to_pi(theta_end - theta_start)) * 180 / pi
```

If IMU yaw is available:

```text
imu_yaw_drift_deg = abs(wrap_to_pi(imu_yaw_end - imu_yaw_start)) * 180 / pi
```

## Validity and Backup

A trial is valid only if the state log exists, `/odometer_state` has enough samples in the analysis window, and `x/y/theta` are parseable. Back up `data/m19c_ros2_odometer_logs/` and `data/m19_repeated_validation_inputs/m19c_trial_records.csv` after each surface before starting the next surface.

## Claim Boundaries

This protocol prepares measurement collection. It does not generate response curves, validate the response model, validate the risk map, claim navigation improvement, or claim cross-robot generalization.
