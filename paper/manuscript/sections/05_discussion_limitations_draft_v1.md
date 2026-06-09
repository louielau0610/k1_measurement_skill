# Discussion and Limitations Draft v1

> **Status**: draft only — not a final manuscript section.
> **Basis**: synthesizes P3-P6 manuscript drafts, M17/M18 evaluation artifacts, and claim-governance documents.
> **Structural evidence only**: current discussion describes what the pipeline demonstrates and what it does not yet demonstrate.
> **No final conclusion**. No performance claim. No publication readiness claim.

---

## 5. Discussion

### 5.1 What the current pipeline demonstrates

The current repository demonstrates that an offline, artifact-governed pipeline can transform real K1 forward-velocity measurement evidence into a chain of structured, reproducible research artifacts: a schema-valid dataset of 5 command-response records (4 numeric, 1 qualitative-only at the 0.10 m/s deadzone), conservative response predictions with categorical uncertainty labels, navigation-aware advisory risk assessments with explicit warning metadata, and a claim-governed evaluation package that separates supported structural claims from unsupported performance claims. Every pipeline stage has a documented input contract, a producer script, an output artifact, and a validation step. The demonstrated evidence is structural and artifact-level: it confirms that the pipeline is internally consistent and reproducible, not that it improves any navigation outcome.

### 5.2 Deployment-layer response modeling as a distinct problem

The command-to-motion response relationship at the deployment layer differs from locomotion policy training [@TanRSS2018] [@HwangboSciRobot2019], from online adaptation that modifies a controller at runtime [@KumarRMA2021] [@MargolisRSS2022], and from direct velocity compensation. In each of those settings, the practitioner has access to the controller, policy, or low-level actuation model. In contrast, the deployment-layer problem studied here operates under a closed-source constraint: the user commands velocity through an SDK-provided ROS2 topic and observes odometry feedback, but cannot inspect or modify the internal locomotion controller. Under this constraint, characterizing command-to-motion response becomes an externally observable measurement and modeling problem rather than a controller-design problem.

The project is positioned as a candidate contribution around black-box, closed-source deployment-layer response characterization. It does not claim that no prior work examines externally measured robot response, nor does it claim to solve closed-source calibration. It does claim — as a structural, artifact-backed claim — that the pipeline constructs, validates, and evaluates such a characterization from sparse real-robot evidence within a conservative claim-governance framework. Broader system-identification and commercial-SDK calibration literature review is needed before upgrading this candidate contribution.

### 5.3 Sparse-evidence uncertainty and reliability labels

Under sparse single-trial evidence, the M15R response model assigns categorical uncertainty and confidence labels (`low`, `medium`, `high`, `extreme`) rather than numerical probability estimates. This design choice is intentional and conservative. Categorical labels offer several advantages under sparse data: they avoid false precision from reporting numbers that a single trial cannot justify; they allow qualitative-only records (such as the 0.10 m/s deadzone) to carry meaningful metadata without numeric fabrication; and they surface regimes where prediction reliability is inherently limited, such as out-of-range queries or command velocities with only qualitative evidence on one side.

The downside is equally clear: these labels are not calibrated probabilities. They do not carry statistical confidence intervals, are not validated against repeated trials, and have not been tested against held-out command points or navigation outcomes. They serve as metadata flags for downstream interpretation, not as quantitative risk scores. Future work requiring calibrated uncertainty must collect sufficient repeated evidence and apply a dedicated calibration protocol.

### 5.4 Navigation-aware risk mapping as advisory interpretation

The M16 risk mapping layer translates response predictions into advisory risk assessments that can inform downstream planning analysis. The mapping is rule-based and offline: for each query velocity, the mapper inspects the prediction type, qualitative response label, uncertainty, and confidence, then assigns a tracking reliability category, a navigation risk level (`low-risk`, `moderate-risk`, `high-risk`, `critical`), and a warning category (deadzone, weak tracking, under tracking, high uncertainty). This helps identify velocity regimes where the robot may not track commands as reliably as a planner might assume — deadzone behavior at low speeds, under-tracking at higher speeds, and prediction uncertainty at the edges of available evidence.

