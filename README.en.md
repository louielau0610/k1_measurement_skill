# K1 Velocity Measurement Toolkit

## M26-E Packaging and Local Release Gate

M26-E packages the hardware-free `calibration_skill` dry-run CLI as the local
`calibration-skill` Python package. It adds a console script, hermetic test
runner, local release gate, package inventory, and distribution-readiness docs.

Useful commands:

```powershell
py -3.12 -m calibration_skill.cli manifest
calibration-skill manifest
calibration-skill examples --operation dry_run_end_to_end
py -3.12 scripts/run_tests_hermetically.py -- py -3.12 -m pytest tests/ --tb=no -q
py -3.12 scripts/run_local_release_gate.py --summary outputs/engineering/m26e_release_gate_summary.json
```

M26-E is pre-release-only. It does not migrate K1, implement G1 or GO1 runtime
support, connect to hardware, open sockets, start DDS, send UDP, or import
vendor SDK runtimes.

## M26-B Unified Domain Contracts and Schemas

M26-B implements the platform-independent contract layer: pure domain value
objects, invariant validation, error taxonomy, capability and maturity models,
hardware-facing port interfaces, deterministic JSON codecs, and versioned
JSON Schemas.

The new `calibration_skill` package (`domain/`, `ports/`, `schemas/`) is
independently importable and testable without any vendor SDK installed.

Key M26-B artifacts:

- `calibration_skill/domain/` — Pure platform-independent value objects
- `calibration_skill/ports/` — Abstract Protocol interfaces
- `calibration_skill/schemas/v1/` — 13 versioned JSON Schemas (v1.0.0)
- `docs/engineering/m26b_error_taxonomy.md` — Error taxonomy
- `outputs/engineering/m26b_readiness.json` — Readiness (ImplementationMaturity model)
- `scripts/validate_engineering_artifacts.py` — Engineering artifact validator

**Important**: M26-B implements no adapters. The existing K1 adapter has not
been migrated. G1/GO1 adapters are not implemented. No platform adapter is
operational under the new architecture.

## M26-A Engineering Program Reset and Multi-Platform Architecture Freeze

M26-A pauses all non-engineering experimental branches of work and reframes the
repository as an **engineering-grade, agent-callable legged robot velocity
calibration skill** with explicitly scoped target platforms:

1. **Booster K1** — biped humanoid (hardware-validated reference)
2. **Unitree G1** — biped humanoid (scaffold only)
3. **Unitree GO1** — quadruped (scaffold only)

M26-A is documentation, inventory, architecture, and migration planning only.
It does **not** connect to any robot, send motion commands, install SDKs,
perform physical tests, alter the gold calibration profile, or change
compensation model behavior.

Key engineering documents:

- `docs/engineering/m26a_program_reset.md` — Program reset declaration
- `docs/engineering/current_repository_inventory.md` — Repository inventory
- `docs/engineering/current_dependency_map.md` — Current dependency map
- `docs/engineering/target_multi_platform_skill_architecture.md` — Target architecture
- `docs/engineering/target_end_to_end_use_chain.md` — End-to-end use chain
- `docs/engineering/preliminary_core_contracts.md` — Core contract specifications
- `docs/engineering/platform_capability_matrix.md` — Platform capability matrix
- `docs/engineering/multi_platform_migration_plan.md` — Phased migration plan
- `docs/adr/` — Architecture Decision Records (ADR-0001 through ADR-0005)
- `outputs/engineering/m26a_repository_audit.json` — Machine-readable audit
- `outputs/engineering/m26a_platform_capability_matrix.json` — Capability matrix JSON
- `outputs/engineering/m26a_readiness.json` — Engineering readiness tracker

**Paused work**: M25 data collection, M26-M28 modeling/compensation/validation,
yaw drift research, deadzone research, paper work (P-series), online yaw
adjustment, physical compensation experiments.

**G1/GO1 readiness claim**: No G1 or GO1 runtime support is claimed before
physical acceptance milestones are completed.

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
# M26-D Agent-Callable Dry-Run CLI

M26-D adds a deterministic JSON CLI for agents to call the mock-only dry-run
skill:

```powershell
py -3.12 -m calibration_skill.cli manifest
py -3.12 -m calibration_skill.cli operations
py -3.12 -m calibration_skill.cli validate --input examples/calibration_skill/dry_run_end_to_end.mock.json
py -3.12 -m calibration_skill.cli invoke --input examples/calibration_skill/dry_run_end_to_end.mock.json --pretty
```

The CLI supports stdin/stdout and file input/output, returns
`skill_response.schema.json`-compatible responses, and rejects real platforms.
M26-D remains mock-only and dry-run-only; no K1/G1/GO1 runtime support or
hardware verification is claimed.

# M26-C Mock Adapter and Dry-Run Skill Service

M26-C adds the first executable hardware-free layer above the M26-B contracts.
It includes a mock-only adapter registry, deterministic `MockRobotAdapter`,
dry-run `SkillService`, and mock end-to-end operation with in-memory audit
generation.

Key M26-C artifacts:

- `calibration_skill/adapters/registry.py`
- `calibration_skill/adapters/mock.py`
- `calibration_skill/skill/service.py`
- `calibration_skill/runtime/dry_run.py`
- `docs/engineering/m26c_mock_adapter_and_skill_service.md`
- `docs/engineering/m26c_dry_run_end_to_end.md`
- `outputs/engineering/m26c_readiness.json`

M26-C is mock-only. It does not migrate K1, implement G1 or GO1, connect to
hardware, open sockets, start DDS, send UDP, or import vendor SDK runtimes.
