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
| E-P2-GAP | `paper/positioning/gap_analysis_v1.md` | positioning_artifact | yes | P2 analyzes six literature clusters and maps them to M13-M17 artifacts. | P2-S1 |
| E-P2-TABLE | `paper/positioning/related_work_positioning_table.md` | positioning_artifact | yes | Related-work clusters are mapped to possible gaps and next required evidence. | P2-C1; P2-C2; P2-C3; P2-C4; P2-C5 |
| E-P2-CANDIDATES | `paper/positioning/contribution_candidates_v1.md` | hypothesis | yes | Five contribution candidates are defined with missing evidence and overclaiming risk. | P2-C1; P2-C2; P2-C3; P2-C4; P2-C5 |
| E-P2-UPGRADE | `paper/claims/claim_upgrade_plan.md` | claim_governance | yes | Upgrade conditions and prohibited wording are documented. | P2-NC1; P2-NC2; P2-NC3 |
| E-P2-FRAMING | `paper/positioning/paper_framing_options_v1.md` | positioning_artifact | yes | Five paper framing options are documented as non-final options. | P2-C1; P2-C4; P2-C5 |
| E-M18-METHOD | `paper/manuscript/sections/03_method_skeleton.md` | manuscript_scaffold | yes | Five-stage method skeleton links M13-M17 artifacts without writing final prose. | M18-S1; M18-C1 |
| E-M18-EXPERIMENTS | `paper/manuscript/sections/04_experiments_skeleton.md` | manuscript_scaffold | yes | Experiment skeleton separates structural validation from unavailable navigation outcomes. | M18-S1; M18-C2 |
| E-M18-FIGURES | `paper/figures/method_pipeline_figure_spec.md`; `paper/figures/evidence_chain_figure_spec.md` | figure_specification | yes | Figure specs describe pipeline and claim governance without generating unsupported result figures. | M18-S1 |
| E-M18-TABLES | `paper/tables/method_artifact_evidence_table.md`; `paper/tables/current_metrics_and_missing_evidence_table.md` | paper_table_scaffold | yes | Tables separate current artifacts and missing metrics. | M18-S1; M18-C2 |
| E-M18-AUDIT | `paper/claims/m18_claim_audit.md` | claim_governance | yes | Strict claim audit documents allowed wording and prohibited wording. | M18-C2; M18-NC1; M18-NC2 |

Evidence kind examples:

- project_experiment
- peer_reviewed_paper
- arxiv_preprint
- official_documentation
- official_dataset

| E-P3-DRAFT | `paper/manuscript/sections/02_related_work_draft_v1.md` | manuscript_draft | yes | Citation-safe Related Work draft covering 7 prior-work clusters with 8 seed citations. | P3-RW1; P3-RW2; P3-RW4 |
| E-P3-CLAIM-MAP | `paper/related_work/related_work_claim_map.md` | claim_governance | yes | Maps 18 draft statements to citations, evidence status, and wording boundaries. | P3-RW2 |
| E-P3-AUDIT | `paper/claims/p3_related_work_claim_audit.md` | claim_governance | yes | P3-specific claim audit with safety checks and prohibited wording table. | P3-RW1; P3-NC1; P3-NC2; P3-NC3 |
| E-P3-SUMMARY | `outputs/research_foundation/p3_related_work_summary.json` | metadata | yes | Machine-readable P3 summary with conservative flags. | P3-RW1 |

| E-P4-INTRO | `paper/manuscript/sections/01_introduction_draft_v1.md` | manuscript_draft | yes | Citation-safe Introduction draft covering deployment motivation, problem, gap, approach, contributions, scope, and organization. | P4-I1; P4-I4; P4-I5 |
| E-P4-PROBLEM | `paper/manuscript/sections/01_problem_statement_v1.md` | manuscript_draft | yes | Formal problem statement with notation, system boundary, input/output, scope, and evidence needs. | P4-I2 |
| E-P4-TITLES | `paper/manuscript/sections/00_title_and_contribution_options_v1.md` | manuscript_options | yes | 7 candidate titles and 3 contribution structures, all marked tentative. | P4-I3 |
| E-P4-CLAIM-MAP | `paper/claims/p4_introduction_claim_map.md` | claim_governance | yes | Maps 17 Introduction draft statements to citations, artifacts, and evidence status. | P4-I1; P4-I5 |
| E-P4-AUDIT | `paper/claims/p4_introduction_claim_audit.md` | claim_governance | yes | P4-specific claim audit with introduction, problem statement, and abstract checks. | P4-I1; P4-I6; P4-NC1; P4-NC2; P4-NC3 |
| E-P4-SUMMARY | `outputs/research_foundation/p4_introduction_summary.json` | metadata | yes | Machine-readable P4 summary with conservative flags. | P4-I1 |

