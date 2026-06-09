# M18 Claim Audit

## Purpose

中文优先说明：M18 claim audit 把当前 manuscript scaffold 可以使用的说法、需要更多证据的说法和禁止说法分开。M18 不建立 final novelty，不建立 performance superiority，不建立 publication readiness。

## Inputs inspected

- M13-M17 method and evaluation artifacts。
- P1 literature matrix and notes。
- P2 gap analysis and contribution candidates。
- `paper/claims/claim_registry.md`
- `paper/claims/evidence_table.md`
- `paper/claims/non_claims.md`
- `paper/claims/claim_upgrade_plan.md`

## Supported structural/software claims

- The repository implements an offline artifact-governed pipeline from dataset schema to response predictions, advisory risk map, and claim evaluation。
- Velocity response dataset v1 exists and contains sparse Measurement v0-derived evidence。
- M15R response model outputs uncertainty/confidence labels, with explicit limitations。
- M16 risk map outputs offline advisory warning metadata。
- M17/M18 claim governance separates structural evidence from unsupported performance claims。

## Literature-supported context claims

- Prior work makes legged robot deployment mismatch, sim-to-real transfer, adaptation, system identification, navigation/locomotion coupling, and risk-aware evaluation relevant contexts。
- P1/P2 literature evidence remains context evidence, not novelty proof。

## Candidate contributions

- Artifact-governed black-box command-to-motion response pipeline。
- Measurement-to-dataset-to-model workflow for closed-source K1 velocity response。
- Sparse-evidence uncertainty/reliability labels。
- Navigation-aware risk interpretation of low-level velocity-response mismatch。
- Claim-governed evaluation package。

## Claims requiring more experiments

- prediction accuracy。
- calibrated uncertainty。
- navigation warning correctness。
- collision / near-miss / success-rate impact。
- multi-surface, multi-session, or cross-robot generalization。

## Claims requiring more literature

- final novelty relative to black-box system identification。
- final novelty relative to commercial quadruped SDK calibration。
- final novelty of artifact governance in robotics deployment papers。

## Prohibited claims

- improved navigation safety。
- reduced collision rate。
- reduced near-miss rate。
- improved navigation success rate。
- performance superiority。
- compensation readiness。
- safe command adapter readiness。
- publication readiness。

## Wording recommendations

- Use "offline artifact-governed pipeline"。
- Use "structural/software validation"。
- Use "candidate contribution"。
- Use "uncertainty/confidence labels, not calibrated probabilities"。
- Use "advisory risk metadata, not navigation control"。

## Wording to avoid

- "improves navigation safety"。
- "reduces collisions"。
- "outperforms prior work"。
- "solves closed-source robot calibration"。
- "generalizes to all legged robots"。
- "calibrated uncertainty estimates"。
- "ready for safe command adaptation"。

| claim_or_wording | status | evidence | missing_evidence | allowed_wording | prohibited_wording |
| --- | --- | --- | --- | --- | --- |
| The repository implements an offline artifact-governed pipeline. | supported structural/software claim | M13-M18 artifacts | none for existence | "implements an offline artifact-governed pipeline" | "validated performance pipeline" |
| The current dataset contains sparse single-robot Measurement v0 evidence. | supported structural/software claim | M14 dataset; M17 report | larger dataset for generalization | "sparse single-robot evidence" | "generalizes to legged robots" |
| The response model emits uncertainty/confidence labels. | supported structural/software claim | M15R outputs | calibration protocol | "labels, not calibrated probabilities" | "calibrated probabilities" |
| The risk map provides advisory metadata. | supported structural/software claim | M16 outputs | navigation outcome trials | "offline advisory risk metadata" | "navigation controller" |
| Navigation-aware risk interpretation is a candidate contribution. | candidate contribution | M16/M17/P2 artifacts | navigation outcomes and broader literature | "candidate contribution" | "improves navigation safety" |
| Claim governance separates structural from performance evidence. | candidate contribution | M17/P1/P2/M18 claim artifacts | artifact-governance literature comparison | "claim-governed evaluation package" | "publication-ready evidence" |
| Collision-rate reduction. | non-claim | none | collision outcome protocol and data | "not available yet" | "reduces collisions" |
| Performance superiority. | non-claim | none | baseline comparison and statistics | "requires future comparison" | "outperforms prior work" |

