# M19R-C Prep SDK State Logger Protocol

M19R-C-prep now prioritizes ROS2 odometer-state logging because robot-side discovery showed that sourcing the Booster ROS2 interface makes `booster_interface` available and `/odometer_state` exposes the needed `x`, `y`, and `theta` fields.

Robot shell requirement:

```bash
source /opt/booster/BoosterRos2Interface/install/setup.bash
```

## Acceptable State Sources

Priority 1: `/odometer_state [booster_interface/msg/Odometer]` with `x`, `y`, and `theta`.

Priority 2: `/low_state [booster_interface/msg/LowState]`, specifically `imu_state.rpy`, as a yaw cross-check.

Priority 3: `/booster/ros2_k2_imu [sensor_msgs/msg/Imu]` or `/send_imu [sensor_msgs/msg/Imu]` as fallback yaw sources when odometer theta is not sufficient.

`B1LocoClient.GetFrameTransform` is no longer a primary displacement source. The discovered frame members are local body-part frames (`kBody`, `kHead`, `kLeftFoot`, `kRightFoot`, `kLeftHand`, `kRightHand`, `kUnknown`) rather than clear `odom`, `world`, or `map` frames, so these transforms should not be used as global forward displacement evidence.

Manual video annotation remains a fallback, not the preferred path, because odometer logs can provide timestamped position and yaw from the robot interface.

## Measurement Computation

For each trial, use `/odometer_state` samples in the analysis window `[1.0, 6.0]` seconds after command start.

Actual velocity is computed from forward displacement projected onto the starting yaw:

```text
distance_m = dot([x_end - x_start, y_end - y_start], [cos(theta_start), sin(theta_start)])
measured_actual_velocity = distance_m / time_sec
```

Yaw drift is the absolute wrapped yaw change:

```text
yaw_drift_statistic = abs(wrap_to_pi(theta_end - theta_start)) in degrees
```

## Evidence Boundary

Prior M19 execution-only trials cannot be retroactively converted into empirical measurements unless matching SDK logs, parseable raw logs, or valid video/manual measurement evidence exists. Command velocity must never be copied into `measured_actual_velocity`.

## Decision Gate

The full M19C measurement run is ready only when `/odometer_state` publishes at usable frequency, `x/y/theta` change consistently during movement, extracted velocity is nonzero for moving smoke trials, and yaw drift is computed from theta without fabricated values. This prep milestone does not compute response statistics, validate the risk map, or claim M19 empirical completion.
