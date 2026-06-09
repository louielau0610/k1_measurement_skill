# P11 Full Manuscript Claim Matrix

| section | claim_summary | claim_type | evidence_source | evidence_status | allowed_wording | risky_wording | required_upgrade_evidence | current_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Abstract | Closed-source command-to-motion mismatch affects navigation reliability. | supported_by_project_artifact | P4 intro, M7-M8 docs | safe | "mapping... is opaque to the user" | — | — | keep |
| Abstract | Five-stage artifact-governed pipeline presented. | supported_by_project_artifact | M13-M18, P5 method | safe | "presents an offline, artifact-governed pipeline" | — | — | keep |
| Abstract | 5 records, 5 predictions, 5 risk assessments across 3 risk levels. | supported_by_project_artifact | dataset v1, model preds, risk eval | safe | "five dataset records (four numeric, one qualitative-only)" | — | — | keep |
| Introduction | Deployment-layer mismatch is a measurable problem. | supported_by_project_artifact | M13-M14 + P1-P2 lit | safe | "measurable deployment-layer response characteristic" | — | — | keep |
| Introduction | Candidate gap: closed-source deployment-layer calibration underexplored. | candidate_contribution | P1-P2 lit + gap analysis | requires_more_literature | "does not yet establish... candidate contribution" | — | broader system-ID review | keep (bounded) |
| Introduction | 4 tentative contributions presented. | candidate_contribution | M13-M18 + P2-P5 | safe | "All contributions remain tentative... not final novelty" | — | — | keep (tentative) |
| Related Work | Sim-to-real, adaptation, navigation-coupled, risk-aware, black-box calibration reviewed. | supported_by_literature | 8 seed references | safe | "These works primarily target..." | — | — | keep |
| Related Work | Seed literature does not establish equivalent closed-source pipeline. | candidate_contribution | P2 gap analysis | requires_more_literature | "does not yet establish..." | — | broader system-ID review | keep (bounded) |
| Method | Five pipeline stages with formal notation and algorithmic contracts. | supported_structural_claim | M13-M18 + code artifacts | safe | "offline, artifact-governed pipeline" | — | — | keep |
| Method | Uncertainty labels are categorical, not calibrated probabilities. | supported_structural_claim | M15R model + eval | safe | "categorical reliability marker... not calibrated probability" | — | — | keep |
| Method | Risk mapper is advisory; no compensation or control. | supported_structural_claim | M16 code + safety flags | safe | "does not control the robot... does not trigger automatic compensation" | — | — | keep |
| Experiments | Dataset: 5 records, 4 numeric, 1 qualitative-only. | supported_by_project_artifact | dataset v1 + model eval | safe | "5 records, 4 numeric, 1 qualitative-only" | — | — | keep |
| Experiments | Exact-source MAE=0.0 is structural sanity check only. | sanity_check_only | model eval | safe | "structural sanity check, not predictive accuracy" | — | held-out evaluation | keep (bounded) |
| Experiments | No navigation outcomes, collision, or success-rate metrics. | supported_by_project_artifact | M17 eval + risk eval | safe | "collision, near-miss, success-rate... explicitly documented as unavailable" | — | navigation trials | keep |
| Discussion | Pipeline demonstrates artifact-governed structural transformation. | supported_by_project_artifact | M13-M18 + P5-P6 | safe | "demonstrates that an offline, artifact-governed pipeline can transform..." | — | — | keep |
| Discussion | Deployment-layer modeling differs from controller-centric work. | candidate_interpretation | P1-P2 lit + P3 draft | requires_more_literature | "differs from locomotion policy training... from direct compensation" | — | system-ID lit review | keep (bounded) |
| Discussion | All limitations comprehensively documented. | supported_by_project_artifact | P6 §4.7 + P7 §6 | safe | "the pipeline is deliberately constrained in scope" | — | — | keep |
| Conclusion | Work provides evidence-governed foundation for deployment-layer reliability. | candidate_interpretation | all M13-P9 + claim gov | safe | "evidence-governed foundation for studying deployment-layer reliability" | — | — | keep (bounded) |
| Conclusion | Future experiments required before performance/safety claims. | future_work_only | P6 §4.8 + P7 §7 | safe | "Future work will expand... Only after such evidence exists" | — | all listed experiments | keep |
