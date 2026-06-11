# Project Status

## 当前阶段

**Step 1 (Measurement Module) is complete.** Step 2 (Velocity Compensation Principle Research) is the next phase.

## 仓库定位

`k1_measurement_skill` 是 **K1 Velocity Measurement, Compensation, and Navigation Safety Pipeline** 的测量阶段前置模块，只负责：

```text
v_x_cmd -> v_x_actual measurement
```

本仓库不实现 velocity compensation、navigation、真实机器人运动执行脚本或完整 ROS2 package layout。

## Step 1: Measurement Module — COMPLETE

Step 1 formally closed with M21-D. All milestones M19C-E through M21-D are complete and validated.

- `measurement_module_v1_status = "complete"`
- `measurement_module_v1_complete = true`
- `booster_k1_reference_ready = true`
- `measurement_contract_v1_ready = true`
- `velocity_compensation_ready = false`
- `next_phase = "velocity_compensation_principle_research"`

Closure artifacts:
- `docs/measurement_module_v1_closure.md`
- `outputs/measurement_v1/measurement_module_v1_closure_summary.json`
- `outputs/measurement_v1/measurement_module_v1_closure_report.md`
- `docs/step2_velocity_compensation_research_plan.md`

## Step 2: Velocity Compensation Principle Research — STARTED

M22-A begins Step 2 as a research/design-only milestone. It documents the feedforward inverse-model compensation principle, compares inverse mapping options, defines feasibility statuses, and recommends the first implementation direction for M22-B.

M22-A does NOT implement a compensator, inverse response model, command remapping CLI, robot execution path, K1 compensation experiment, GO1/G1 validation, or compensation readiness claim.

Current Step 2 flags:

- `velocity_compensation_principle_research_started=true`
- `recommended_first_method=conservative_piecewise_linear_inverse_mapping`
- `implementation_ready=false`
- `velocity_compensation_ready=false`
- `k1_compensation_validated=false`
- `unitree_go1_measurement_ready=false`
- `unitree_g1_measurement_ready=false`
- `next_milestone=M22-B velocity compensation algorithm specification`

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
- [x] M20 cross-platform calibration skill core scaffold
- [x] M21-A measurement module consolidation
- [x] M22-A velocity compensation principle research

## M20 Cross-Platform Calibration Core

M20 adds `calibration_core/` and `platforms/` as a reusable calibration skill layer. Booster K1 is registered as the only `hardware_validated_reference`, using the completed M19C ROS2 odometer profile. Unitree G1 and Unitree GO1 are scaffold-only entries with no hardware access, no extracted measurements, and no validation claims.

Readiness flags:

- `booster_k1_hardware_validated_reference=true`
- `unitree_g1_hardware_validated_reference=false`
- `unitree_go1_hardware_validated_reference=false`
- `cross_platform_empirical_validation=false`
- `compensation_ready=false`
- `navigation_control_ready=false`

## M21-A Measurement Module Consolidation

M21-A consolidates the measurement module as Step 1 of the corrected roadmap. It adds `docs/measurement_module_v1.md`, a hardware-optional measurement pipeline abstraction, a Measurement Module v1 manifest schema, and a Booster K1 reference manifest under `outputs/measurement_v1/`.

K1 remains the only validated measurement reference. GO1/G1 remain future platforms with no measurement readiness or hardware validation claim. Velocity compensation is the next research phase after measurement module closure; it is not implemented or claimed ready in M21-A.

Readiness flags:

- `measurement_module_v1_status=consolidated_reference_ready`
- `booster_k1_reference_ready=true`
- `unitree_go1_measurement_ready=false`
- `unitree_g1_measurement_ready=false`
- `velocity_compensation_ready=false`

## M21-B Booster K1 Measurement Reference Hardening

M21-B hardens Booster K1 as the **first hardened measurement reference implementation**. It adds a standardized split-process measurement workflow, session management, extraction, QC, and CLI tools under `platforms/booster_k1/` and `scripts/`.

Key additions:

- **Split-process design**: SDK command process isolated from ROS2 logger process.
- **Dry-run by default**: No hardware movement without explicit `--execute`.
- **Per-trial permit mode**: Each trial requires operator confirmation.
- **Standard session layout**: `data/measurement_sessions/booster_k1/<session_id>/`
- **Unified CLIs**: `run_booster_k1_measurement.py`, `extract_booster_k1_measurements.py`, `qc_booster_k1_measurement_session.py`
- **Fixture/replay test mode**: `tests/fixtures/` for offline testing without hardware.
- **Updated manifest**: `outputs/measurement_v1/booster_k1_reference_manifest.md` includes M21-B paths.

