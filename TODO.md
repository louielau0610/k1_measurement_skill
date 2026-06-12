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
- [x] P4 introduction/problem statement draft.
- [x] M19 future experiment protocol and figure-generation assets.
- [x] M19R-B measurement completion pack: replacement trial plan, annotation template, annotation protocol, and annotation QC.
- [x] Complete M19 replacement trials for the 5 incomplete surface-speed cells.
- [x] Refresh M19 valid-only annotation template after replacements.
- [x] Add M19 annotation intake validator for filled measurement CSVs.
- [x] Add M19R-C SDK state-source discovery, smoke logging, and SDK-log extraction scaffold.
- [x] Add M19R-C ROS2 `/odometer_state` logger, smoke runner, and odometer-log extractor scaffold.
- [x] Add full M19C 72-trial ROS2 odometer runner, extractor, QC, and protocol.
- [x] M20 cross-platform calibration core scaffold.
- [x] M21-A measurement module consolidation.
- [x] M21-B Booster K1 measurement reference implementation hardening.
- [x] M21-C measurement data contract definition and K1 contract compliance.
- [x] M21-D measurement module closure and Step 2 transition plan.
- [x] M22-A velocity compensation principle research and first-method decision framework.
- [x] M22-B velocity compensation algorithm specification (Conservative Monotonic Segment Inverse Lookup).
- [x] M22-C offline velocity compensator prototype with novelty/positioning audit.
- [x] M22-D offline compensator verification and edge-case audit.
- [x] M23-A K1 physical compensation experiment design.
- [x] M23-B K1 physical compensation execution pack.
- [x] M23-B hotfix2 synchronized logger + SDK subprocess orchestration.
- [x] M23-A hotfix executable compensated trial plan.
- [x] M23-C analyze K1 S2 physical compensation before/after results.
- [x] M23-D negative result diagnosis and revised compensator plan.
- [x] M23-E revised offline compensator with identity fallback and benefit gate.
- [x] M23-F revised offline audit and second K1 validation readiness assessment.
- [x] M24-A S2 current-condition profile refresh design.
- [x] M24-B S2 profile refresh execution pack.
- [x] M24-C analyze clean S2 profile refresh results.
- [x] M24-D response consistency audit and profile adoption boundary.
- [ ] Run M24-B direct-only S2 current-condition profile refresh on Booster K1.
- [x] Analyze M24-C old-vs-current S2 profile mismatch before any new compensation validation.
- [ ] Collect more controlled S2 refresh data or diagnose M24-B near-zero extracted velocity before compensation validation.
- [ ] Audit M24-B/M24-C extraction and odometer source before adopting any current S2 profile.
- [ ] Revise M22-C compensator policy after M23-C negative physical result.
- [ ] Run SDK state discovery on the physical K1 shell with Booster SDK sourced.
- [ ] Source `/opt/booster/BoosterRos2Interface/install/setup.bash` on K1 and run ROS2 odometer standing smoke logger.
- [ ] Confirm `/odometer_state` publishes timestamped `x`, `y`, and `theta` at usable frequency before full M19C measurement run.
- [ ] Run three ROS2 odometer dynamic smoke trials and verify nonzero extracted velocity before full M19C measurement run.
- [ ] Run full M19C ROS2 odometer measurement by surface: S1, then S2, then S3.
- [ ] Extract `m19c_extracted_measurements.csv` and pass M19C measurement-run QC before empirical analysis.
- [x] Ingest completed M19C 72-trial K1 odometer dataset.
- [x] Generate M19C empirical response statistics, region classification, and `k1_gold_profile_v1`.
- [x] M20 Cross-Platform Calibration Skill Core: common command adapter, state logger, measurement schema, and Booster K1 / Unitree G1 / Unitree GO1 adapters.
- [x] M21-A Measurement Module Consolidation: module boundary, pipeline abstraction, K1 reference manifest, status CLI, and manifest validation CLI.
- [x] Close Measurement Module v1 review before starting velocity compensation implementation.
- [x] Study the velocity compensation principle after measurement module closure.
- [x] M22-B specify the offline velocity compensation algorithm without robot execution.
- [x] Implement the first dry-run Booster K1 compensator only after M22-B specification is reviewed.
- [ ] M22-D run offline compensator verification and edge-case audit.
- [ ] Reproduce and experimentally validate the velocity compensator on Booster K1 before any GO1/G1 generalization.
- [ ] Add real Unitree G1 state-source discovery before enabling any G1 measurement extraction.
- [ ] Add real Unitree GO1 state-source discovery before enabling any GO1 measurement extraction.
- [ ] Keep paper updates minimal unless directly useful for the calibration skill.
- [ ] Fill M19 valid-only measurement annotations from real velocity/yaw evidence only.
- [ ] Re-run M19R empirical analysis only after actual velocity and yaw drift annotations pass QC.

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
- [ ] Do not treat M19R-B pending annotation rows as empirical measurements.
- [ ] Do not treat M19R-C valid-only pending annotation rows as empirical measurements.
- [ ] Do not compute M19 empirical response statistics until annotation intake validation confirms complete real measurements.
- [ ] Do not run the full M19C measurement protocol until ROS2 odometer standing and dynamic smoke logs pass.
- [ ] Do not claim Unitree G1 or GO1 results before real or explicitly simulated adapter evidence exists.
- [ ] Do not treat K1 gold profile as cross-robot validation.
- [ ] Do not create hardware command remapping or compensation execution before Step 3 physical validation planning.
- [ ] Do not claim K1 compensation validation before Step 3 physical compensated trials.
- [ ] Do not overwrite `k1_gold_profile_v1` without a versioned profile-refresh artifact.
- [ ] Do not run a second K1 compensation experiment before the S2 current-condition profile refresh is analyzed.
- [ ] Do not treat M24-B execution-pack readiness as a completed physical profile refresh.
- [ ] Do not treat `m24c_s2_current_profile_candidate.json` as an adopted gold profile.
- [ ] Do not run a second compensation validation while M24-D adoption decision is `investigate_extraction_before_profile_decision`.
- [ ] Do not claim publication readiness from M13-P1 artifacts.
- [ ] Do not claim novelty from P1 seed literature search alone.
- [ ] Do not claim novelty or performance superiority from P2 positioning alone.
- [ ] Do not treat M18 scaffold files as a full paper draft.
