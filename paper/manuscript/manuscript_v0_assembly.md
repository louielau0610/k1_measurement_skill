# 1. Introduction

> **Status**: draft only — not a final manuscript section.
> **Citation safety**: uses only verified/partially verified citation keys from `paper/related_work/seed_references.bib`.
> **Basis**: synthesizes P1 seed literature, P2 gap analysis, P3 Related Work draft, M18 method skeleton/claim audit, and M13-M17 project artifacts.
> **Not an abstract**. Not a final novelty claim. Not a full manuscript.

---

## 1.1 Deployment motivation

Legged robots are increasingly deployed through high-level velocity command interfaces, where a planner or operator sends linear and angular velocity targets and expects the platform to track them [@TanRSS2018] [@HwangboSciRobot2019]. Command-conditioned locomotion policies and sim-to-real transfer pipelines have enabled rapid progress in robot agility and outdoor robustness [@MargolisRSS2022] [@MaRSS2024DrEureka]. However, deployment performance depends not only on the quality of a trained locomotion controller, but also on how faithfully commanded motion is executed on the real hardware under the specific deployment environment, floor surface, battery state, and payload.

For closed-source robots or SDK-driven platforms, this relationship is particularly opaque: the user operates through a manufacturer-provided interface (such as a DDS/ROS2 velocity command topic and an odometry feedback topic) but does not have access to the internal controller, state estimator parameters, or low-level actuator models. Under these conditions, the connection between commanded velocity and actual robot motion is a black-box system whose characteristics may vary with command magnitude, direction, and environment.

## 1.2 Problem: command-to-motion mismatch

When high-level velocity commands do not match executed motion — whether through under-tracking, over-tracking, deadzone behavior, or lateral/yaw drift — downstream navigation systems may assume a more reliable response than the robot actually provides [@FuCVPRW2022]. A planner that expects a commanded forward velocity to produce a certain displacement within a given time window may overestimate the robot's capability, leading to accumulated positioning error or, in the worst case, navigation decisions that the platform cannot execute.

This project studies the problem as a measurable deployment-layer response characteristic. Rather than modifying the robot's internal controller or training a new locomotion policy, the project treats the closed-source K1 quadruped as a measurement subject: externally commanded velocities and externally observed odometry are collected, structured through a research data schema, and analyzed to produce response predictions and advisory risk assessments. The current evaluation is limited to structural pipeline validation and does not yet include real navigation outcome metrics.

## 1.3 Candidate gap: closed-source deployment-layer response calibration

Prior work addresses several adjacent problems. Sim-to-real transfer research models actuator dynamics, latency, and domain randomization to close the reality gap during policy training [@TanRSS2018] [@HwangboSciRobot2019]. Rapid motor adaptation and online system identification allow policies to adjust to changing terrain, payload, and wear at deployment time [@KumarRMA2021] [@MargolisRSS2022]. Navigation-coupled locomotion work integrates terrain perception, proprioceptive signals, and footstep planning to constrain navigation decisions [@FuCVPRW2022] [@FanRSS2021STEP]. Risk-aware traversability frameworks assess environmental uncertainty for safe path planning [@FanRSS2021STEP].

These works generally assume the practitioner can modify the locomotion policy, access internal model parameters, or integrate perception and planning pipelines — assumptions that may not hold for closed-source, SDK-only deployment scenarios. The current seed literature does not yet establish a directly equivalent artifact-governed pipeline that operates purely at the external command-response interface of a closed-source legged robot. This motivates the present repository as a candidate contribution in the space of deployment-layer response calibration, recognizing that broader system-identification and commercial-SDK literature review is required before any final gap or novelty claim can be made.

## 1.4 Approach overview

This repository currently implements an artifact-governed pipeline that proceeds through five stages:

1. **Measurement v0 artifacts**: real K1 forward-velocity field measurements are collected under a read-only ROS2 logging protocol and validated through a research measurement profile.
2. **Velocity response dataset schema and dataset v1**: measurement records are structured through a JSON schema and consolidated into a sparse dataset of five command-response records with source provenance.
3. **Uncertainty-aware response model foundation**: a conservative hybrid response model produces velocity predictions, uncertainty labels, and confidence labels from the sparse dataset — without claiming calibrated probabilities.
4. **Navigation-aware reliability and risk mapping**: response predictions are translated into offline advisory risk categories, producing warning-level metadata for downstream interpretation.
5. **Pipeline evaluation and claim governance**: a paper-style evaluation package consolidates pipeline artifacts, separates supported structural claims from unsupported performance/safety claims, and documents unavailable metrics and required future experiments.

The current pipeline provides structural evidence for the existence and reproducibility of the artifact chain. It does not yet evaluate real navigation outcomes, report collision or success metrics, or calibrate uncertainty labels. The pipeline is measurement-only and advisory: it does not implement velocity compensation, inverse command mapping, navigation control, or safe command adaptation.

## 1.5 Current contributions as tentative contributions

The work currently contributes:

- **An artifact-governed measurement-to-model-to-risk-map pipeline** for black-box command-response characterization of a closed-source legged robot, with explicit separation between structural evidence and unsupported performance claims.
- **A sparse-evidence velocity response dataset and model contract** that labels uncertainty and confidence from five real K1 command-response records, with schema-level guardrails against fabricating or overinterpreting weak evidence.
- **An offline advisory risk interpretation layer** that maps response mismatch and uncertainty into navigation-relevant warning metadata, while clearly documenting that these labels are not calibrated probabilities and do not constitute navigation control.
- **A claim-governed evaluation package** that tracks project evidence, prior-work evidence, candidate gaps, prohibited claims, and upgrade conditions across milestones, enabling incremental drafting without overclaiming.

All contributions remain tentative and are positioned as candidate contributions, not final novelty. Each requires additional literature review, expanded measurement data, and/or real navigation outcome experiments before being upgraded.

## 1.6 Scope and limitations

The current repository operates under the following scope:

- **Single robot**: one K1 closed-source quadruped unit.
- **Sparse command set**: five forward-velocity commands from Measurement v0.
- **Single environment**: one indoor floor surface, one session.
- **No calibrated uncertainty**: M15R labels are metadata flags, not calibrated probability estimates.
- **No real navigation outcomes**: collision rate, near-miss rate, success rate, and navigation safety metrics are explicitly documented as unavailable.
- **No compensation**: velocity compensation logic is not implemented and remains a future milestone.
- **No safe command adapter**: safe command adaptation is not implemented.
- **No navigation controller**: the repository does not send navigation commands to a robot.

These limitations are structural to the current research stage and are essential context for interpreting every claim in this and subsequent drafts.

## 1.7 Paper organization placeholder

> **Draft note**: The following is a planned organization outline, not a finalized structure. It may be revised after P5 (Method draft) and P6 (Experiments draft).

The remainder of a potential future manuscript is planned as follows. Section 2 reviews related work across sim-to-real locomotion, adaptation, navigation-coupled planning, risk-aware evaluation, and black-box command-response calibration (draft v1 available at `paper/manuscript/sections/02_related_work_draft_v1.md`). Section 3 describes the method pipeline and its five stages (skeleton available at `paper/manuscript/sections/03_method_skeleton.md`). Section 4 presents the current experimental evidence, separating structural validation from missing navigation outcomes (skeleton available at `paper/manuscript/sections/04_experiments_skeleton.md`). Sections 5-7 address discussion, limitations, and conclusion as planned scaffolding content only.

