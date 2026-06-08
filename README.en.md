# K1 Velocity Measurement Toolkit

## Positioning

`k1_measurement_skill` is the measurement-first module of the larger **K1 Velocity Measurement, Compensation, and Navigation Safety Pipeline**.

```text
v_actual = f(v_cmd, environment, robot_state)
```

This repository measures the relationship between commanded forward velocity and actual executed velocity on the Booster Robotics K1. It is not a full ROS2 package, does not implement compensation or navigation, does not publish real robot motion commands, and does not hard-code unconfirmed K1 topics.

```text
measurement -> compensation -> navigation safety
```

Only the measurement stage is implemented here. Later compensation and navigation work must consume real measurement artifacts with environment labels, ground truth, confidence fields, and warnings. Dummy artifacts are never real K1 findings.

## Current Status

- M0-M6 completed.
- M7 in progress: Real K1 Measurement Preparation Pack.
- Real K1 ROS2 topic mapping is still TBD and must be confirmed in tomorrow's K1 ROS2 shell.
- Existing dummy raw logs, profiles, and reports validate the pipeline only.

M7 prepares:

- ROS2 availability checks
- real K1 topic discovery
- candidate topic classification
- message type inspection
- logger configuration template
- forward velocity baseline plan
- ground-truth recording template
- field-test checklist
- static visualization artifacts

## Repository Boundary

The repository remains a Python-based K1 velocity measurement toolkit with configs, scripts, analysis utilities, visualization artifacts, and reports. M7 does not create a full ROS2 package layout.

M7 discovery tools only run read-only ROS2 CLI checks:

- `ros2 --help`
- `ros2 topic list`
- `ros2 topic list -t`
- optional `ros2 interface show <message_type>`

They do not publish to `cmd_vel` or any motion topic. Candidate topics are heuristic keyword matches only and are not confirmed mappings.

## M7 Quick Workflow

In the real K1 ROS2 shell:

```powershell
python scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

In a development shell without ROS2:

```powershell
python scripts/validate_ros2_readonly_topics.py --print-only --output-dir outputs/ros2_readonly_validation
```

After reviewing the report, manually confirm candidate odom / IMU / battery / robot_state / command topics and fill:

```text
configs/real_k1_logger_template.yaml
```

The forward baseline keeps the original speed groups:

```text
0.1, 0.2, 0.3, 0.4 m/s
3 repeats per speed
```

## Key Artifacts

- `outputs/ros2_readonly_validation/ros2_topic_discovery_report.json`
- `outputs/ros2_readonly_validation/ros2_topic_discovery_report.md`
- `configs/real_k1_logger_template.yaml`
- `configs/forward_velocity_baseline_plan.yaml`
- `templates/ground_truth_trial_sheet.csv`
- `docs/real_k1_field_test_checklist.md`
- `docs/m7_real_k1_measurement_preparation.md`

Visualization exists only as static measurement report artifacts:

- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `trial_timeseries_plot.png`
- `drift_plot.png`

## Validation

```powershell
python -m pytest
python -m pytest tests/test_ros2_readonly_validator.py -q
python -m pytest tests/test_visualization.py -q
python -m compileall k1_measurement scripts tests
python scripts/validate_ros2_readonly_topics.py --print-only --output-dir outputs/ros2_readonly_validation
```
