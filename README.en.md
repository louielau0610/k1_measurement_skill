# K1 Velocity Measurement Toolkit

## M25 Active Scope: Full-Range Velocity Profiling

M25 refocuses the active repository on longitudinal command velocity versus measured actual velocity across the complete configured valid command-speed domain, excluding the deadzone by an explicit engineering boundary. The active domain is `[0.35, 0.60] m/s` for the current K1 experiment configuration; `safe_command_speed_max` is confirmed at `0.6 m/s` via operator confirmation. No command above `0.6 m/s` is permitted.

The 0.50-0.60 m/s region is the dense high-priority evaluation region for the current K1 config. Deadzone research has been abandoned for the active roadmap, and yaw drift / yaw compensation work is paused and removed from active M25 objectives. M25 establishes the measurement/profile foundation only; it does not claim compensation success or validate an inverse compensator.

Key M25 artifacts:

- `docs/m25_full_range_velocity_profiling.md`
- `docs/m25_repository_cleanup_manifest.md`
- `configs/m25_full_range_velocity_profile_template.yaml`
- `k1_measurement/full_range_velocity_profile.py`
- `scripts/plan_full_range_velocity_profile.py`

Next milestones: M26 compares full-range monotonic response models, M27 implements or finalizes inverse velocity compensation, and M28 performs full-range direct-vs-compensated real-robot validation.

## M25-R Readiness

M25-R adds safe-speed operator confirmation, real-collection preflight validation, blocked exploration/formal collection packages, and an exploration-to-formal gate.

## M25-T K1 SDK Motion Context

M25-T aligns the K1 preflight with the confirmed SDK command path: `booster_sdk_kPrepare_kWalking_Move`. The current adapter validates the fixed sequence `kPrepare -> kWalking -> Move(vx, 0.0, 0.0)`. `control_mode` and `gait_mode` are optional metadata for this K1 adapter, not mandatory execution blockers, and `kWalking` is documented only as part of the fixed validated sequence.

The authoritative safety limit is loaded from `configs/m25_k1_safe_speed_operator_confirmation.yaml`, with `safe_command_speed_max: 0.6` for the current K1 experiment configuration. Exploration is package-ready with 12 planned trials; formal collection remains blocked until exploration review is approved.

## M25-S K1 Safe-Speed Integration

M25-S integrates the confirmed K1 safe forward command-speed maximum of `0.6 m/s` into the M25/M25-R real-collection workflow. The current exploration plan has 12 trials (4 command points x 3 repeats) and the formal plan has 30 trials (6 x 5). Safe speed is resolved through validated configuration provenance.

Start here:

- `docs/m25r_real_data_collection_readiness.md`
- `docs/m25s_k1_safe_speed_integration.md`
- `configs/m25_k1_safe_speed_operator_confirmation.yaml`
- `configs/m25_k1_s2_real_collection.yaml`
- `configs/m25_real_collection_preflight_template.yaml`

M26 response-model fitting must not proceed until real formal profile data exist.

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
- M7 complete: Real K1 Measurement Preparation Pack.
- M8 current milestone: Real K1 Field Logging and Forward Baseline Execution Support.
- Real K1 ROS2 topic mapping is still TBD and must be confirmed in tomorrow's K1 ROS2 shell.
- Existing dummy raw logs, profiles, and reports validate the pipeline only.

M8 makes the repository ready for a real field logging workflow:

- Create a real test session directory.
- Validate manually confirmed topic mappings.
- Launch read-only multi-topic logging with `ros2 bag record`.
- Record ground-truth trial metadata.
- Generate a session manifest.
- Normalize exported CSV logs into a measurement-pipeline compatible format when available.
- Produce or reference first real measurement artifacts and plots.

## Repository Boundary

The repository remains a Python-based K1 velocity measurement toolkit with configs, scripts, analysis utilities, visualization artifacts, and reports. M8 does not create a full ROS2 package layout.

M7/M8 tools only run read-only discovery and logging:

- `ros2 --help`
- `ros2 topic list`
- `ros2 topic list -t`
- optional `ros2 interface show <message_type>`
- `ros2 bag record -o <session_dir>/raw_ros/rosbag <confirmed topics...>`

They do not publish to `cmd_vel` or any motion topic. Candidate topics are heuristic keyword matches only and are not confirmed mappings.

## M8 Quick Workflow

Create a session:

```powershell
py scripts/create_real_k1_field_session.py --session-id 20260609_k1_forward_baseline --output-root data/real_k1_sessions
```

Run discovery in the real K1 ROS2 shell:

```powershell
py scripts/validate_ros2_readonly_topics.py --output-dir outputs/ros2_readonly_validation --include-interface-show
```

Fill and validate mapping:

```powershell
py scripts/validate_real_k1_topic_mapping.py --mapping data/real_k1_sessions/20260609_k1_forward_baseline/topic_mapping.yaml
```

Start static logger:

```powershell
py scripts/start_real_k1_field_logger.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline --duration-sec 30
```

Normalize exported CSV logs:

```powershell
py scripts/normalize_real_k1_logs.py --session-dir data/real_k1_sessions/20260609_k1_forward_baseline
```

The forward baseline keeps the original speed groups:

```text
0.1, 0.2, 0.3, 0.4 m/s
3 repeats per speed
```

## Key Artifacts

- `data/real_k1_sessions/<session_id>/session_manifest.json`
- `data/real_k1_sessions/<session_id>/topic_mapping.yaml`
- `data/real_k1_sessions/<session_id>/ground_truth_trial_sheet.csv`
- `data/real_k1_sessions/<session_id>/logger_run_summary.json`
- `data/real_k1_sessions/<session_id>/normalized/normalization_report.json`
- `data/real_k1_sessions/<session_id>/normalized/raw_measurement_log.csv`
- `docs/m8_real_k1_field_logging_workflow.md`
- `docs/real_k1_field_test_checklist.md`

Visualization exists only as static measurement report artifacts:

- `velocity_error_plot.png`
- `speed_gain_plot.png`
- `trial_timeseries_plot.png`
- `drift_plot.png`

## Validation

```powershell
py -m pytest
py -m compileall k1_measurement scripts tests
py scripts/create_real_k1_field_session.py --session-id test_m8_session --output-root outputs/m8_field_session_test
py scripts/validate_real_k1_topic_mapping.py --mapping outputs/m8_field_session_test/test_m8_session/topic_mapping.yaml
```

The default template mapping still contains `TBD`, so the mapping validator returns a controlled validation failure rather than a Python crash.
