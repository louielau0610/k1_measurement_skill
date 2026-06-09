# Method Draft v1

> **Status**: draft only — not a final manuscript section.
> **Basis**: derived from M13-M18 method artifacts, P2 gap analysis, and P4 Introduction/Problem Statement.
> **Not a novelty claim**. Not a performance claim. Not a full manuscript. No compensation, inverse mapping, navigation control, or safe command adapter is implemented.

---

## 3. Method Overview

This work implements an offline, artifact-governed pipeline for characterizing the black-box command-to-motion response of a closed-source legged robot. The pipeline maps real measurement artifacts through five stages: (1) measurement artifact construction and structuring, (2) velocity response dataset construction under a research schema, (3) conservative uncertainty-aware response modeling, (4) offline navigation-aware reliability and risk mapping, and (5) claim-governed pipeline evaluation. All stages produce structured, reproducible output artifacts with explicit input/output contracts and safety flags. The method does not implement velocity compensation, inverse command mapping, real-time navigation control, or safe command adaptation. A planned pipeline figure (specification at `paper/figures/method_pipeline_figure_spec.md`) illustrates the artifact flow.

## 3.1 System Boundary and Assumptions

**System boundary**. The robot is treated as a closed-source command-execution system. The user operates through an SDK-provided velocity command interface and receives odometry feedback, but has no access to the internal locomotion controller, state estimator parameters, actuator model, or proprietary SDK internals. The method uses only externally observable or already-available structured artifacts.

**Assumptions**:
- A ROS2-based velocity command topic and an odometry feedback topic are available for read-only logging.
- Commanded body-frame velocities `[v_x^cmd, v_y^cmd, omega_z^cmd]` can be recorded alongside odometry-derived actual velocities `[v_x^actual, v_y^actual, omega_z^actual]`.
- Measurement environment (floor type, session identifier) is documented.
- `battery_state` is optional and not required for pipeline operation.
- `remote_controller_state` is permanently out of scope and excluded from all research schema artifacts.
- No unconfirmed ROS2 topics are used.

**Explicit non-goals**. This is not controller tuning. This is not policy training. This is not velocity compensation. This is not real-time navigation control. The method is confined to offline measurement, modeling, and advisory interpretation of existing sensor logs.

## 3.2 Problem Formulation

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

## 3.3 Stage 1 — Measurement Artifact Construction

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

## 3.4 Stage 2 — Velocity Response Dataset Construction

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

## 3.5 Stage 3 — Uncertainty-Aware Velocity Response Modeling

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

## 3.6 Stage 4 — Navigation-Aware Reliability and Risk Mapping

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

## 3.7 Stage 5 — Claim-Governed Evaluation

The pipeline evaluation stage (`scripts/generate_research_pipeline_evaluation_v1.py`) consolidates all upstream artifacts into a structured evaluation package that explicitly separates structural/software validation from unsupported performance claims.

**Evaluation categories**:
- **Structural/software validation**: confirms that artifacts exist, are JSON-valid, conform to their schema, and are reproducible via documented scripts.
- **Dataset evidence summary**: records the number of dataset records, numeric vs. qualitative-only counts, and command range covered.
- **Model sanity checks**: verifies that exact-source numeric predictions are self-consistent and that qualitative-only records are not numerically fabricated.
- **Risk-map readiness evaluation**: reports risk-level and warning-category counts without interpreting them as navigation-safety evidence.
- **Real navigation outcome evaluation**: explicitly documented as *not available*; collision rate, near-miss rate, success rate, and path-deviation metrics are all listed as missing.

**Claim governance**: the evaluation package links to the project claim registry (`paper/claims/claim_registry.md`), evidence table (`paper/claims/evidence_table.md`), and non-claims (`paper/claims/non_claims.md`). These governance artifacts track which statements are supported by project evidence, supported by prior work, plausible but unverified, planned, or explicitly prohibited. This separation prevents the Method section from implying capabilities that the current pipeline does not possess.

## 3.8 Reproducibility and Artifact Traceability

Each pipeline stage produces traceable output artifacts through documented producer scripts. The following table summarizes the artifact chain:

| Stage | Producer script | Output artifact | Validation artifact |
| --- | --- | --- | --- |
| Schema definition | — (repository artifact) | `configs/velocity_response_dataset_schema_v1.json` | `scripts/validate_velocity_response_dataset_schema.py` |
| Dataset construction | `scripts/build_velocity_response_dataset_v1.py` | `outputs/research_datasets/velocity_response_dataset_v1.json` | `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` |
| Response modeling | `scripts/run_velocity_response_model_v1.py` | `outputs/research_models/response_model_predictions_v1.json` | `outputs/research_models/response_model_evaluation_v1.json` |
| Risk mapping | `scripts/run_navigation_risk_mapping_v1.py` | `outputs/research_risk/navigation_risk_map_v1.json` | `outputs/research_risk/navigation_risk_evaluation_v1.json` |
| Pipeline evaluation | `scripts/generate_research_pipeline_evaluation_v1.py` | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | `outputs/research_evaluation/m17_method_artifact_table.md` |

All producer scripts are runnable from the repository root and report clear error messages for missing inputs, invalid schemas, or fabricating operations. A more detailed artifact evidence table is maintained at `paper/tables/method_artifact_evidence_table.md`.

## 3.9 Scope and Current Limitations

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