M21-B does NOT:
- Implement velocity compensation
- Add command remapping
- Claim compensation readiness
- Claim GO1/G1 hardware validation
- Overwrite M19C-E gold artifacts

Readiness flags:

- `measurement_module_v1_status=consolidated_reference_ready`
- `booster_k1_reference_ready=true`
- `unitree_go1_measurement_ready=false`
- `unitree_g1_measurement_ready=false`
- `velocity_compensation_ready=false`

## M21-C Measurement Data Contract

M21-C defines the formal cross-platform measurement data contract (`measurement_v1.0`) that all platforms must satisfy before velocity compensation. It adds:

- **Contract module**: `calibration_core/measurement_contract.py` with trial (27 fields), aggregate (25 fields), and session metadata (22 fields) schemas.
- **Legacy mapping**: `calibration_core/measurement_contract_mapping.py` maps M19C field names to contract names.
- **Conversion CLI**: `scripts/convert_measurements_to_contract.py` — converted all 72 K1 rows to contract format (all valid).
- **Validation CLI**: `scripts/validate_measurement_contract.py` — validates CSVs, metadata, and session directories.
- **Contract artifacts**: JSON schema, markdown documentation, K1 contract CSV, validation report.
- **Coordinate convention**: body x forward, y left, z up; yaw in degrees for export.

M21-C does NOT:
- Implement velocity compensation
- Add command remapping
- Claim compensation readiness
- Claim GO1/G1 hardware validation
- Overwrite M19C-E gold artifacts

Readiness flags:

- `measurement_module_v1_status=consolidated_reference_ready`
- `booster_k1_reference_ready=true`
- `measurement_contract_active=true` (K1 only)
- `unitree_go1_measurement_ready=false`
- `unitree_g1_measurement_ready=false`
- `velocity_compensation_ready=false`

## M21-D Measurement Module Closure

M21-D formally closes Step 1 (Measurement Module). It adds:

- **Closure summary**: `docs/measurement_module_v1_closure.md` and `outputs/measurement_v1/measurement_module_v1_closure_summary.json`
- **Closure report**: `outputs/measurement_v1/measurement_module_v1_closure_report.md`
- **Updated status**: `outputs/measurement_v1/measurement_module_status.json` — status changed to `complete`
- **Closure validation CLI**: `scripts/validate_measurement_module_closure.py`
- **Step 2 transition plan**: `docs/step2_velocity_compensation_research_plan.md` (planning only, no implementation)

M21-D does NOT:
- Implement velocity compensation
- Add inverse response modeling
- Add command remapping
- Claim compensation readiness
- Claim GO1/G1 hardware validation

Readiness flags:

- `measurement_module_v1_status=complete`
- `measurement_module_v1_complete=true`
- `booster_k1_reference_ready=true`
- `measurement_contract_v1_ready=true`
- `velocity_compensation_ready=false`
- `unitree_go1_measurement_ready=false`
- `unitree_g1_measurement_ready=false`
- `next_phase=velocity_compensation_principle_research`

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

## P5 Method Section Draft v1

P5 creates an academic Method draft v1 from M13-M18 artifacts with formal notation, algorithmic contracts, artifact traceability, and claim audit. P5 does not implement engineering functionality, does not claim novelty, and does not claim performance superiority or publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P6 Experiments and Evaluation Draft v1

P6 creates an academic Experiments/Evaluation draft v1 reporting structural evaluation from current artifacts. P6 covers 5 evaluation questions, dataset/model/risk-map evidence, current metrics, missing evidence, and future experiment protocol. P6 does not implement engineering functionality, does not claim navigation performance, and does not claim novelty or publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P7 Discussion and Limitations Draft v1

P7 creates an academic Discussion and Limitations draft v1 interpreting the pipeline, its limitations, and future work. P7 adds a claim-upgrade requirements table documenting evidence needed for each claim type. P7 does not implement engineering functionality, does not write a final conclusion, and does not claim final novelty or publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P8 Manuscript Assembly v0

