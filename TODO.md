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
- [x] M15R uncertainty-aware response model foundation with minimal baseline hooks
- [x] M16 navigation-aware reliability / risk mapping
- [x] M17 pipeline evaluation and paper-style report
- [x] P1 seed literature search and literature matrix v1
- [x] P2 gap analysis and contribution positioning
- [x] M18 paper method skeleton, figures, and claim audit

## Research Foundation Follow-Up

- [ ] Use `configs/velocity_response_dataset_schema_v1.json` when preparing real velocity response datasets.
- [ ] Validate schema changes with `scripts/validate_velocity_response_dataset_schema.py`.
- [ ] Keep `battery_state` optional.
- [ ] Keep `remote_controller_state` permanently out of scope.
- [x] Start seed literature review only after M17 completion.

## Next Research Milestone

- [x] P3 related work section draft v1 (citation-safe, P1/P2 synthesized).


- [x] P3 related work section draft after M18 or after additional literature.
- [ ] P4 introduction/problem statement draft.
- [ ] M19 future experiment protocol and figure-generation assets.
- [ ] Future experimental expansion before compensation or safe command adapter work.

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
- [ ] Do not claim publication readiness from M13-P1 artifacts.
- [ ] Do not claim novelty from P1 seed literature search alone.
- [ ] Do not claim novelty or performance superiority from P2 positioning alone.
- [ ] Do not treat M18 scaffold files as a full paper draft.