### 1.8 Known limitations of this draft

1. **Citation coverage reflects P3 limitations**: only 8 verified/partially verified seed references are available in `seed_references.bib`. Broader black-box system identification, commercial SDK calibration, and field robotics evaluation literature is needed.
2. **Contribution statements remain tentative**: all contribution bullets use candidate language and are not ready for final manuscript claims.
3. **No abstract exists**: this Introduction draft is not a substitute for a paper abstract, which should be written last, after all sections are drafted and evidence is reviewed.
4. **Organization section is a placeholder**: the "Paper organization" paragraph is planned content only and will need revision after P5 and P6.
5. **This draft does not establish final novelty or publication readiness** and is intended for revision after additional literature review and experiments.


# 2. Related Work

> **Status**: draft only — not a final manuscript section.
> **Citation safety**: uses only verified or partially verified citation keys from `paper/related_work/seed_references.bib`.
> **Basis**: synthesizes P1 literature matrix v1 and P2 gap analysis v1.
> **No final novelty claim**. No performance superiority claim. No navigation safety improvement claim.
> This draft is intended for later editing and expansion; additional literature review is needed before submission.

---

## 2.21 Sim-to-real and learned legged locomotion

Learned locomotion policies have demonstrated agile and robust behaviors on quadruped robots, with much of the progress driven by simulation training and sim-to-real transfer [@TanRSS2018] [@HwangboSciRobot2019]. Tan *et al.* [@TanRSS2018] showed that closing the sim-to-real gap requires careful modeling of actuator dynamics, latency, and domain randomization, while Hwangbo *et al.* [@HwangboSciRobot2019] demonstrated that trained policies can deploy directly on complex hardware such as ANYmal. More recently, LLM-guided domain randomization [@MaRSS2024DrEureka] has been proposed to automate the sim-to-real configuration process for legged locomotion tasks.

These works primarily target the training and deployment of learned locomotion controllers under the assumption that the practitioner has full access to the policy, simulator, and low-level control stack. They do not establish an external, measurement-only calibration pipeline for closed-source robots where the user can only observe command-response behavior through the manufacturer-provided SDK interface. In contrast, our current project focuses on artifact-governed measurement and response modeling under black-box deployment constraints, using externally collected velocity command and odometry records from a closed-source K1 quadruped without modifying or retraining its internal locomotion policy.

## 2.2 Rapid motor adaptation and deployment adaptation

Several recent works address deployment-time adaptation as a strategy for robust legged locomotion. Kumar *et al.* [@KumarRMA2021] introduced a base-policy plus adaptation-module architecture that learns to compensate for varying terrain, payload, and wear online, deployed on a Unitree A1. Margolis and Agrawal [@MargolisRSS2022] proposed end-to-end RL controllers with adaptive velocity-command curricula and online system identification for high-speed outdoor locomotion on the MIT Mini Cheetah.

These adaptation approaches operate at the controller or policy level and typically require the ability to modify the locomotion controller. They are complementary to, and conceptually distinct from, an external, artifact-governed calibration workflow that measures and labels command-to-motion response mismatch without altering the robot's control stack. Our current M15R response model foundation labels uncertainty and confidence from sparse measurement records, but it does not perform online adaptation, policy modification, or system identification of internal controller parameters.

## 2.3 Navigation-coupled legged locomotion

The interface between high-level navigation and low-level locomotion has received increasing attention in legged robotics. Fu *et al.* [@FuCVPRW2022] coupled vision-based cost maps with proprioceptive safety signals to constrain legged robot navigation speeds, demonstrating that awareness of low-level walking capability can influence navigation decisions. Fan *et al.* [@FanRSS2021STEP] developed a stochastic traversability evaluation and planning framework (STEP) that assesses terrain risk under uncertainty for safe off-road navigation across wheeled and legged platforms.

These works generally assume access to terrain perception, path planning, and a controllable locomotion stack, and they derive safety or risk signals from perceptual and geometric features of the environment. Our project takes a different, narrower approach: it derives offline advisory risk metadata specifically from externally measured command-to-motion response mismatch, without terrain perception, without a planner, and without controlling the robot's navigation stack. The motivation is that, for closed-source deployment, the command-response relationship itself may carry useful warning information for downstream planning systems.

## 2.4 Risk- and uncertainty-aware navigation

Risk-aware planning and uncertainty-aware traversability evaluation have been studied across ground and legged robot platforms. STEP [@FanRSS2021STEP] provides a comprehensive framework for reasoning about terrain traversability under localization and sensing uncertainty using CVaR-based tail-risk assessment. This literature supports the broader principle that navigation planning benefits from explicit uncertainty representation.

Our M15R/M16 pipeline produces uncertainty/confidence labels and advisory risk categories from response model predictions, inspired by but not equivalent to the calibrated risk frameworks found in the traversability literature. A critical limitation is that our current labels are not calibrated probabilities: they are derived from sparse single-session K1 measurement evidence and are intended as conservative metadata flags, not as safety guarantees. Further experiments are required to evaluate whether these response-derived labels can be calibrated and to assess their correspondence with established risk metrics.

## 2.5 Field robotics metrics and evaluation

Field robotics evaluation protocols emphasize repeatable outcome metrics such as success rate, collision rate, near-miss rate, and traversability scores. Prior work such as STEP [@FanRSS2021STEP] includes field validation across extreme terrain, and the broader traversability- and navigation-evaluation literature defines metric categories against which deployment claims should be measured.

Our current M17 pipeline evaluation is structural rather than performance evaluation: it validates that the measurement-to-dataset-to-model-to-risk-map artifact chain is internally consistent and reproducible, but it does not report real navigation outcomes. Collision, near-miss, success-rate, and navigation-safety metrics are explicitly recorded as unavailable and as required evidence for any future performance or safety claim. The field robotics metrics literature provides the vocabulary for what would constitute an adequate evaluation, and it reinforces the conservative position that structural validation alone does not constitute navigation performance evidence.

## 2.6 Black-box command-response calibration and deployment-layer mismatch

Command-response modeling, system identification, and external calibration have been addressed in several adjacent robotics domains. Tan *et al.* [@TanRSS2018] performed system identification of actuator and latency parameters as part of their sim-to-real pipeline. Yang *et al.* [@YangRAL2022] proposed online kinematic calibration for legged robots using velocity prediction errors within a state estimator. Margolis and Agrawal [@MargolisRSS2022] incorporated online system identification into their RL controller to handle deployment-domain shift.

These works motivate the value of characterizing and compensating for deployment mismatch, but they typically assume access to the robot's internal model parameters, state estimator, or controller structure. The current seed literature does not yet establish a directly equivalent artifact-governed pipeline that operates purely at the deployment command-response interface of a closed-source legged robot — measuring commands and odometry externally, validating sparse evidence through a research schema, and deriving conservative response predictions and risk labels without internal access. This motivates further literature review in black-box system identification and commercial quadruped SDK calibration before any final gap or novelty claim can be made.

## 2.7 Positioning of the current work