P8 assembles all P3-P7 section drafts into a manuscript v0, performs a cross-section consistency audit, and creates manuscript-level claim audit and status tables. P8 does not implement engineering functionality, does not write final abstract or conclusion, and does not claim publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P9 Conclusion Draft v1

P9 creates an academic Conclusion draft v1 completing the first complete manuscript narrative (except final abstract). P9 does not implement engineering functionality, does not write the abstract, and does not claim final novelty or publication readiness.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P10 Abstract Draft v1

P10 creates an academic Abstract draft v1 (193 words primary, with short/extended variants), completing the first full manuscript narrative from Abstract through Conclusion. P10 does not implement engineering functionality and does not claim final novelty or publication readiness.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P11 Full Manuscript Claim Audit

P11 performs a comprehensive full-manuscript claim audit with 19 claims classified, 12 numeric items verified, 16 citation keys audited, and a prioritized revision plan. P11 finds 0 blocking issues and 6 high-severity evidence gaps (correctly documented). Submission readiness: not_submission_ready. P11 does not implement engineering functionality and does not write new manuscript sections.

Readiness flags remain:

- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P12 Manuscript Revision v1

P12 creates manuscript v1 assembly, revision changelog, post-revision consistency check, and resolves 5/8 Codex-editable P11 audit issues. P12 does not add new scientific results, does not claim publication readiness, and preserves all evidence gaps.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P13 Reference and BibTeX Cleanup

P13 resolves all 8 matrix-only BibTeX entries from verified P1 metadata, strengthening seed_references.bib to 16 entries. P13 adds 3 new manuscript citations (FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025) to Related Work §4/§5. P13 does not add new experimental evidence and does not claim publication readiness.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M19 Figure Rendering and Table Assets

M19 generates Mermaid (.mmd) figure sources for the method pipeline and evidence chain figures using `scripts/generate_m19_figures.py`. Both figures respect claim boundaries with explicit prohibited execution path and claim category markings. Final SVG rendering pending external Mermaid CLI or mermaid.live.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M19.1 Figure/Table Caption and Integration Assets

M19.1 completes missing figure/table caption packs, main and appendix table packs, evidence-gap figure spec, integration plan, and figure/table claim audit. M19.1 does not add new experimental evidence, does not claim publication readiness, and preserves all evidence gaps.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## P14 Manuscript v2 Polish

