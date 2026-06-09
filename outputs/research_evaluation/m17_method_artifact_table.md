# M17 Method Artifact Table

| Chapter / Level | Milestone | Artifact | Path | Producer script | Reproducible? | Purpose | Evidence type | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chapter 2 / Dataset | M13 | Velocity response dataset schema v1 | `configs/velocity_response_dataset_schema_v1.json` | `manual/repository artifact` | False | Velocity response dataset schema v1 | schema |  |
| Chapter 2 / Dataset | M14 | Velocity response dataset v1 | `outputs/research_datasets/velocity_response_dataset_v1.json` | `scripts/build_velocity_response_dataset_v1.py` | True | Velocity response dataset v1 | dataset | single robot; single environment; sparse command samples |
| Chapter 2 / Dataset | M14 | Dataset validation report | `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` | `scripts/build_velocity_response_dataset_v1.py` | True | Dataset validation report | validation_report |  |
| Chapter 2 / Model | M15R | Response model predictions | `outputs/research_models/response_model_predictions_v1.json` | `scripts/run_velocity_response_model_v1.py` | True | Response model predictions | prediction_output | uncertainty labels are not calibrated probabilities |
| Chapter 2 / Model | M15R | Response model structural evaluation | `outputs/research_models/response_model_evaluation_v1.json` | `scripts/run_velocity_response_model_v1.py` | True | Response model structural evaluation | evaluation_output | exact-source reconstruction is not performance evidence |
| Chapter 3 / Risk | M16 | Offline navigation risk map | `outputs/research_risk/navigation_risk_map_v1.json` | `scripts/run_navigation_risk_mapping_v1.py` | True | Offline navigation risk map | risk_map | advisory only; no navigation outcomes |
| Chapter 3 / Risk | M16 | Risk-map structural evaluation | `outputs/research_risk/navigation_risk_evaluation_v1.json` | `scripts/run_navigation_risk_mapping_v1.py` | True | Risk-map structural evaluation | risk_evaluation | no collision, near-miss, or success-rate metrics |
| Research Governance | P0-M17 | Conservative claim registry | `paper/claims/claim_registry.md` | `manual/repository artifact` | False | Conservative claim registry | claim_registry |  |
| Research Governance | P0-M17 | Prohibited overclaim list | `paper/claims/non_claims.md` | `manual/repository artifact` | False | Prohibited overclaim list | non_claims |  |