Critically, the risk mapping layer does not control the robot. It does not trigger automatic compensation, does not compute inverse command mappings, does not issue robot motion commands, and does not adapt navigation plans in real time. The 5 current risk assessments (1 critical, 2 high-risk, 2 medium-risk) reflect model-internal evaluation of response evidence quality, not validated navigation outcomes. Whether these advisory warnings would reduce collisions, near-misses, or navigation failures if incorporated into a planner remains an open question requiring separate navigation trials. The mapping is useful as a structured, auditable interpretation of low-level response evidence — not as a safety guarantee.

### 5.5 Claim-governed evaluation and evidence discipline

A distinctive aspect of this repository is the claim-governance infrastructure that accompanies the pipeline: a claim registry (`paper/claims/claim_registry.md`), an evidence table (`paper/claims/evidence_table.md`), a non-claims file (`paper/claims/non_claims.md`), and milestone-specific claim audits (P3-P6). These artifacts enforce a clear separation between structural claims supported by project artifacts, context claims supported by prior literature, candidate contributions that require more evidence, and claims that are explicitly prohibited.

This governance layer matters for two reasons. First, it prevents overstating sparse real-robot evidence: at every pipeline stage, the method explicitly records what it does not implement (compensation, inverse mapping, navigation control, safe command adaptation) and what it does not yet evaluate (collision rates, success rates, calibrated uncertainty). Second, it provides a transparent audit trail for reviewers and future contributors, making it clear which claims are ready for manuscript use and which require additional experiments or literature review. The claim-upgrade requirements table (`paper/tables/claim_upgrade_requirements_table.md`) documents exactly what evidence would be needed to move each candidate contribution into a supported claim.

---

## 6. Limitations

### 6.1 Dataset limitations

The current velocity response dataset consists of 5 records from a single K1 quadruped unit on a single indoor floor surface within a single test session. Of these, 4 records include numeric actual velocity values (commands at 0.30, 0.40, 0.45, and 0.50 m/s), while the 0.10 m/s record is qualitative-only — the robot's actual displacement at this commanded velocity was too small to measure meaningfully under the current odometry-based protocol, so the record carries a `deadzone` label without a fabricated numeric response. No repeated trials per command velocity exist, making it impossible to estimate response variance, to evaluate held-out prediction error, or to assess measurement repeatability. The dataset covers only forward linear velocity (`v_x`); lateral velocity (`v_y`) and angular velocity (`omega_z`) are schema-supported fields reserved for future measurement expansion. Additional response dimensions — yaw drift, lateral drift, response delay, and stop distance — are not available. `battery_state` remains an optional field and is not required for pipeline operation.

### 6.2 Response-model limitations

The response model `uncertainty_aware_hybrid_v1` is a lightweight, rule-based model, not a learned or parametric statistical model. It handles exact numeric matches, qualitative-only records, bounded interpolation, and out-of-range queries through deterministic rules. The exact-source reconstruction check (MAE = 0.0 m/s) confirms only that the model retrieves its own input correctly — it is a structural sanity check, not evidence of predictive accuracy. The model has not been evaluated on held-out data, has not been compared against external ground truth (e.g., motion capture), and does not produce calibrated confidence intervals. Its behavior outside the evaluated command range — including extrapolation to higher speeds, different surfaces, or different payload conditions — is unknown and would be conservatively labeled as high-uncertainty. The three baseline model hooks are retained for future comparison readiness and have not been evaluated competitively.

### 6.3 Risk-mapping limitations

The navigation risk mapper operates entirely offline and produces advisory classifications from model prediction attributes. Its warning categories and risk levels are derived from qualitative heuristics — deadzone status, tracking category, uncertainty level — rather than from empirical navigation outcome data. No real navigation trials have been conducted: the pipeline has no collision-rate data, no near-miss-rate data, no navigation success or failure statistics, and no path-deviation measurements. The current risk map cannot be interpreted as validated navigation-risk evidence, and the advisory warnings have not been tested against planner behavior.

