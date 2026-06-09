# P2 Gap Analysis v1

中文优先说明：P2 将 P1 seed literature matrix 和 M13-M17 project artifacts 对齐，形成 gap analysis 与 contribution positioning。P2 不写完整 introduction 或 related-work section，不声称 final novelty，不声称 performance superiority，也不声称 publication readiness。

## Purpose of P2

P2 的目的不是扩大工程功能，而是把现有文献证据、项目 artifact 和 claim governance 放到同一个分析框架中，明确哪些内容可以作为 context claim，哪些内容只能作为 candidate contribution，哪些内容必须等待更多文献或实验。

## Input Artifacts Used

- P1 literature matrix: `paper/related_work/literature_matrix.md`
- P1 notes: `paper/related_work/notes/`
- P1 gap candidates: `paper/claims/literature_gap_candidates.md`
- M17 pipeline evaluation: `outputs/research_evaluation/m17_pipeline_evaluation_report.json`
- Claim registry: `paper/claims/claim_registry.md`
- Evidence table: `paper/claims/evidence_table.md`
- Non-claims: `paper/claims/non_claims.md`

P2 used P1 literature only. No extra search was added.

## Prior Work Cluster Analysis

### Cluster 1: Sim-to-real and learned legged locomotion

- Representative papers: `TanRSS2018`, `HwangboSciRobot2019`, `RudinCoRL2021`, `MaRSS2024DrEureka`.
- What they address: simulation-to-real transfer, learned locomotion, actuator/latency modeling, domain randomization, and policy-training workflows.
- What they do not address: they do not establish closed-source SDK-level command-to-motion calibration as a separate deployment artifact, and they generally assume policy, simulator, or controller access.
- Relation to our project: M14-M15R provide measured response artifacts and conservative labels for a fixed K1 deployment context, without training a locomotion controller.
- Safe interpretation: sim-to-real and learned locomotion work supports the broader claim that deployment mismatch matters.
- Prohibited interpretation: do not claim our pipeline solves sim-to-real transfer, outperforms these methods, or produces a trained locomotion policy.

### Cluster 2: Rapid motor adaptation / deployment adaptation

- Representative papers: `KumarRMA2021`, `MargolisRSS2022`, `MargolisCoRL2022`.
- What they address: online adaptation, behavior diversity, velocity-command curricula, and real deployment robustness.
- What they do not address: they do not establish a measurement-only calibration pipeline for a closed-source robot where the user cannot modify the locomotion policy.
- Relation to our project: M15R labels uncertainty/reliability from sparse response evidence; it does not adapt control online.
- Safe interpretation: deployment adaptation literature makes response mismatch a credible problem context.
- Prohibited interpretation: do not describe M15R as rapid adaptation or claim controller robustness.

### Cluster 3: Perceptive / navigation-coupled legged locomotion

- Representative papers: `FuCVPRW2022`, `GrandiaTRO2023`, `GangapurwalaArxiv2020`, `FanRSS2021STEP`.
- What they address: navigation-locomotion coupling, proprioceptive safety signals, terrain-aware planning, perception-aware control, and risk-aware traversal.
- What they do not address: P1 did not find strong evidence that these works derive planner advisory risk labels specifically from externally measured command-to-motion response mismatch.
- Relation to our project: M16 maps response-model predictions to offline advisory risk categories but does not control a planner or robot.
- Safe interpretation: prior work supports the relevance of coupling low-level capability with navigation decisions.
- Prohibited interpretation: do not claim M16 improves navigation outcomes, reduces collision, or implements navigation control.

### Cluster 4: Risk-aware / uncertainty-aware navigation and deployment

- Representative papers: `FanRSS2021STEP`, `FanArxiv2021Costmaps`, `BenrabahSensors2024`, `FrancisTOHRI2025`.
- What they address: traversability risk, cost distributions, CVaR-style tail-risk reasoning, and navigation evaluation guidelines.
- What they do not address: they do not validate our response-derived risk labels, and the P1 evidence does not establish calibrated probabilities for our labels.
- Relation to our project: M15R/M16 create uncertainty/confidence and risk labels as conservative metadata.
- Safe interpretation: uncertainty-aware navigation literature provides vocabulary and evaluation pressure for future experiments.
- Prohibited interpretation: do not call current labels calibrated risk probabilities or safety guarantees.