The work in this repository currently implements a conservative, artifact-governed pipeline that transforms real K1 forward-velocity measurement artifacts into dataset records, response predictions, uncertainty/confidence labels, advisory risk assessments, and claim-governed evaluation artifacts. The pipeline is measurement-only: it does not implement velocity compensation, inverse command mapping, navigation control, or safe command adaptation.

The project is positioned as a set of candidate contributions, not as final novelty. The current evidence — five sparse single-session command-response records, conservative model outputs, and structural pipeline validation — is sufficient to support the existence of the pipeline but insufficient to support performance, safety, or generalization claims. Additional literature review, multi-session measurement, and real navigation outcome experiments are required before the candidate contributions can be upgraded.

### 2.8 Known limitations of this draft

1. **Citation coverage is limited to 8 verified/partially verified seed references.** The P1 literature matrix contains 16 entries, but only 8 have verified BibTeX entries in `seed_references.bib`. Eight additional matrix entries (RudinCoRL2021, MargolisCoRL2022, DaoArxiv2026, GangapurwalaArxiv2020, GrandiaTRO2023, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025) lack BibTeX entries and are not cited in this draft. These should be added to the BibTeX file and the draft expanded after verification.
2. **Sections 4 and 5 have the thinnest citation support** — both currently rely primarily on a single verified source [@FanRSS2021STEP]. Broader traversability risk and field evaluation literature review is needed.
3. **No cross-comparison with commercial quadruped SDK calibration literature.** P1 did not surface papers that specifically address calibration workflows for commercial closed-source robot SDKs.
4. **This draft does not establish a novelty claim** and is not ready for a final manuscript submission. It is a structural first pass intended to be revised after P4 (Introduction draft) and after additional literature and experiments.


# 3. Method

> **Status**: draft only — not a final manuscript section.
> **Basis**: derived from M13-M18 method artifacts, P2 gap analysis, and P4 Introduction/Problem Statement.
> **Not a novelty claim**. Not a performance claim. Not a full manuscript. No compensation, inverse mapping, navigation control, or safe command adapter is implemented.

---

## 3.0 Method Overview

This work implements an offline, artifact-governed pipeline for characterizing the black-box command-to-motion response of a closed-source legged robot. The pipeline maps real measurement artifacts through five stages: (1) measurement artifact construction and structuring, (2) velocity response dataset construction under a research schema, (3) conservative uncertainty-aware response modeling, (4) offline navigation-aware reliability and risk mapping, and (5) claim-governed pipeline evaluation. All stages produce structured, reproducible output artifacts with explicit input/output contracts and safety flags. The method does not implement velocity compensation, inverse command mapping, real-time navigation control, or safe command adaptation. A planned pipeline figure (specification at `paper/figures/method_pipeline_figure_spec.md`) illustrates the artifact flow.

## 3.01 System Boundary and Assumptions

**System boundary**. The robot is treated as a closed-source command-execution system. The user operates through an SDK-provided velocity command interface and receives odometry feedback, but has no access to the internal locomotion controller, state estimator parameters, actuator model, or proprietary SDK internals. The method uses only externally observable or already-available structured artifacts.

**Assumptions**:
- A ROS2-based velocity command topic and an odometry feedback topic are available for read-only logging.
- Commanded body-frame velocities `[v_x^cmd, v_y^cmd, omega_z^cmd]` can be recorded alongside odometry-derived actual velocities `[v_x^actual, v_y^actual, omega_z^actual]`.
- Measurement environment (floor type, session identifier) is documented.
- `battery_state` is optional and not required for pipeline operation.
- `remote_controller_state` is permanently out of scope and excluded from all research schema artifacts.
- No unconfirmed ROS2 topics are used.

**Explicit non-goals**. This is not controller tuning. This is not policy training. This is not velocity compensation. This is not real-time navigation control. The method is confined to offline measurement, modeling, and advisory interpretation of existing sensor logs.

## 3.02 Problem Formulation

Let:

```
u = [v_x^cmd, v_y^cmd, omega_z^cmd]       (commanded body-frame velocity)
c = [environment, robot_state_optional]     (deployment context)
x = [u, c]                                  (method input)
y = [v_x^actual, v_y^actual, omega_z^actual,
     response_label, uncertainty_label]     (response characterization)
r = [tracking_reliability_label,
     navigation_risk_level,
     warning_category]                      (advisory risk metadata)
```

The pipeline defines two mappings:

```
f(x) -> y_hat     (response prediction)
g(y_hat) -> r     (advisory risk assessment)
```

where `f` is a conservative, rule-based model that produces response predictions with uncertainty labels, and `g` is an offline risk-mapping function that assigns warning-level metadata without controlling the robot.

**Current instantiations**:
- Dataset v1 instantiates only a sparse subset of `u`: forward velocity `v_x^cmd` at five command values derived from Measurement v0.
- `v_y^cmd` and `omega_z^cmd` are schema-supported fields reserved for future measurement expansion.
- `uncertainty_label` is a categorical reliability marker (`low`, `medium`, `high`, `extreme`), not a calibrated probability.
- `g` produces advisory risk categories (`low-risk`, `moderate-risk`, `high-risk`); it does not issue navigation commands, modify velocity targets, or trigger safety interventions.

## 3.03 Stage 1 — Measurement Artifact Construction

The pipeline begins with Measurement v0 artifacts obtained from a real K1 forward-velocity field test. The measurement protocol records commanded forward velocities through a read-only ROS2 logging setup and extracts odometry-derived actual velocities from synchronized topic streams. Supporting artifacts include the K1 velocity profile contract (`docs/real_k1_velocity_profile_contract_v0.md`), the field test documentation (`docs/real_k1_forward_velocity_field_test_v0.md`), and the measurement closure summary (`outputs/real_k1_field_tests/measurement_v0_closure_summary.json`).

What Measurement v0 provides:
- Structured records of commanded `v_x` and estimated actual `v_x` for five forward-velocity conditions under a single indoor floor surface.
- Qualitative tracking assessments (e.g., deadzone, weak tracking, under-tracking, stable tracking).
- Documented environment metadata.

What Measurement v0 does not provide:
- Lateral or angular velocity evidence (`v_y`, `omega_z`).
- Multi-surface, multi-session, or multi-unit evidence.
- Ground-truth motion capture or external reference measurements beyond the robot's own odometry.
- Compensation-ready or navigation-safety evidence.

Measurement v0 artifacts are treated as the primary source of real-robot response evidence and are never fabricated, imputed, or extrapolated beyond their recorded values.

## 3.04 Stage 2 — Velocity Response Dataset Construction

Dataset v1 is constructed from Measurement v0 artifacts under the velocity response dataset schema v1 (`configs/velocity_response_dataset_schema_v1.json`). The schema defines mandatory fields (`vx_cmd_mps`, `measurement_source`), optional fields (`vx_actual_mps_mean`, `battery_state`), qualitative fields (`qualitative_response_label`), and permanently excluded fields (e.g., `remote_controller_state`). A field-level mapping document (`docs/measurement_v0_to_velocity_response_schema_v1_mapping.md`) governs the transformation.