| E-P5-METHOD | `paper/manuscript/sections/03_method_draft_v1.md` | manuscript_draft | yes | Academic Method draft covering 10 subsections with formal notation, 3 pseudo-algorithms, and scope/limitations. | P5-M1; P5-M3 |
| E-P5-CLAIM-MAP | `paper/claims/p5_method_claim_map.md` | claim_governance | yes | Maps 15 Method draft statements to project artifacts and evidence status. | P5-M1 |
| E-P5-AUDIT | `paper/claims/p5_method_claim_audit.md` | claim_governance | yes | P5-specific method claim audit with algorithm consistency checks and artifact traceability audit. | P5-M1; P5-NC1; P5-NC2; P5-NC3 |
| E-P5-IO-TABLE | `paper/tables/method_stage_io_contract_table.md` | method_table | yes | Five-stage input/output contract table with producer scripts and validation artifacts. | P5-M2 |
| E-P5-ALGO-TABLE | `paper/tables/method_algorithm_summary_table.md` | method_table | yes | Algorithm summary table with conservative rules and avoided unsupported operations. | P5-M2 |
| E-P5-SUMMARY | `outputs/research_foundation/p5_method_draft_summary.json` | metadata | yes | Machine-readable P5 summary with conservative flags. | P5-M1 |

| E-P6-DRAFT | `paper/manuscript/sections/04_experiments_draft_v1.md` | manuscript_draft | yes | Academic Experiments/Evaluation draft with 5 EQs, structural validation, and missing evidence. | P6-E1; P6-E5 |
| E-P6-CLAIM-MAP | `paper/claims/p6_experiments_claim_map.md` | claim_governance | yes | Maps 16 experiment statements to artifacts and evidence status. | P6-E1 |
| E-P6-AUDIT | `paper/claims/p6_experiments_claim_audit.md` | claim_governance | yes | P6-specific claim audit with metric availability and baseline comparison audits. | P6-E1; P6-NC1; P6-NC2; P6-NC3 |
| E-P6-METRICS-TABLE | `paper/tables/experiment_metrics_status_table.md` | experiment_table | yes | 26-row metrics status table with available/unavailable indicators. | P6-E5 |
| E-P6-EQ-MAP | `paper/tables/evaluation_question_artifact_map.md` | experiment_table | yes | 5-row EQ-to-artifact mapping with current results and interpretation limits. | P6-E1 |
| E-P6-SUMMARY | `outputs/research_foundation/p6_experiments_draft_summary.json` | metadata | yes | Machine-readable P6 summary with conservative flags. | P6-E1 |

| E-P7-DRAFT | `paper/manuscript/sections/05_discussion_limitations_draft_v1.md` | manuscript_draft | yes | Academic Discussion/Limitations draft with 14 subsections. | P7-D1 |
| E-P7-CLAIM-MAP | `paper/claims/p7_discussion_claim_map.md` | claim_governance | yes | Maps 17 discussion statements to artifacts and evidence status. | P7-D1 |
| E-P7-AUDIT | `paper/claims/p7_discussion_claim_audit.md` | claim_governance | yes | P7-specific claim audit with limitation completeness and future-work audits. | P7-D1; P7-NC1; P7-NC2; P7-NC3 |
| E-P7-UPGRADE | `paper/tables/claim_upgrade_requirements_table.md` | method_table | yes | 14-row claim-upgrade requirements table. | P7-D3 |
| E-P7-SUMMARY | `outputs/research_foundation/p7_discussion_limitations_summary.json` | metadata | yes | Machine-readable P7 summary. | P7-D1 |
