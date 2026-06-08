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
