# Claim Registry

| claim_id | claim_text | claim_type | evidence_source | evidence_type | confidence | manuscript_ready | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M16-C1 | The repository contains an offline navigation-aware risk mapping layer that converts M15R response predictions into advisory risk assessments. | supported_by_our_experiment | `outputs/research_risk/navigation_risk_map_v1.json` | software artifact validation | medium | no | This is a structural/software claim, not a real navigation performance claim. |
| M16-NC1 | M16 demonstrates improved real-world navigation safety. | unsupported_and_must_not_be_stated | none | none | none | no | No real navigation outcome experiment has been run. |
| M16-NC2 | M16 demonstrates reduced collision, near-miss, or navigation failure rates. | unsupported_and_must_not_be_stated | none | none | none | no | Collision, near-miss, and success-rate metrics are not available. |
| M17-C1 | The repository contains a paper-style pipeline evaluation package that consolidates M13-M16 artifacts. | supported_by_our_experiment | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | software artifact validation | medium | no | Structural evaluation package exists; not a manuscript or publication claim. |
| M17-C2 | Velocity response dataset v1 contains five Measurement v0-derived command records. | supported_by_our_experiment | `outputs/research_datasets/velocity_response_dataset_v1.json` | project dataset artifact | medium | no | Dataset is sparse and single-environment. |
| M17-C3 | M15R response model foundation and M16 offline risk mapping can be reproduced from repository scripts. | supported_by_our_experiment | `scripts/run_velocity_response_model_v1.py`; `scripts/run_navigation_risk_mapping_v1.py` | software artifact validation | medium | no | Reproducible artifact claim only. |
| M17-NC1 | The current pipeline is ready for full publication submission. | unsupported_and_must_not_be_stated | none | none | none | no | Literature review, calibrated uncertainty, and real navigation evaluation are missing. |
| M17-NC2 | The current pipeline demonstrates compensation readiness. | unsupported_and_must_not_be_stated | none | none | none | no | Compensation remains disabled and unimplemented. |
| M17-NC3 | The current pipeline demonstrates safe command adapter readiness. | unsupported_and_must_not_be_stated | none | none | none | no | Safe command adapter remains disabled and unimplemented. |
| P1-C1 | Prior work establishes sim-to-real mismatch, actuator/latency modeling, online adaptation, and deployment calibration as relevant contexts for legged locomotion. | supported_by_prior_work | `paper/related_work/literature_matrix.md` | verified literature metadata | medium | no | Context claim only; does not imply novelty or performance superiority. |
| P1-C2 | Prior work establishes navigation/locomotion coupling and risk-aware traversability as relevant contexts for navigation-aware response interpretation. | supported_by_prior_work | `paper/related_work/literature_matrix.md` | verified literature metadata | medium | no | Context claim only; not evidence that our M16 map improves navigation safety. |
| P1-G1 | Closed-source deployment-layer command-to-motion calibration may be an underexplored gap. | plausible_but_unverified | `paper/claims/literature_gap_candidates.md` | candidate gap | low | no | Candidate only; requires P2 literature expansion and experiments. |
| P1-G2 | Low-level response uncertainty labels may help bridge response modeling and planner advisory layers. | plausible_but_unverified | `paper/claims/literature_gap_candidates.md` | candidate gap | low | no | Candidate only; current labels are not calibrated probabilities. |
| P1-NC1 | P1 establishes final novelty. | unsupported_and_must_not_be_stated | none | none | none | no | P1 is seed search only. |
| P1-NC2 | P1 proves our method outperforms prior work. | unsupported_and_must_not_be_stated | none | none | none | no | No comparative experiment exists. |
| P1-NC3 | P1 proves real navigation safety improvement. | unsupported_and_must_not_be_stated | none | none | none | no | No navigation outcome experiment exists. |
| P2-S1 | P2 analyzes six prior-work clusters against M13-M17 project artifacts. | supported_structural_claim | `paper/positioning/gap_analysis_v1.md` | positioning artifact | medium | no | Structural positioning claim only. |
| P2-C1 | Artifact-governed black-box command-to-motion response pipeline is a candidate contribution. | candidate_gap | `paper/positioning/contribution_candidates_v1.md` | candidate contribution | low | no | Requires more literature and more experiments. |
| P2-C2 | Measurement-to-dataset-to-model workflow for closed-source K1 velocity response is a candidate contribution. | candidate_gap | `paper/positioning/contribution_candidates_v1.md` | candidate contribution | low | no | Current evidence is sparse and single-session. |
| P2-C3 | Uncertainty/reliability-labeled response modeling is a candidate contribution under sparse evidence. | requires_more_experiment | `paper/positioning/contribution_candidates_v1.md` | candidate contribution | low | no | Labels are not calibrated probabilities. |
| P2-C4 | Navigation-aware risk interpretation of low-level response mismatch is a candidate contribution. | requires_more_experiment | `paper/positioning/contribution_candidates_v1.md` | candidate contribution | low | no | No navigation outcome metrics exist. |
| P2-C5 | Claim-governed evaluation separating structural and performance evidence is a candidate contribution. | requires_more_literature | `paper/positioning/contribution_candidates_v1.md`; `paper/claims/claim_upgrade_plan.md` | candidate contribution | low | no | Needs artifact-governance literature comparison. |
| P2-NC1 | P2 establishes final novelty. | non_claim | none | none | none | no | P2 keeps all contributions tentative. |
| P2-NC2 | P2 establishes performance superiority. | non_claim | none | none | none | no | No comparative performance experiment exists. |
| P2-NC3 | P2 establishes publication readiness. | non_claim | none | none | none | no | P2 is positioning only. |
| M18-S1 | M18 creates a method skeleton, experiments skeleton, figure specs, artifact tables, manuscript scaffold, and claim audit. | supported_structural_claim | `outputs/research_foundation/m18_method_skeleton_summary.json` | scaffold artifact validation | medium | no | Structural scaffold claim only; not a full paper draft. |
| M18-C1 | The method skeleton can organize current artifacts into a five-stage paper method structure. | supported_structural_claim | `paper/manuscript/sections/03_method_skeleton.md` | manuscript scaffold | medium | no | Bullet-point skeleton only. |
| M18-C2 | Current evaluation evidence remains structural and does not support navigation outcome claims. | supported_structural_claim | `paper/manuscript/sections/04_experiments_skeleton.md`; `paper/claims/m18_claim_audit.md` | claim audit | high | no | Keeps performance/safety claims prohibited. |
| M18-NC1 | M18 writes a full paper draft. | non_claim | none | none | none | no | M18 creates scaffold artifacts only. |
| M18-NC2 | M18 establishes final novelty or performance superiority. | non_claim | none | none | none | no | Candidate contributions remain tentative. |

Claim type options:

- supported_by_our_experiment
- supported_by_prior_work
- plausible_but_unverified
- planned_experiment
- unsupported_and_must_not_be_stated
- supported_structural_claim
- literature_context_claim
- candidate_gap
- requires_more_literature
- requires_more_experiment
- non_claim
