# Current Metrics and Missing Evidence Table

| Category | Metric / evidence | Available now? | Current source artifact | Can be used for paper now? | Missing requirement | Claim allowed? |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset metrics | dataset record count | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as structural dataset summary | none | structural claim only |
| Dataset metrics | numeric records count | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as dataset summary | none | structural claim only |
| Dataset metrics | qualitative-only count | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as limitation/context | none | structural claim only |
| Dataset metrics | validation pass/fail | yes | `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json` | yes | none | structural claim only |
| Response-model metrics | response predictions count | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as output count | none | structural claim only |
| Response-model metrics | exact-source reconstruction sanity check | yes | `outputs/research_models/response_model_evaluation_v1.json` | yes, with caveat | held-out data for performance | no performance claim |
| Response-model metrics | held-out prediction error | no | none | no | repeated and held-out trials | no |
| Uncertainty calibration metrics | calibrated uncertainty error | no | none | no | repeated evidence and calibration protocol | no |
| Risk-map metrics | risk level counts | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as structural output summary | none | structural/advisory claim only |
| Risk-map metrics | warning category counts | yes | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | yes, as structural output summary | none | structural/advisory claim only |
| Navigation outcome metrics | collision rate | no | none | no | navigation outcome trials | no |
| Navigation outcome metrics | near-miss rate | no | none | no | navigation outcome trials and annotation protocol | no |
| Navigation outcome metrics | success rate | no | none | no | navigation task protocol | no |
| Navigation outcome metrics | path deviation | no | none | no | planned path and executed trajectory evidence | no |
| Safety metrics | before/after advisory comparison | no | none | no | controlled baseline comparison | no |
| Generalization metrics | multi-environment generalization | no | none | no | multi-surface / multi-session trials | no |
| Generalization metrics | cross-robot generalization | no | none | no | additional K1 units or legged robots | no |

