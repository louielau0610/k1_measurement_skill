# K1 Velocity Measurement Skill

This repository is the measurement-stage predecessor of the larger **K1 Velocity Measurement, Compensation and Navigation Safety Pipeline**.

The larger project addresses a practical robotics issue on Booster Robotics K1: commanded forward velocity (`v_cmd`) can differ from actual executed velocity (`v_actual`). During navigation, this mismatch can accumulate into position error, trajectory drift, and collision risk.

This repository implements only:

```text
v_x_cmd -> v_x_actual measurement
```

It does not implement velocity compensation, autonomous navigation, real-time closed-loop control, real robot movement commands, or hard-coded unverified ROS2 topic names.

The primary downstream interface is:

```text
processed_environment_profile.json
```

This profile is intended for later modules such as velocity compensation models, safe command adapters, navigation safety layers, and simulation validation pipelines. Downstream users must check confidence, valid speed range, environment match, sample size, and extrapolation risk before using a profile.

## Data Interface Contract

`processed_environment_profile.json` is the downstream contract between this measurement repository and future compensation or navigation safety modules.

The schema is defined in:

```text
contracts/measurement_profile_schema.json
```

A dummy validation-only example is provided at:

```text
examples/dummy_processed_environment_profile.json
```

This repository does not implement compensation. Future downstream modules may consume the profile, but they must validate schema version, environment match, speed range, confidence, trial count, ground-truth method, odom validation status, extrapolation policy, and warnings before use.

## Core Measurement Metrics

M2 implements pure measurement metrics:

- actual velocity: `v_x_actual = (x_end - x_start) / (t_end - t_start)`
- speed gain: `speed_gain = v_x_actual / v_x_cmd`
- absolute error: `e_abs = v_x_actual - v_x_cmd`
- relative error: `e_rel = (v_x_actual - v_x_cmd) / v_x_cmd`
- lateral drift rate: `|y_end - y_start| / (t_end - t_start)`
- yaw drift rate: `|yaw_end - yaw_start| / (t_end - t_start)`
- tracking RMSE: `sqrt(mean((v_actual_i - v_cmd)^2))`

These metrics are measurement-only. They do not implement compensation, and they will later support `processed_environment_profile.json` generation.

## M3 Dummy Data Pipeline

The dummy pipeline validates the repository workflow before real K1 ROS2 integration:

```text
dummy raw measurement log -> processed environment profile -> schema validation -> tests
```

Dummy data is not real robot data. Dummy profiles must not be used for compensation, navigation, or robot safety decisions. This repository still does not implement compensation.

## M4 ROS2 Topic Discovery and Logger Skeleton

The discovery script is read-only. It detects whether `ros2` is available and, when present, runs only `ros2 topic list`.

Candidate topic classification is keyword-based and is not verification. Real logging remains disabled until odom, imu, and robot_state topics are manually verified in `config/topic_mapping_template.yaml`.

The repository still does not implement robot movement, ROS2 publishers, or velocity compensation.

## M5 Dry-run Forward Baseline Trial Manager

This milestone generates and validates the forward velocity baseline trial plan. It is dry-run only, does not publish ROS2 commands, and does not move the robot.

Real execution remains disabled until the K1 command interface is manually verified in a future milestone.
