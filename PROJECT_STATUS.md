# Project Status

## 当前阶段

M8: Real K1 Field Logging and Forward Baseline Execution Support is the current milestone.

## 仓库定位

`k1_measurement_skill` 是 **K1 Velocity Measurement, Compensation, and Navigation Safety Pipeline** 的测量阶段前置模块，只负责：

```text
v_x_cmd -> v_x_actual measurement
```

本仓库不实现 velocity compensation、navigation、真实机器人运动执行脚本或完整 ROS2 package layout。

## Completed Milestones

- [x] M0 project structure
- [x] M1 interface contracts
- [x] M2 metrics core
- [x] M3 dummy data pipeline
- [x] M4 ROS2 topic discovery / logger skeleton
- [x] M5 dry-run forward baseline trial manager
- [x] M6 measurement report generator
- [x] M7 real K1 measurement preparation pack

M7 commit: `0e8db1131b152617cd9f86d42d61c96d473d7996`

## Current Milestone

- [x] M8 field session directory creation
- [x] M8 session manifest generation
- [x] M8 configurable real K1 topic mapping template
- [x] M8 topic mapping validator
- [x] M8 read-only rosbag logging launcher
- [x] M8 ground-truth sheet validation helpers
- [x] M8 mapping-driven real log normalizer
- [x] M8 workflow documentation and checklist updates
- [x] M13 research-grade velocity response foundation

## M13 Research Foundation

M13 adds research problem framing for:

```text
v_actual = f(v_cmd, environment, robot_state)
```

M13 also adds the Chapter 2 velocity response modeling plan, dataset schema v1, schema validation CLI, tests, and milestone summary JSON. It does not start literature review, P1, full paper drafting, compensation, inverse command mapping, navigation control, or safe command adapter implementation.

## M13.1 Schema Hardening

M13.1 hardens reusable velocity response schema validation and adds the Measurement v0 to velocity response schema v1 bridge. It does not implement M14, compensation, inverse command mapping, navigation control, or safe command adapter logic.

Preserved readiness flags:

- `measurement_v0_complete=true`
- `real_k1_profile_available=true`
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M14 Velocity Response Dataset v1

M14 constructs `outputs/research_datasets/velocity_response_dataset_v1.json` from Measurement v0 artifacts. M14 is dataset construction only: it does not implement baseline modeling, uncertainty-aware modeling, compensation, inverse command mapping, navigation control, or safe command adapter logic.

Preserved readiness flags:

- `measurement_v0_complete=true`
- `real_k1_profile_available=true`
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M15R Uncertainty-Aware Response Model Foundation

M15R implements the conservative response model foundation. The old baseline-only M15 is compressed into minimal baseline hooks for future paper comparison. The proposed hybrid model outputs uncertainty/confidence labels, not calibrated probabilities, and M15R does not prove performance superiority.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M16 Navigation-Aware Risk Mapping

M16 implements offline navigation-aware reliability and risk mapping from M15R predictions. It does not implement real navigation control and does not prove navigation performance improvement.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M17 Pipeline Evaluation Report

M17 consolidates M13-M16 outputs into a paper-style evaluation package with artifact table, supported claims, non-claims, limitations, and next experiments. M17 does not prove navigation performance improvement.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P1 Seed Literature Matrix

P1 creates seed literature search artifacts, literature matrix v1, citation verification report, rejected-source log, seed BibTeX, paper notes, and conservative candidate gaps. P1 is literature/positioning work only: it does not implement engineering functionality, does not claim novelty, does not write a full related-work section, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P2 Gap Analysis and Contribution Positioning

P2 analyzes P1 literature clusters against M13-M17 project artifacts and produces gap analysis, related-work positioning, contribution candidates, claim-upgrade rules, and paper framing options. P2 does not implement engineering functionality, does not claim final novelty, does not claim performance superiority, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M18 Paper Method Skeleton and Claim Audit

M18 creates paper method skeleton, experiments skeleton, figure specs, artifact/evidence tables, manuscript scaffold, and strict claim audit. M18 does not implement engineering functionality, does not write a full paper draft, does not claim final novelty, does not claim performance superiority, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## Pending Real K1 Validation

真实 K1 validation 仍需等明天机器测试完成：

- real odom topic TBD
- real IMU topic TBD
- real battery topic TBD
- real robot_state topic TBD
- real command topic TBD
- real message field names TBD
- real timestamp fields TBD
- robot mode / gait names TBD
- ground-truth method TBD
- test field distance TBD

Dummy artifacts remain pipeline-validation outputs only and must not be presented as real K1 findings.

## P3 Related Work Draft v1

P3 creates a citation-safe Related Work draft v1 that synthesizes P1 verified/partially verified literature, follows P2 cluster positioning, and respects M18 claim boundaries. P3 does not implement engineering functionality, does not write a full paper, does not claim final novelty, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P4 Introduction and Problem Statement Draft v1

P4 creates a citation-safe Introduction draft, formal Problem Statement, and title/contribution options. P4 synthesizes P1-P3 literature and M18 artifacts. P4 does not implement engineering functionality, does not write a final abstract, does not claim final novelty, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`
