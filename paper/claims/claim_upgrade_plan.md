# Claim Upgrade Plan

中文优先说明：本文件定义 claim 如何从当前状态升级。P2 不升级任何 candidate gap 为 final novelty claim。

## Current Supported Structural / Software Claims

- M13-M17 artifacts exist and are reproducible where scripts exist.
- Velocity response dataset v1 exists and contains five Measurement v0-derived records.
- M15R response model foundation and M16 offline risk mapping can be rerun.
- M17 pipeline evaluation separates supported claims from non-claims.

## Current Literature-Supported Context Claims

- Prior work establishes sim-to-real mismatch, actuator/latency modeling, adaptation, and system identification as relevant contexts.
- Prior work establishes navigation/locomotion coupling, traversability risk, and navigation evaluation metrics as relevant contexts.

## Candidate Gap Claims

- Closed-source deployment-layer command-to-motion response calibration may be underexplored.
- Navigation-aware interpretation of low-level velocity-response mismatch may be a useful gap.
- Sparse-evidence uncertainty/reliability labels may bridge response modeling and planner advisory.
- Artifact-governed measurement-to-risk-map pipelines may be useful for claim governance.

## Claims That Require More Literature

- Novelty relative to black-box robot system identification.
- Novelty relative to commercial quadruped SDK calibration.
- Novelty relative to planner-controller mismatch and advisory risk layers.
- Novelty of artifact-governed robotics evaluation framing.

## Claims That Require More Experiments

- Generalization across surfaces, sessions, and K1 units.
- Prediction accuracy on held-out velocity-response trials.
- Calibrated uncertainty or confidence.
- Navigation safety improvement.
- Collision, near-miss, or success-rate change.

## Claims That Are Prohibited

- The current system improves navigation safety.
- The current system reduces collision rate.
- The current system outperforms prior work.
- The current system solves closed-source robot calibration.
- The current system generalizes to legged robots.
- The safe command adapter is ready.
- The current system is publication-ready.

| claim | current_status | current_evidence | missing_evidence | upgrade_condition | prohibited_wording |
| --- | --- | --- | --- | --- | --- |
| The repository contains a structural measurement-to-risk-map pipeline. | supported_structural_claim | M13-M17 artifacts; M17 report | None for structural existence | Keep as structural claim only. | "validated performance pipeline" |
| Prior work makes deployment mismatch relevant for legged robots. | literature_context_claim | P1 matrix and notes | Full-text synthesis for P3 | Use as context after P3 drafting. | "therefore our method is novel" |
| Closed-source deployment-layer response calibration is a candidate gap. | candidate_gap | P1/P2 positioning docs | Broader system-identification literature | Upgrade only after systematic review finds clear differentiation. | "solves closed-source robot calibration" |
| Response labels can support planner advisory interpretation. | requires_more_experiment | M15R/M16 artifacts; risk-aware literature | Navigation trials and calibrated labels | Upgrade only after outcome metrics and baseline comparisons. | "improves navigation safety" |
| Uncertainty labels are useful. | requires_more_experiment | M15R labels and P1 risk literature | Calibration and held-out evaluation | Upgrade only after repeated trials and uncertainty evaluation. | "calibrated probabilities" |
| Claim-governed evaluation is useful. | requires_more_literature | M17/P1/P2 governance artifacts | Reproducibility and artifact-governance literature | Upgrade only after literature comparison and reviewer-facing rationale. | "publication-ready evidence" |
| Performance superiority over prior work. | unsupported_do_not_claim | none | Comparative experiments and baselines | Only after protocol, baselines, and statistics exist. | "outperforms prior work" |
| Navigation safety improvement. | unsupported_do_not_claim | none | Real navigation outcome trials | Only after collision/near-miss/success metrics exist. | "reduces collision rate" |