### Cluster 5: Field robotics metrics and evaluation

- Representative papers: `BenrabahSensors2024`, `FrancisTOHRI2025`, `FanRSS2021STEP`, `GangapurwalaArxiv2020`.
- What they address: success, safety, traversal, risk, and field evaluation metrics.
- What they do not address: they do not provide project evidence for K1 collision rate, near-miss rate, success rate, or safety improvement.
- Relation to our project: M17 explicitly lists unavailable metrics and next experiments.
- Safe interpretation: these works justify why future performance/safety claims need real navigation trials and outcome metrics.
- Prohibited interpretation: do not treat structural pipeline validation as field performance validation.

### Cluster 6: Black-box system identification / command-response calibration

- Representative papers: `TanRSS2018`, `YangRAL2022`, `DaoArxiv2026`, `MargolisRSS2022`.
- What they address: system identification, kinematic calibration, simulator adaptation, and online identification.
- What they do not address: current P1 evidence is not enough to prove an open gap for closed-source deployment-layer command-to-motion calibration.
- Relation to our project: M13-M15R define schema, dataset, and response-model foundations for black-box command-response measurement.
- Safe interpretation: this is the strongest candidate gap, but it needs broader system-identification search before novelty language.
- Prohibited interpretation: do not claim the project is the first closed-source command-response calibration method.

## Cluster-by-Cluster Comparison

The strongest overlap with prior work is the shared recognition that legged robot deployment mismatch matters. The strongest current differentiation is artifact governance around externally measured command response under a conservative claim boundary. The weakest area is experimental evidence: current artifacts are sparse, single-robot, single-session, and not navigation-outcome validated.

## Candidate Gaps Retained

- Closed-source / black-box deployment-layer command-to-motion calibration: retained as `candidate_gap`, requires more literature and experiment.
- Navigation-aware interpretation of low-level velocity response mismatch: retained as `candidate_gap`, requires planner/outcome experiments.
- Uncertainty/reliability labels as bridge between response modeling and planner advisory: retained as `candidate_gap`, requires calibration and navigation trials.
- Artifact-governed pipeline from measurement to risk map: retained as `candidate_gap`, requires reproducibility/artifact-governance literature comparison.

## Candidate Gaps Weakened or Deferred

- Any claim that the approach is novel: deferred.
- Any claim that response labels are calibrated uncertainty: deferred.
- Any claim that advisory risk labels improve navigation safety: deferred.
- Any claim that closed-source deployment-layer calibration is absent from prior work: deferred until P2/P3 follow-up search.

## Risks of Overclaiming

- Treating literature context as novelty evidence.
- Treating structural software validation as performance evidence.
- Treating sparse single-session K1 data as generalizable.
- Treating uncertainty/confidence labels as calibrated probabilities.
- Treating an offline advisory map as navigation control or safety improvement.

## Additional Literature Needed

- Broader black-box system identification and command-response calibration literature.
- Commercial quadruped SDK deployment and calibration literature.
- Planner-controller mismatch and advisory-layer navigation literature.
- Robotics artifact governance, reproducibility, and benchmark-reporting literature.

## Additional Experiments Needed

- Repeated velocity-response trials per command velocity.
- Multi-surface and multi-session K1 response collection.
- Command grid including `vx` and `wz`.
- Delay, stop-distance, yaw drift, and lateral drift measurement.
- Navigation task trials with outcome metrics.
- Baseline comparisons under a fixed protocol.

## Safe Positioning Summary

The current safe framing is: this repository contains an artifact-governed, measurement-to-model-to-risk-map research pipeline for black-box K1 command-response analysis, and P1/P2 identify plausible contribution candidates. It is not yet a final novelty claim, not a full paper, not a performance evaluation, not a compensation method, and not a navigation safety proof.