### 6.4 System and scope limitations

The pipeline is deliberately constrained in scope. It does not implement velocity compensation (adjusting commands to pre-correct for response mismatch), inverse command mapping (computing the command needed to achieve a desired actual velocity), a navigation controller, or a safe command adapter. It does not assume any unconfirmed ROS2 topics, does not use `remote_controller_state`, and treats `battery_state` as optional rather than required. These constraints are safety-oriented design choices that prevent the pipeline from issuing unintended robot commands. They also define the current scope boundary: the pipeline stops at advisory output and does not close the loop to robot control.

### 6.5 Generalization limitations

All current evidence comes from a single K1 unit on a single indoor hard floor during a single session. The pipeline has not been tested on additional K1 units, on different legged robot platforms, across distinct floor surfaces (e.g., carpet, outdoor pavement, grass), or under varying payload or battery conditions. It has not been evaluated on lateral or angular velocity commands. Claims about generalization across robots, environments, or command dimensions are not supported and would require dedicated multi-robot, multi-surface, and multi-dimensional experimental protocols.

---

## 7. Future Work

### 7.1 Experimental expansion

The most immediate priority is expanding the measurement base. This includes collecting repeated forward-velocity trials (at least 3-5 per command velocity) to estimate response variability; extending the command grid to include `v_y` and `omega_z` dimensions; testing across multiple floor surfaces; and recording the currently missing response dimensions — yaw drift, lateral drift, response delay, and stop distance. Where available, optional context such as battery level, payload, and gait mode should be recorded to support future conditional modeling.

### 7.2 Navigation outcome evaluation

To upgrade any navigation-aware claim beyond "advisory interpretation," controlled navigation task trials are required. A fixed navigation protocol should be defined, and trials should be conducted both with and without the advisory risk layer integrated into the planning system. Outcome metrics — collision rate, near-miss rate, navigation success rate, and path deviation — must be collected under repeatable conditions. Only after such trials can the relationship between advisory risk warnings and real navigation outcomes be assessed.

### 7.3 Toward calibrated uncertainty

If probability-calibrated uncertainty is desired for downstream use, sufficient repeated trials must be collected to estimate empirical variance. A calibration protocol — including held-out evaluation on command points not used for model construction — should be applied to produce calibrated confidence intervals. The current categorical labels would then be compared against empirically derived uncertainty estimates to assess whether the conservative labeling strategy is appropriately cautious or overly pessimistic.

### 7.4 Toward command adaptation

Velocity compensation, inverse command mapping, and safe command adaptation should be considered only after the evidence base is substantially stronger — multi-trial, multi-surface, multi-session data with held-out evaluation. Even then, any command adaptation logic must be validated under controlled conditions before being used on a real robot. The current risk mapping layer should not be directly converted into control actions without experimental validation of the mapping's correspondence to real navigation outcomes.

---

## 8. Discussion Summary

The current artifact-governed pipeline provides a conservative, reproducible research foundation for black-box command-to-motion response characterization of a closed-source legged robot. The pipeline demonstrates that sparse real-robot evidence can be structured into a schema-valid dataset, used to generate conservative response predictions with explicit uncertainty labeling, and translated into advisory risk assessments with clear scope boundaries. The claim-governance infrastructure ensures that every statement about the pipeline's capabilities is traceable to a specific artifact or explicitly documented as unsupported.

Current evidence supports structural claims: the pipeline exists, is reproducible, and produces consistent outputs given its sparse inputs. Current evidence does not support performance claims, safety claims, or generalization claims. All such claims require future experiments — repeated trials, multi-surface testing, expanded command dimensions, and controlled navigation task protocols — before they can be upgraded from candidate contributions to supported findings.

This discussion is not a final conclusion. A manuscript conclusion should be written only after the full manuscript is assembled (P8) and all sections are reviewed together for consistency, claim boundaries, and missing evidence.