**Field categories**:
- **Direct fields**: mapped one-to-one from existing structured Measurement v0 fields (e.g., `vx_cmd_mps`, `measurement_source`).
- **Derived fields**: computed from Measurement v0 fields only when the source field exists and is non-null (e.g., `vx_actual_mps_mean` from `v_actual_est_mps`).
- **Qualitative fields**: preserved when numeric evidence is absent (e.g., `qualitative_response_label` = `deadzone` for `0.1 m/s` where actual displacement could not be measured).
- **Unavailable fields**: omitted rather than fabricated (e.g., `yaw_drift_deg_per_s`, `lateral_drift_mps`, `response_delay_ms`).

**No-fabrication policy**: if a numeric actual velocity is absent from the source artifact, the corresponding dataset field is left absent; no value is synthesized, interpolated, or inferred from similar commands.

**Pseudo-algorithm**:
```
Algorithm 1: Measurement artifacts to velocity-response dataset
Input: Measurement v0 artifacts, schema v1
Output: Dataset v1, validation report
Steps:
1. Load structured measurement artifacts.
2. For each command condition, map direct fields according to the v0-to-v1 mapping document.
3. Compute derived fields only where source numeric fields exist and are non-null.
4. Preserve qualitative labels when numeric response is absent.
5. Omit unavailable fields without fabricating values.
6. Validate all records against schema v1 using the project schema validator.
```

Outputs: `outputs/research_datasets/velocity_response_dataset_v1.json` and `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json`. The producer script is `scripts/build_velocity_response_dataset_v1.py`, which calls `k1_measurement.velocity_response_dataset_builder` and `k1_measurement.research_dataset_schema`.

## 3.05 Stage 3 — Uncertainty-Aware Velocity Response Modeling

The response model `uncertainty_aware_hybrid_v1` is a lightweight, rule-based model (not a learned/ML model) that produces conservative velocity response predictions with uncertainty and confidence labels. It operates on the sparse Dataset v1 records and does not assume a parametric velocity-response curve.

**Prediction contract** (`k1_measurement.velocity_response_model.VelocityResponsePrediction`): each prediction object includes query velocity, model name, prediction type, optional numeric predicted actual velocity, qualitative response label, uncertainty label, confidence label, source record identifiers, interpolation/extrapolation flags, limitations, and downstream safety flags (all confirmed `compensation_allowed=false`, `safe_command_adapter_allowed=false`, `navigation_warning_ready=true`).

**Handling rules**:
- **Exact numeric match**: if a dataset record with the same commanded velocity contains a numeric actual velocity, the model returns that source value directly. This is a structural sanity check, not a predictive accuracy claim.
- **Exact qualitative-only match**: if an exact command exists but only a qualitative label is available (e.g., `0.1 m/s` deadzone), the model returns the qualitative label without fabricating a numeric predicted velocity.
- **Bounded interpolation**: if bracketing numeric evidence exists on both sides of the query command, bounded linear interpolation is permitted between the nearest lower and upper evidence points.
- **Mixed or out-of-range**: if evidence is mixed (numeric on one side, qualitative on the other) or the query lies outside the evaluated command range, the model returns conservative uncertainty labels (`high` or `extreme`) and explicitly records the limitation.

**Baseline hooks**: three minimal baseline model interfaces (`nearest_lookup_baseline_v1`, `naive_global_gain_baseline_v1`, `piecewise_linear_baseline_v1`) are retained as comparison hooks for future evaluation. They are not currently evaluated against held-out data and are not presented as competitive baselines.

**Pseudo-algorithm**:
```
Algorithm 2: Conservative response prediction
Input: Dataset v1, query command velocity vx_query
Output: VelocityResponsePrediction
Steps:
1. Search Dataset v1 for an exact vx_cmd match.
2. If exact numeric evidence exists, return numeric source prediction with low uncertainty.
3. If exact qualitative-only evidence exists, return qualitative prediction without numeric fabrication.
4. If bracketing numeric evidence (vx_lower < vx_query < vx_upper) exists, perform bounded interpolation.
5. If evidence is mixed or vx_query is out of evaluated range, return conservative uncertainty label and record limitations.
6. Preserve downstream safety flags in the prediction output.
```

Outputs: `outputs/research_models/response_model_predictions_v1.json` and `outputs/research_models/response_model_evaluation_v1.json`. The producer script is `scripts/run_velocity_response_model_v1.py`, which calls `k1_measurement.velocity_response_model`.

## 3.06 Stage 4 — Navigation-Aware Reliability and Risk Mapping

The navigation risk mapper (`k1_measurement.navigation_risk_mapping.NavigationRiskMapper`) translates each response prediction into an advisory navigation risk assessment. It does not access the robot, a planner, or a navigation stack.

**Mapping logic**: for each prediction, the mapper inspects the prediction type, qualitative response label, uncertainty label, and confidence label, then assigns:
- **Tracking reliability label**: `reliable`, `moderate`, `unreliable`, or `unknown`.
- **Navigation risk level**: `low-risk`, `moderate-risk`, or `high-risk`.
- **Warning category**: whether the command velocity is near a deadzone, under-tracking, weak-tracking, or presents high uncertainty.
- **Allowed downstream uses**: includes offline analysis, research evaluation, planner warning advisory, and human review.
- **Disallowed downstream uses**: always includes automatic compensation, inverse command mapping, real-time navigation control, safe command adapter execution, and robot motion commanding.

**Explicit scope boundaries**:
- No automatic compensation is triggered by risk levels.
- No inverse command mapping is computed from risk categories.
- No real-time navigation control commands are issued.
- No safe command adapter execution is performed.

**Pseudo-algorithm**:
```
Algorithm 3: Response prediction to navigation-risk assessment
Input: VelocityResponsePrediction
Output: NavigationRiskAssessment
Steps:
1. Inspect prediction type, qualitative label, uncertainty, and confidence.
2. Assign tracking reliability label based on combined evidence quality.
3. Assign navigation risk level (low / moderate / high).
4. Determine whether advisory warning is required.
5. Record risk reasons (e.g., deadzone, under-tracking, high uncertainty).
6. Record allowed and disallowed downstream uses.
```

Outputs: `outputs/research_risk/navigation_risk_map_v1.json` and `outputs/research_risk/navigation_risk_evaluation_v1.json`. The producer script is `scripts/run_navigation_risk_mapping_v1.py`, which calls `k1_measurement.navigation_risk_mapping`.

## 3.07 Stage 5 — Claim-Governed Evaluation

The pipeline evaluation stage (`scripts/generate_research_pipeline_evaluation_v1.py`) consolidates all upstream artifacts into a structured evaluation package that explicitly separates structural/software validation from unsupported performance claims.

**Evaluation categories**:
- **Structural/software validation**: confirms that artifacts exist, are JSON-valid, conform to their schema, and are reproducible via documented scripts.
- **Dataset evidence summary**: records the number of dataset records, numeric vs. qualitative-only counts, and command range covered.
- **Model sanity checks**: verifies that exact-source numeric predictions are self-consistent and that qualitative-only records are not numerically fabricated.
- **Risk-map readiness evaluation**: reports risk-level and warning-category counts without interpreting them as navigation-safety evidence.
- **Real navigation outcome evaluation**: explicitly documented as *not available*; collision rate, near-miss rate, success rate, and path-deviation metrics are all listed as missing.

