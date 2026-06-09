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

Claim type options:

- supported_by_our_experiment
- supported_by_prior_work
- plausible_but_unverified
- planned_experiment
- unsupported_and_must_not_be_stated