P14 creates polished manuscript v2 assembly with integrated figure/table references, main/appendix asset separation, and cross-referenced caption packs. P14 does not add new experimental evidence, does not claim publication readiness, and preserves all evidence gaps.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`

## M20 Future Experiment Protocol

M20 designs a future experiment protocol for real navigation outcome evaluation: 4 experiment tiers, 35 defined metrics, claim-upgrade evidence matrix, JSON schema, examples, validator, and test suite. M20 is protocol-only — no experiments have been executed. M20 does not claim publication readiness.

Readiness flags remain:
- `compensation_ready=false`
- `navigation_warning_ready=true`
- `safe_command_adapter_ready=false`
M21.1 closes M21 completion gaps (navigation task template, validator/test updates, cross-references). Pack-only.
M21.1 merged. P15 planning-only: 9 docs created, 0 .tex, 0 PDF, not submission ready.
P16 creates non-final LaTeX scaffold (17 files). No PDF, no submission package, not submission ready.
P16.1 evidence patch: evidence_table updated, P16 summary consistency fixed, git diff --check passed.
P17: 3 LaTeX tables created, figures copied (not rendered). No PDF. Not submission ready.
P18: LaTeX tools detected. Compile attempted. Underscore escaping in filenames blocks full build (documented). Not submission ready.
P19: Underscore escaping fixed. Smoke build PDF built (3pp, 95KB). Not submission ready.
M19-A: Repeated validation infrastructure ready. Pending-data mode (no real repeated logs). 209/209 tests pass.

## M19R-B Measurement Completion Pack

M19R-B creates the measurement completion pack after blocker-aware M19R ingestion. It generates the exact replacement-trial plan for incomplete surface-speed cells, a blank measurement annotation template, a measurement annotation protocol, and annotation QC tooling.

Empirical response analysis remains blocked until real `measured_actual_velocity` and `yaw_drift_statistic` values are filled from acceptable evidence sources. Replacement trials are required because M19R found only 67 execution-valid trials after QC, with 5 invalid/debug rows excluded. No response-model validation, risk-map validation, navigation improvement claim, compensation claim, or cross-robot generalization claim is added by M19R-B.

## M19R-C Prep Valid Annotation Template

M19R-C-prep refreshes the annotation package after replacement trial execution. The updated `m19_trial_records.csv` contains 77 rows: 72 execution-valid formal trials, 5 invalid/debug rows, and 5 valid replacement rows. All 24 surface-speed cells now have exactly 3 execution-valid trials, and `m19_valid_trial_measurement_annotation_template.csv` is ready for manual, video-assisted, or log-derived measurement annotation.

Empirical analysis remains blocked because `measured_actual_velocity` and `yaw_drift_statistic` are still blank. M19R-C-prep does not compute response statistics, generate response plots, validate the risk map, claim navigation improvement, or add cross-robot generalization.

## M19R-C Annotation Intake Validation

M19R-C annotation intake validation adds a strict pre-analysis validator for filled measurement annotation CSV files. It verifies the exact 72 expected valid trial IDs, rejects invalid/debug or duplicate trial IDs, checks required annotation fields and quality flags, and detects placeholder/fabricated tokens where possible.

The current valid-only template passes intake validation with 72 pending rows, 5 replacement rows, and 0 issues. No empirical statistics are computed, and empirical response analysis remains blocked until real `measured_actual_velocity` and `yaw_drift_statistic` values are filled and pass QC.

## M19R-C Prep SDK State Logger

M19R-C SDK state logger prep adds SDK state-source discovery, standing-state smoke logging, guarded three-trial smoke planning, and SDK state-log measurement extraction utilities. The local development workspace does not have the Booster SDK importable, so no usable SDK state source, position stream, or yaw stream was detected here.

The full M19C measurement run is not ready until robot-side SDK discovery and standing/dynamic smoke logs confirm timestamped position and yaw. No empirical response statistics, response plots, risk-map validation, navigation improvement claim, or cross-robot generalization claim is added by this prep milestone.

## M19R-C ROS2 Odometer Logger Update

Robot-side discovery showed that sourcing `/opt/booster/BoosterRos2Interface/install/setup.bash` exposes `booster_interface` and `/odometer_state [booster_interface/msg/Odometer]` with `x`, `y`, and `theta`. M19R-C prep now prioritizes ROS2 odometer logging as the primary measurement source, with `/low_state.imu_state.rpy` and IMU topics as yaw fallbacks.

`GetFrameTransform` is downgraded because discovered frames are local body-part frames rather than odom/world/map frames. Local Windows smoke outputs cannot import ROS2/Booster packages, so the full M19C measurement run remains gated on robot-side odometer smoke logs.

## M19C Full ROS2 Odometer Measurement Runner

M19C full-run infrastructure now provides the 72-trial ROS2 odometer measurement runner, full-run extractor, measurement-run QC, and protocol documentation. Robot-side smoke evidence indicates ROS2 odometer extraction is feasible, including low-speed deadzone behavior at 0.20 m/s and measurable motion/yaw drift at 0.40 and 0.60 m/s.

Full empirical M19C analysis remains pending until the physical 72-trial run is completed, logs are extracted, and QC reports `m19c_measurement_extraction_ready_for_empirical_analysis`. No response-model or risk-map validation claim is added yet.

## M19C-E K1 Empirical Gold Profile

M19C-E ingests the completed 72-trial Booster K1 ROS2 odometer dataset and freezes `k1_gold_profile_v1.json` as a skill-facing single-unit reference profile. All 24 surface-speed cells have 3 measured trials. Default conservative region classification yields 8 deadzone cells, 6 unstable cells, 4 drift-prone cells, 2 over-response cells, and 4 reliable cells.

Project priority is now skill completion first. The paper track is kept minimal: M19C-E supports tested-K1 evidence of speed-response nonlinearity, surface dependence, deadzone behavior, and yaw-drift variation, but does not claim cross-robot generalization, compensation-controller validation, or navigation improvement.

## M20 Cross-Platform Calibration Skill Core

Next planned milestone: build a reusable calibration skill core with a common command adapter interface, common state logger interface, common measurement schema, robot-specific adapters for Booster K1, Unitree G1, and Unitree GO1, and simulated/test-fixture adapters for CI. No fake hardware results should be treated as empirical evidence.