**Claim governance**: the evaluation package links to the project claim registry (`paper/claims/claim_registry.md`), evidence table (`paper/claims/evidence_table.md`), and non-claims (`paper/claims/non_claims.md`). These governance artifacts track which statements are supported by project evidence, supported by prior work, plausible but unverified, planned, or explicitly prohibited. This separation prevents the Method section from implying capabilities that the current pipeline does not possess.

## 3.08 Reproducibility and Artifact Traceability

Each pipeline stage produces traceable output artifacts through documented producer scripts. The following table summarizes the artifact chain:

| Stage | Producer script | Output artifact | Validation artifact |
| --- | --- | --- | --- |
| Schema definition | — (repository artifact) | `configs/velocity_response_dataset_schema_v1.json` | `scripts/validate_velocity_response_dataset_schema.py` |
| Dataset construction | `scripts/build_velocity_response_dataset_v1.py` | `outputs/research_datasets/velocity_response_dataset_v1.json` | `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` |
| Response modeling | `scripts/run_velocity_response_model_v1.py` | `outputs/research_models/response_model_predictions_v1.json` | `outputs/research_models/response_model_evaluation_v1.json` |
| Risk mapping | `scripts/run_navigation_risk_mapping_v1.py` | `outputs/research_risk/navigation_risk_map_v1.json` | `outputs/research_risk/navigation_risk_evaluation_v1.json` |
| Pipeline evaluation | `scripts/generate_research_pipeline_evaluation_v1.py` | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | `outputs/research_evaluation/m17_method_artifact_table.md` |

All producer scripts are runnable from the repository root and report clear error messages for missing inputs, invalid schemas, or fabricating operations. A more detailed artifact evidence table is maintained at `paper/tables/method_artifact_evidence_table.md`.

## 3.09 Scope and Current Limitations

The method operates under the following current constraints:

- **Single robot**: one K1 closed-source quadruped unit.
- **Sparse command set**: five forward-velocity commands (`v_x` only; `v_y` and `omega_z` not yet measured).
- **Single environment**: one indoor floor surface, one session.
- **No calibrated uncertainty**: M15R labels are categorical reliability markers, not calibrated probability estimates.
- **No lateral, yaw, delay, or stop-distance metrics**: these remain schema-supported future fields with no current measurement evidence.
- **No real navigation outcomes**: collision rate, near-miss rate, success rate, and path-deviation metrics are documented as unavailable.
- **No compensation**: velocity compensation logic is not implemented.
- **No safe command adapter**: safe command adaptation is not implemented.
- **No navigation controller**: the method does not send navigation commands to a robot.

**Future evidence required**: before any contribution can be upgraded from tentative to supported, the following evidence is needed — repeated velocity-response trials per command, multi-surface and multi-session data collection, an expanded command grid including `v_y` and `omega_z`, hold-out prediction evaluation, uncertainty calibration trials, and real navigation task trials with outcome metrics. Performance or safety claims remain unsupported until such evidence exists.


# 4. Experiments and Evaluation

> **Status**: draft only — not a final manuscript section.
> **Basis**: derived from M17 pipeline evaluation, M18 experiments skeleton, P5 method draft, and real repository output artifacts.
> **Structural evaluation only**: current evaluation covers dataset construction, response-model outputs, risk-map outputs, and pipeline reproducibility. It does not include real navigation outcome trials.
> **No performance claim**. No navigation safety claim. No publication readiness claim.

---

## 4.0 Experiments and Evaluation Overview

The current evaluation is artifact-level and structural: it confirms that each pipeline stage produces valid, reproducible output artifacts given the available sparse input evidence. This section reports dataset evidence, response-model evaluation, risk-map assessment, claim-governed pipeline evaluation, and a transparent accounting of what is and is not yet measurable. Real navigation outcome trials — measuring collision rates, near-miss rates, success rates, or safety improvement — are not part of the current evaluation and are documented as future required experiments.

## 4.01 Evaluation Questions

We structure the evaluation around five questions, each mapped to existing repository artifacts:

- **EQ1**: Can Measurement v0 artifacts be converted into a schema-valid velocity response dataset without fabricating unavailable values?
- **EQ2**: Can the response-model layer produce conservative predictions for both numeric and qualitative-only dataset records?
- **EQ3**: Can response predictions be mapped into navigation-aware advisory risk assessments with explicit warning metadata?
- **EQ4**: Are pipeline artifacts and claims traceable enough for paper-style structural evaluation?
- **EQ5**: Which performance and safety claims remain unsupported by current evidence?

A detailed EQ-to-artifact mapping is maintained at `paper/tables/evaluation_question_artifact_map.md`.

## 4.02 Reproducible Artifact Chain

All evaluation outputs are generated by producer scripts runnable from the repository root:

