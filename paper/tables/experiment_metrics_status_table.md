# Experiment Metrics Status Table

| metric_category | metric | available_now | current_source_artifact | current_use | missing_requirement | claim_allowed_now |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset structure | record count | yes (5) | `velocity_response_dataset_v1.json` | structural summary | — | structural claim only |
| Dataset structure | numeric record count | yes (4) | `velocity_response_dataset_v1.json` | structural summary | — | structural claim only |
| Dataset structure | qualitative-only record count | yes (1) | `velocity_response_dataset_v1.json` | limitation context | — | structural claim only |
| Dataset structure | schema validation pass | yes | `velocity_response_dataset_v1_validation_report.json` | structural validation | — | structural claim only |
| Dataset structure | command velocity range | yes (0.10–0.50 m/s) | `velocity_response_dataset_v1.json` | context | — | structural claim only |
| Model output | prediction count | yes (5) | `response_model_predictions_v1.json` | output count | — | structural claim only |
| Model output | prediction types generated | yes (numeric, qualitative) | `response_model_predictions_v1.json` | coverage report | — | structural claim only |
| Model output | uncertainty labels assigned | yes (all predictions) | `response_model_predictions_v1.json` | labeling report | — | structural claim only |
| Model accuracy | exact-source reconstruction MAE | yes (0.0) | `response_model_evaluation_v1.json` | sanity check only | held-out data for predictive accuracy | no performance claim |
| Model accuracy | held-out prediction error | **no** | — | — | repeated and held-out trials | no |
| Model calibration | calibrated uncertainty error | **no** | — | — | repeated evidence and calibration protocol | no |
| Risk output | assessment count | yes (5) | `navigation_risk_map_v1.json` | output count | — | structural claim only |
| Risk output | warning count | yes (5) | `navigation_risk_evaluation_v1.json` | advisory report | — | structural claim only |
| Risk output | risk level distribution | yes (1 critical, 2 high, 2 medium) | `navigation_risk_evaluation_v1.json` | advisory report | — | structural claim only |
| Risk output | warning category distribution | yes (4 categories) | `navigation_risk_evaluation_v1.json` | advisory report | — | structural claim only |
| Navigation performance | collision rate | **no** | — | — | navigation outcome trials | no |
| Navigation performance | near-miss rate | **no** | — | — | navigation outcome trials + annotation protocol | no |
| Navigation performance | navigation success rate | **no** | — | — | navigation task protocol | no |
| Navigation performance | path deviation | **no** | — | — | planned path and executed trajectory evidence | no |
| Safety | before/after advisory comparison | **no** | — | — | controlled baseline comparison | no |
| Generalization | multi-environment replication | **no** | — | — | multi-surface / multi-session trials | no |
| Generalization | cross-robot replication | **no** | — | — | additional K1 units or legged robots | no |
| Latency / drift | response delay | **no** | — | — | timestamp-aligned logging | no |
| Latency / drift | yaw drift | **no** | — | — | angular measurement evidence | no |
| Latency / drift | lateral drift | **no** | — | — | lateral measurement evidence | no |
| Latency / drift | stop distance | **no** | — | — | stop-trial protocol | no |
