# Project Status

## 当前阶段

M7: Real K1 Measurement Preparation Pack is the current milestone.

## 仓库定位

`k1_measurement_skill` 是 **K1 Velocity Measurement, Compensation, and Navigation Safety Pipeline** 的测量阶段前置模块，只负责：

```text
v_x_cmd -> v_x_actual measurement
```

本仓库不实现 velocity compensation、navigation、真实机器人运动执行或完整 ROS2 package layout。

## Completed Milestones

- [x] M0 project structure
- [x] M1 interface contracts
- [x] M2 metrics core
- [x] M3 dummy data pipeline
- [x] M4 ROS2 topic discovery / logger skeleton
- [x] M5 dry-run forward baseline trial manager
- [x] M6 measurement report generator

## Current Milestone

- [x] M7 ROS2 availability check
- [x] M7 read-only topic discovery report
- [x] M7 candidate topic classification
- [x] M7 optional message interface inspection
- [x] M7 logger configuration template
- [x] M7 forward velocity baseline plan
- [x] M7 ground-truth trial sheet template
- [x] M7 field-test checklist and workflow documentation
- [x] M7 static visualization support

## Pending Real K1 Validation

真实 K1 validation 仍需等明天机器测试完成：

- real odom topic TBD
- real IMU topic TBD
- real battery topic TBD
- real robot_state topic TBD
- real command topic TBD
- ground-truth method TBD
- test field distance TBD

Dummy artifacts remain pipeline-validation outputs only and must not be presented as real K1 findings.