| evaluation stage | producer script | output artifact |
| --- | --- | --- |
| Dataset construction & validation | `scripts/build_velocity_response_dataset_v1.py` | `outputs/research_datasets/velocity_response_dataset_v1.json` + validation report |
| Response model prediction & evaluation | `scripts/run_velocity_response_model_v1.py` | `outputs/research_models/response_model_predictions_v1.json` + evaluation |
| Navigation risk mapping & evaluation | `scripts/run_navigation_risk_mapping_v1.py` | `outputs/research_risk/navigation_risk_map_v1.json` + evaluation |
| Pipeline evaluation report | `scripts/generate_research_pipeline_evaluation_v1.py` | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` |

Each script validates its inputs, reports errors for missing or invalid artifacts, and writes structured output in a schema-defined format. Schema validation is available via `scripts/validate_velocity_response_dataset_schema.py`.

## 4.03 Dataset Evidence

Dataset v1 (`outputs/research_datasets/velocity_response_dataset_v1.json`) contains **5 records** derived from Measurement v0 artifacts:

- **4 numeric records** at commanded velocities 0.30, 0.40, 0.45, and 0.50 m/s — each includes an odometry-derived numeric actual forward velocity.
- **1 qualitative-only record** at commanded velocity 0.10 m/s — the actual forward displacement could not be meaningfully measured, so the record carries a `qualitative_response_label` of `deadzone` without a fabricated numeric `vx_actual_mps_mean`.

**Field mapping policy**: direct fields (e.g., commanded velocity) are mapped one-to-one from Measurement v0; derived fields (e.g., mean actual velocity) are computed only where source numeric fields exist; qualitative labels are preserved when numeric evidence is absent; unavailable fields (lateral drift, yaw drift, response delay, stop distance) are omitted rather than fabricated.

**Validation**: all 5 records pass schema validation (`velocity_response_dataset_v1_validation_report.json`), confirming structural compliance with the dataset schema v1. This supports EQ1: schema-valid dataset construction without fabrication.

**Missing fields** (documented, not fabricated): `yaw_drift_deg_per_s`, `lateral_drift_mps`, `response_delay_ms`, `stop_distance_m`, `vx_actual_mps_std`, `vx_actual_mps_min`, `vx_actual_mps_max`, calibrated confidence scores, and multi-trial statistics. `battery_state` remains optional.

## 4.04 Response Model Evaluation

The response model evaluation (`outputs/research_models/response_model_evaluation_v1.json`) covers 5 prediction queries from the `uncertainty_aware_hybrid_v1` model with dataset inputs of 5 records (4 numeric, 1 qualitative-only).

**Prediction coverage**:
- Exact numeric matches return source actual velocity values without interpolation.
- The qualitative-only record at 0.10 m/s returns a qualitative `deadzone` label without numeric fabrication.
- Bounded interpolation is applied where bracketing numeric evidence exists.
- Out-of-range queries would return conservative uncertainty labels with explicit limitations.

**Exact-source reconstruction sanity check**: for records where numeric source evidence exists, the model returns the source actual velocity value. The absolute reconstruction error is 0.0 m/s (mean and maximum) — this is a structural sanity check confirming the model retrieves its own input correctly, not evidence of predictive performance.

**Baseline model hooks**: three baseline interfaces (`nearest_lookup_baseline_v1`, `naive_global_gain_baseline_v1`, `piecewise_linear_baseline_v1`) are retained in the model module for future comparison readiness. They are not evaluated on held-out data and no superiority or inferiority claim is made about any model.

**Uncertainty labeling**: all predictions carry categorical uncertainty and confidence labels (`low`, `medium`, `high`, `extreme`). These are conservative metadata flags, not calibrated probability estimates. The evaluation explicitly records: `uncertainty_and_confidence_are_labels_not_calibrated_probabilities`.

**Limitations affecting model evaluation**:
- Single trial per command velocity (no held-out evaluation possible).
- Single environment and single session.
- Odometer-primary measurements without external ground truth.
- Sparse command grid (5 points; no `v_y` or `omega_z` evidence).
- No compensation or safe command adapter authority.

This supports EQ2: conservative prediction generation for both numeric and qualitative records, with appropriate uncertainty labeling.

## 4.05 Navigation-Risk Evaluation

The navigation-risk evaluation (`outputs/research_risk/navigation_risk_evaluation_v1.json`) reports **5 advisory risk assessments** with **5 warnings**:

| risk level | count | interpretation |
| --- | --- | --- |
| critical | 1 | command velocity at deadzone; no measurable motion |
| high | 2 | high uncertainty or under-tracking behavior |
| medium | 2 | moderate tracking with some warning indicators |

| warning category | count |
| --- | --- |
| deadzone / no motion | 1 |
| high uncertainty | 2 |
| under tracking | 1 |
| weak tracking | 1 |

Each assessment carries an explicit `allowed_downstream_uses` list (offline analysis, research evaluation, planner warning advisory, human review) and `disallowed_downstream_uses` list (automatic compensation, inverse command mapping, real-time navigation control, safe command adapter execution, robot motion commanding). Every assessment confirms `compensation_allowed=false` and `safe_command_adapter_allowed=false`.

**Critical limitation**: these risk levels and warnings are derived from model prediction attributes — not from real navigation outcomes. No collision, near-miss, or success-rate data exists. The evaluation explicitly records `no_real_navigation_outcomes=true` and `no_safety_improvement_claim=true`. This supports EQ3: advisory risk assessments can be generated, but they do not constitute navigation performance evidence.

## 4.06 Claim-Governed Pipeline Evaluation

The M17 pipeline evaluation (`outputs/research_evaluation/m17_pipeline_evaluation_report.json`) consolidates all upstream artifacts into a claim-governed evaluation package.

**Supported structural claims**:
- The repository contains an offline, artifact-governed, five-stage pipeline from measurement to risk mapping.
- Dataset v1 exists and is schema-valid with 5 records (4 numeric, 1 qualitative-only).
- The response model produces conservative predictions with uncertainty/confidence labels.
- The risk map produces advisory assessments with warning metadata.
- Pipeline artifacts are reproducible via documented producer scripts.
- Claim governance (registry, evidence table, non-claims) separates structural evidence from unsupported performance claims.

**Non-claims explicitly enforced**:
- No navigation safety improvement.
- No collision-rate reduction.
- No near-miss-rate reduction.
- No success-rate improvement.
- No path-deviation improvement.
- No compensation readiness.
- No safe command adapter readiness.
- No publication readiness.
- No generalizability across robots, surfaces, or sessions.

This supports EQ4: artifacts and claims are sufficiently traceable for structural paper-style evaluation. It also directly answers EQ5: performance and safety claims remain unsupported.

## 4.07 Current Metrics and Missing Evidence

| metric category | metric | available | current source |
| --- | --- | --- | --- |
| Dataset | record count (5) | yes | `velocity_response_dataset_v1.json` |
| Dataset | numeric records (4) | yes | `velocity_response_dataset_v1.json` |
| Dataset | qualitative-only records (1) | yes | `velocity_response_dataset_v1.json` |
| Dataset | schema validation pass | yes | `velocity_response_dataset_v1_validation_report.json` |
| Model | prediction count (5) | yes | `response_model_predictions_v1.json` |
| Model | exact-source reconstruction MAE (0.0) | sanity check only | `response_model_evaluation_v1.json` |
| Model | held-out prediction error | **no** | — |
| Model | calibrated uncertainty error | **no** | — |
| Risk | assessment count (5) | yes | `navigation_risk_map_v1.json` |
| Risk | warning count (5) | yes | `navigation_risk_evaluation_v1.json` |
| Risk | risk level distribution | yes | `navigation_risk_evaluation_v1.json` |
| Performance | collision rate | **no** | — |
| Performance | near-miss rate | **no** | — |
| Performance | navigation success rate | **no** | — |
| Performance | path deviation | **no** | — |
| Safety | before/after advisory layer comparison | **no** | — |
| Generalization | multi-environment replication | **no** | — |
| Generalization | cross-robot replication | **no** | — |

Currently available metrics support structural evaluation only. All performance, safety, and generalization metrics require future multi-trial, multi-session experiments.

A detailed metrics status table is maintained at `paper/tables/experiment_metrics_status_table.md`.

## 4.08 Future Experimental Protocol

The following experimental expansions are required before any performance or safety claim can be supported:

- **Repeated trials per command velocity**: at least 3–5 repeated forward-velocity trials per command condition to estimate variability.
- **Multi-surface testing**: collect response evidence on at least 2–3 distinct floor surfaces (e.g., hard floor, carpet, outdoor pavement).
- **Expanded command grid**: add `v_y` and `omega_z` command dimensions; expand `v_x` grid beyond 5 points.
- **Additional response metrics**: record yaw drift, lateral drift, response delay, and stop distance.
- **Hold-out evaluation**: split trials into model-fitting and held-out sets for prediction error evaluation.
- **Navigation task trials**: define a fixed navigation protocol, run trials with and without advisory-layer exposure, and record collision, near-miss, and success outcomes under controlled conditions.
- **Baseline comparison protocol**: evaluate the proposed model against simple baselines (nearest lookup, global gain, piecewise linear) on the same expanded dataset.
- **Uncertainty calibration**: if probability-calibrated uncertainty is desired, collect sufficient repeated evidence and apply a calibration protocol with held-out evaluation.

None of these experiments have been conducted as of this draft. They are listed as required evidence for upgrading any contribution from tentative to supported.

## 4.09 Evaluation Summary

The current evaluation establishes that an offline, artifact-governed pipeline can transform real K1 measurement evidence into a schema-valid dataset, conservative response predictions with uncertainty labels, and advisory navigation-risk assessments — without fabricating unavailable values, without claiming calibrated uncertainty, and without implementing compensation or navigation control. All available metrics are structural or distributional counts derived from existing output artifacts.

The evaluation does not, and with current evidence cannot, establish:
- predictive performance of the response model,
- calibrated uncertainty estimates,
- real navigation safety improvement,
- collision or near-miss reduction,
- compensation or safe command adapter readiness,
- generalizability across environments or robots.

Future experiments, including repeated multi-session trials and controlled navigation task protocols, are required before any performance or safety claim can be made.


# 5. Discussion and Limitations

> **Status**: draft only — not a final manuscript section.
> **Basis**: synthesizes P3-P6 manuscript drafts, M17/M18 evaluation artifacts, and claim-governance documents.
> **Structural evidence only**: current discussion describes what the pipeline demonstrates and what it does not yet demonstrate.
> **No final conclusion**. No performance claim. No publication readiness claim.

---

## 5.1 Discussion

### 5.11 What the current pipeline demonstrates

The current repository demonstrates that an offline, artifact-governed pipeline can transform real K1 forward-velocity measurement evidence into a chain of structured, reproducible research artifacts: a schema-valid dataset of 5 command-response records (4 numeric, 1 qualitative-only at the 0.10 m/s deadzone), conservative response predictions with categorical uncertainty labels, navigation-aware advisory risk assessments with explicit warning metadata, and a claim-governed evaluation package that separates supported structural claims from unsupported performance claims. Every pipeline stage has a documented input contract, a producer script, an output artifact, and a validation step. The demonstrated evidence is structural and artifact-level: it confirms that the pipeline is internally consistent and reproducible, not that it improves any navigation outcome.

### 5.12 Deployment-layer response modeling as a distinct problem

The command-to-motion response relationship at the deployment layer differs from locomotion policy training [@TanRSS2018] [@HwangboSciRobot2019], from online adaptation that modifies a controller at runtime [@KumarRMA2021] [@MargolisRSS2022], and from direct velocity compensation. In each of those settings, the practitioner has access to the controller, policy, or low-level actuation model. In contrast, the deployment-layer problem studied here operates under a closed-source constraint: the user commands velocity through an SDK-provided ROS2 topic and observes odometry feedback, but cannot inspect or modify the internal locomotion controller. Under this constraint, characterizing command-to-motion response becomes an externally observable measurement and modeling problem rather than a controller-design problem.

The project is positioned as a candidate contribution around black-box, closed-source deployment-layer response characterization. It does not claim that no prior work examines externally measured robot response, nor does it claim to solve closed-source calibration. It does claim — as a structural, artifact-backed claim — that the pipeline constructs, validates, and evaluates such a characterization from sparse real-robot evidence within a conservative claim-governance framework. Broader system-identification and commercial-SDK calibration literature review is needed before upgrading this candidate contribution.

### 5.13 Sparse-evidence uncertainty and reliability labels

Under sparse single-trial evidence, the M15R response model assigns categorical uncertainty and confidence labels (`low`, `medium`, `high`, `extreme`) rather than numerical probability estimates. This design choice is intentional and conservative. Categorical labels offer several advantages under sparse data: they avoid false precision from reporting numbers that a single trial cannot justify; they allow qualitative-only records (such as the 0.10 m/s deadzone) to carry meaningful metadata without numeric fabrication; and they surface regimes where prediction reliability is inherently limited, such as out-of-range queries or command velocities with only qualitative evidence on one side.

The downside is equally clear: these labels are not calibrated probabilities. They do not carry statistical confidence intervals, are not validated against repeated trials, and have not been tested against held-out command points or navigation outcomes. They serve as metadata flags for downstream interpretation, not as quantitative risk scores. Future work requiring calibrated uncertainty must collect sufficient repeated evidence and apply a dedicated calibration protocol.

### 5.14 Navigation-aware risk mapping as advisory interpretation

The M16 risk mapping layer translates response predictions into advisory risk assessments that can inform downstream planning analysis. The mapping is rule-based and offline: for each query velocity, the mapper inspects the prediction type, qualitative response label, uncertainty, and confidence, then assigns a tracking reliability category, a navigation risk level (`low-risk`, `moderate-risk`, `high-risk`, `critical`), and a warning category (deadzone, weak tracking, under tracking, high uncertainty). This helps identify velocity regimes where the robot may not track commands as reliably as a planner might assume — deadzone behavior at low speeds, under-tracking at higher speeds, and prediction uncertainty at the edges of available evidence.

Critically, the risk mapping layer does not control the robot. It does not trigger automatic compensation, does not compute inverse command mappings, does not issue robot motion commands, and does not adapt navigation plans in real time. The 5 current risk assessments (1 critical, 2 high-risk, 2 medium-risk) reflect model-internal evaluation of response evidence quality, not validated navigation outcomes. Whether these advisory warnings would reduce collisions, near-misses, or navigation failures if incorporated into a planner remains an open question requiring separate navigation trials. The mapping is useful as a structured, auditable interpretation of low-level response evidence — not as a safety guarantee.

### 5.15 Claim-governed evaluation and evidence discipline

A distinctive aspect of this repository is the claim-governance infrastructure that accompanies the pipeline: a claim registry (`paper/claims/claim_registry.md`), an evidence table (`paper/claims/evidence_table.md`), a non-claims file (`paper/claims/non_claims.md`), and milestone-specific claim audits (P3-P6). These artifacts enforce a clear separation between structural claims supported by project artifacts, context claims supported by prior literature, candidate contributions that require more evidence, and claims that are explicitly prohibited.

This governance layer matters for two reasons. First, it prevents overstating sparse real-robot evidence: at every pipeline stage, the method explicitly records what it does not implement (compensation, inverse mapping, navigation control, safe command adaptation) and what it does not yet evaluate (collision rates, success rates, calibrated uncertainty). Second, it provides a transparent audit trail for reviewers and future contributors, making it clear which claims are ready for manuscript use and which require additional experiments or literature review. The claim-upgrade requirements table (`paper/tables/claim_upgrade_requirements_table.md`) documents exactly what evidence would be needed to move each candidate contribution into a supported claim.

---

## 5.6 Limitations

### 5.61 Dataset limitations

The current velocity response dataset consists of 5 records from a single K1 quadruped unit on a single indoor floor surface within a single test session. Of these, 4 records include numeric actual velocity values (commands at 0.30, 0.40, 0.45, and 0.50 m/s), while the 0.10 m/s record is qualitative-only — the robot's actual displacement at this commanded velocity was too small to measure meaningfully under the current odometry-based protocol, so the record carries a `deadzone` label without a fabricated numeric response. No repeated trials per command velocity exist, making it impossible to estimate response variance, to evaluate held-out prediction error, or to assess measurement repeatability. The dataset covers only forward linear velocity (`v_x`); lateral velocity (`v_y`) and angular velocity (`omega_z`) are schema-supported fields reserved for future measurement expansion. Additional response dimensions — yaw drift, lateral drift, response delay, and stop distance — are not available. `battery_state` remains an optional field and is not required for pipeline operation.

### 5.62 Response-model limitations

The response model `uncertainty_aware_hybrid_v1` is a lightweight, rule-based model, not a learned or parametric statistical model. It handles exact numeric matches, qualitative-only records, bounded interpolation, and out-of-range queries through deterministic rules. The exact-source reconstruction check (MAE = 0.0 m/s) confirms only that the model retrieves its own input correctly — it is a structural sanity check, not evidence of predictive accuracy. The model has not been evaluated on held-out data, has not been compared against external ground truth (e.g., motion capture), and does not produce calibrated confidence intervals. Its behavior outside the evaluated command range — including extrapolation to higher speeds, different surfaces, or different payload conditions — is unknown and would be conservatively labeled as high-uncertainty. The three baseline model hooks are retained for future comparison readiness and have not been evaluated competitively.

### 5.63 Risk-mapping limitations

The navigation risk mapper operates entirely offline and produces advisory classifications from model prediction attributes. Its warning categories and risk levels are derived from qualitative heuristics — deadzone status, tracking category, uncertainty level — rather than from empirical navigation outcome data. No real navigation trials have been conducted: the pipeline has no collision-rate data, no near-miss-rate data, no navigation success or failure statistics, and no path-deviation measurements. The current risk map cannot be interpreted as validated navigation-risk evidence, and the advisory warnings have not been tested against planner behavior.

### 5.64 System and scope limitations

The pipeline is deliberately constrained in scope. It does not implement velocity compensation (adjusting commands to pre-correct for response mismatch), inverse command mapping (computing the command needed to achieve a desired actual velocity), a navigation controller, or a safe command adapter. It does not assume any unconfirmed ROS2 topics, does not use `remote_controller_state`, and treats `battery_state` as optional rather than required. These constraints are safety-oriented design choices that prevent the pipeline from issuing unintended robot commands. They also define the current scope boundary: the pipeline stops at advisory output and does not close the loop to robot control.

### 5.65 Generalization limitations

All current evidence comes from a single K1 unit on a single indoor hard floor during a single session. The pipeline has not been tested on additional K1 units, on different legged robot platforms, across distinct floor surfaces (e.g., carpet, outdoor pavement, grass), or under varying payload or battery conditions. It has not been evaluated on lateral or angular velocity commands. Claims about generalization across robots, environments, or command dimensions are not supported and would require dedicated multi-robot, multi-surface, and multi-dimensional experimental protocols.

---

## 5.11 Future Work

### 5.111 Experimental expansion

The most immediate priority is expanding the measurement base. This includes collecting repeated forward-velocity trials (at least 3-5 per command velocity) to estimate response variability; extending the command grid to include `v_y` and `omega_z` dimensions; testing across multiple floor surfaces; and recording the currently missing response dimensions — yaw drift, lateral drift, response delay, and stop distance. Where available, optional context such as battery level, payload, and gait mode should be recorded to support future conditional modeling.

### 5.112 Navigation outcome evaluation

To upgrade any navigation-aware claim beyond "advisory interpretation," controlled navigation task trials are required. A fixed navigation protocol should be defined, and trials should be conducted both with and without the advisory risk layer integrated into the planning system. Outcome metrics — collision rate, near-miss rate, navigation success rate, and path deviation — must be collected under repeatable conditions. Only after such trials can the relationship between advisory risk warnings and real navigation outcomes be assessed.

### 5.113 Toward calibrated uncertainty

If probability-calibrated uncertainty is desired for downstream use, sufficient repeated trials must be collected to estimate empirical variance. A calibration protocol — including held-out evaluation on command points not used for model construction — should be applied to produce calibrated confidence intervals. The current categorical labels would then be compared against empirically derived uncertainty estimates to assess whether the conservative labeling strategy is appropriately cautious or overly pessimistic.

### 5.114 Toward command adaptation

Velocity compensation, inverse command mapping, and safe command adaptation should be considered only after the evidence base is substantially stronger — multi-trial, multi-surface, multi-session data with held-out evaluation. Even then, any command adaptation logic must be validated under controlled conditions before being used on a real robot. The current risk mapping layer should not be directly converted into control actions without experimental validation of the mapping's correspondence to real navigation outcomes.

---

## 5.15 Discussion Summary

The current artifact-governed pipeline provides a conservative, reproducible research foundation for black-box command-to-motion response characterization of a closed-source legged robot. The pipeline demonstrates that sparse real-robot evidence can be structured into a schema-valid dataset, used to generate conservative response predictions with explicit uncertainty labeling, and translated into advisory risk assessments with clear scope boundaries. The claim-governance infrastructure ensures that every statement about the pipeline's capabilities is traceable to a specific artifact or explicitly documented as unsupported.

Current evidence supports structural claims: the pipeline exists, is reproducible, and produces consistent outputs given its sparse inputs. Current evidence does not support performance claims, safety claims, or generalization claims. All such claims require future experiments — repeated trials, multi-surface testing, expanded command dimensions, and controlled navigation task protocols — before they can be upgraded from candidate contributions to supported findings.

This discussion is not a final conclusion. A manuscript conclusion should be written only after the full manuscript is assembled (P8) and all sections are reviewed together for consistency, claim boundaries, and missing evidence.



---

# 6. Conclusion

**[PLACEHOLDER — final conclusion intentionally not written in P8. A conclusion should be written after cross-section consistency audit (P8), after all claim boundaries are verified, and after the abstract is drafted.]**

---

## Planned Figures

- Method pipeline figure: specification at `paper/figures/method_pipeline_figure_spec.md`
- Evidence chain / claim-governance figure: specification at `paper/figures/evidence_chain_figure_spec.md`
- Additional figures may be generated in M19

## Planned Tables

- Method artifact evidence table: `paper/tables/method_artifact_evidence_table.md`
- Current metrics and missing evidence table: `paper/tables/current_metrics_and_missing_evidence_table.md`
- Method stage I/O contract table: `paper/tables/method_stage_io_contract_table.md`
- Method algorithm summary table: `paper/tables/method_algorithm_summary_table.md`
- Experiment metrics status table: `paper/tables/experiment_metrics_status_table.md`
- Evaluation question artifact map: `paper/tables/evaluation_question_artifact_map.md`
- Claim upgrade requirements table: `paper/tables/claim_upgrade_requirements_table.md`
- Terminology consistency table: `paper/tables/terminology_consistency_table.md`
- Manuscript section status table: `paper/tables/manuscript_section_status_table.md`

## Current Claim Boundaries

All claims in this assembled manuscript are governed by:
- `paper/claims/claim_registry.md`
- `paper/claims/evidence_table.md`
- `paper/claims/non_claims.md`
- `paper/claims/m18_claim_audit.md`
- Milestone-specific claim audits: `paper/claims/p3_*`, `p4_*`, `p5_*`, `p6_*`, `p7_*`, `p8_*`

**Key boundaries**:
- No final novelty claim. No performance superiority claim. No navigation safety improvement claim.
- Uncertainty labels are categorical, not calibrated probabilities.
- Risk map is advisory/offline, not navigation control.
- Compensation, inverse command mapping, and safe command adapter are not implemented.
- Publication readiness is not claimed.

## Assembly Notes

- Assembled: 2026-06-10, P8 milestone.
- Source files preserved at `paper/manuscript/sections/`.
- Section heading numbering has been normalized for manuscript flow.
- Abstract and Conclusion are intentionally placeholders.
- No section content has been altered beyond heading normalization.
- Consistency audit at `paper/manuscript/manuscript_v0_consistency_audit.md`.
