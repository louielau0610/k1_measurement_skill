# Evidence Table

| evidence_id | source | evidence_kind | verified | summary | supports_claims |
| --- | --- | --- | --- | --- | --- |
| E-M13-SCHEMA | `configs/velocity_response_dataset_schema_v1.json` | project_experiment | yes | Research dataset schema v1 exists. | M17-C1 |
| E-M14-DATASET | `outputs/research_datasets/velocity_response_dataset_v1.json` | project_experiment | yes | Dataset v1 contains five Measurement v0-derived records. | M17-C2 |
| E-M15R-MODEL | `outputs/research_models/response_model_predictions_v1.json` | project_experiment | yes | Response model predictions exist for five command velocities. | M17-C3 |
| E-M16-RISK | `outputs/research_risk/navigation_risk_map_v1.json` | project_experiment | yes | Offline advisory risk assessments exist for five command velocities. | M16-C1 |
| E-M17-EVAL | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | project_experiment | yes | Pipeline evaluation report consolidates M13-M16 artifacts. | M17-C1 |

Evidence kind examples:

- project_experiment
- peer_reviewed_paper
- arxiv_preprint
- official_documentation
- official_dataset
