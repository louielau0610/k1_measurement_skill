# TODO

## Completed

- [x] M0 project structure
- [x] M1 interface contracts
- [x] M2 metrics core
- [x] M3 dummy data pipeline
- [x] M4 ROS2 topic discovery / logger skeleton
- [x] M5 dry-run forward baseline trial manager
- [x] M6 measurement report generator
- [x] M7 real K1 measurement preparation pack
- [x] M8 real K1 field logging workflow support
- [x] M13 research-grade velocity response foundation
- [x] M13.1 harden velocity response schema validation
- [x] M14 construct velocity response dataset v1

## Research Foundation Follow-Up

- [ ] Use `configs/velocity_response_dataset_schema_v1.json` when preparing real velocity response datasets.
- [ ] Validate schema changes with `scripts/validate_velocity_response_dataset_schema.py`.
- [ ] Keep `battery_state` optional.
- [ ] Keep `remote_controller_state` permanently out of scope.
- [ ] Start literature review only after the project explicitly enters the next research phase.

## Next Research Milestone

- [ ] M15 baseline response models.
- [ ] M16 uncertainty-aware response model.
- [ ] M17 navigation-aware risk mapping.
- [ ] M18 experimental evaluation and paper-style report.
- [ ] Do not turn M15-M18 into compensation or navigation control unless explicitly re-scoped.

## Next Step On Real K1

- [ ] Push M7/M8 commits if the repository should be shared before the field test.
- [ ] Run M7 discovery on the real K1 ROS2 shell.
- [ ] Fill `topic_mapping.yaml` with confirmed real topics and field names.
- [ ] Run `validate_real_k1_topic_mapping.py`.
- [ ] Run M8 field logger for static logging.
- [ ] Inspect raw ROS logs.
- [ ] Run one smoke forward trial.
- [ ] Run full forward velocity baseline.
- [ ] Normalize logs.
- [ ] Generate first real measurement report and plots.

## Still Do Not Implement

- [ ] Do not implement velocity compensation in this repository.
- [ ] Do not implement navigation.
- [ ] Do not publish robot movement commands.
- [ ] Do not hard-code unconfirmed K1 topics.
- [ ] Do not treat dummy artifacts as real K1 findings.
- [ ] Do not claim publication readiness from M13 artifacts.
