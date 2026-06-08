# TODO

## M0-M6

- [x] M0 project structure
- [x] M1 interface contracts
- [x] M2 metrics core
- [x] M3 dummy data pipeline
- [x] M4 ROS2 topic discovery / logger skeleton
- [x] M5 dry-run forward baseline trial manager
- [x] M6 measurement report generator

## M7 Real K1 Measurement Preparation

- [x] Add structured ROS2 availability check.
- [x] Add read-only topic discovery report generation.
- [x] Add candidate topic classification.
- [x] Add optional message type inspection.
- [x] Add real K1 logger config template with TBD topics.
- [x] Add forward velocity baseline plan using original velocity groups.
- [x] Add ground-truth trial sheet template.
- [x] Add field-test checklist.
- [x] Add static measurement visualization support.

## Next Step On Real K1

- [ ] Run M7 in the real K1 ROS2 shell.
- [ ] Confirm candidate odom / IMU / battery / robot_state / command topics.
- [ ] Fill `configs/real_k1_logger_template.yaml`.
- [ ] Run static logging test.
- [ ] Check timestamp, odom, IMU, robot mode, and battery fields.
- [ ] Run one smoke forward trial.
- [ ] Run full forward velocity baseline.
- [ ] Generate first real measurement report and plots.

## Still Do Not Implement

- [ ] Do not implement velocity compensation in this repository.
- [ ] Do not implement navigation.
- [ ] Do not publish robot movement commands.
- [ ] Do not treat dummy artifacts as real K1 findings.
