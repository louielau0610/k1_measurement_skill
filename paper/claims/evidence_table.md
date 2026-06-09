# Evidence Table

| evidence_id | source | evidence_kind | verified | summary | supports_claims |
| --- | --- | --- | --- | --- | --- |
| E-M13-SCHEMA | `configs/velocity_response_dataset_schema_v1.json` | project_experiment | yes | Research dataset schema v1 exists. | M17-C1 |
| E-M14-DATASET | `outputs/research_datasets/velocity_response_dataset_v1.json` | project_experiment | yes | Dataset v1 contains five Measurement v0-derived records. | M17-C2 |
| E-M15R-MODEL | `outputs/research_models/response_model_predictions_v1.json` | project_experiment | yes | Response model predictions exist for five command velocities. | M17-C3 |
| E-M16-RISK | `outputs/research_risk/navigation_risk_map_v1.json` | project_experiment | yes | Offline advisory risk assessments exist for five command velocities. | M16-C1 |
| E-M17-EVAL | `outputs/research_evaluation/m17_pipeline_evaluation_report.json` | project_experiment | yes | Pipeline evaluation report consolidates M13-M16 artifacts. | M17-C1 |
| E-P1-LIT-A-C | `paper/related_work/literature_matrix.md` entries TanRSS2018, HwangboSciRobot2019, KumarRMA2021, RudinCoRL2021, MargolisRSS2022, MargolisCoRL2022 | peer_reviewed_paper_or_preprint | yes/partial | Seed literature supports sim-to-real mismatch, velocity-command curricula, online adaptation, and deployment calibration as relevant contexts. | P1-C1 |
| E-P1-LIT-D-F | `paper/related_work/literature_matrix.md` entries FuCVPRW2022, FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025 | peer_reviewed_paper_or_preprint | yes/partial | Seed literature supports navigation/locomotion coupling, risk-aware traversability, and navigation evaluation metrics as relevant contexts. | P1-C2 |
| E-P1-GAP | `paper/claims/literature_gap_candidates.md` | hypothesis | yes | Candidate gaps are logged as hypotheses only. | P1-G1; P1-G2 |

Evidence kind examples:

- project_experiment
- peer_reviewed_paper
- arxiv_preprint
- official_documentation
- official_dataset
