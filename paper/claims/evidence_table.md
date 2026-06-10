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

| E-P8-ASSEMBLY | `paper/manuscript/manuscript_v0_assembly.md` | manuscript_assembly | yes | Assembled manuscript v0 with all section drafts, placeholder abstract/conclusion, and claim boundaries. | P8-A1; P8-A4 |
| E-P8-CONSISTENCY | `paper/manuscript/manuscript_v0_consistency_audit.md` | audit | yes | Cross-section consistency audit with terminology, contribution, claim, citation, figure/table, and flow checks. | P8-A2 |
| E-P8-CLAIM-AUDIT | `paper/claims/p8_manuscript_claim_audit.md` | claim_governance | yes | Manuscript-level claim audit confirming no prohibited claims and abstract/conclusion boundaries. | P8-A3; P8-NC1; P8-NC2 |
| E-P8-SECTION-TABLE | `paper/tables/manuscript_section_status_table.md` | manuscript_table | yes | 13-row section status table with current status, evidence sources, and next actions. | P8-A1 |
| E-P8-TERM-TABLE | `paper/tables/terminology_consistency_table.md` | manuscript_table | yes | 10-row terminology consistency table with preferred terms, variants, and definitions. | P8-A1 |
| E-P8-SUMMARY | `outputs/research_foundation/p8_manuscript_assembly_summary.json` | metadata | yes | Machine-readable P8 summary. | P8-A1 |

| E-P9-CONCLUSION | `paper/manuscript/sections/06_conclusion_draft_v1.md` | manuscript_draft | yes | Academic Conclusion draft: 619 words, 6 paragraphs. | P9-C1; P9-C2 |
| E-P9-CLAIM-MAP | `paper/claims/p9_conclusion_claim_map.md` | claim_governance | yes | Maps 9 conclusion statements to artifacts and evidence status. | P9-C1 |
| E-P9-AUDIT | `paper/claims/p9_conclusion_claim_audit.md` | claim_governance | yes | P9 conclusion claim audit confirming confident but bounded tone. | P9-C1; P9-NC1; P9-NC2; P9-NC3 |
| E-P9-SUMMARY | `outputs/research_foundation/p9_conclusion_summary.json` | metadata | yes | Machine-readable P9 summary. | P9-C1 |

| E-P10-ABSTRACT | `paper/manuscript/sections/00_abstract_draft_v1.md` | manuscript_draft | yes | Academic Abstract draft: 193 words primary, plus short and extended variants. | P10-A1; P10-A2 |
| E-P10-CLAIM-MAP | `paper/claims/p10_abstract_claim_map.md` | claim_governance | yes | Maps 8 abstract clauses to artifacts and evidence status. | P10-A1 |
| E-P10-AUDIT | `paper/claims/p10_abstract_claim_audit.md` | claim_governance | yes | P10 abstract claim audit confirming safe wording and numeric accuracy. | P10-A1; P10-NC1; P10-NC2; P10-NC3 |
| E-P10-SUMMARY | `outputs/research_foundation/p10_abstract_summary.json` | metadata | yes | Machine-readable P10 summary. | P10-A1 |

| E-P11-AUDIT | `paper/manuscript/full_manuscript_claim_audit_v1.md` | audit | yes | Full-manuscript claim audit with section-by-section analysis, numeric traceability, citation audit, overclaim scan. | P11-A1 |
| E-P11-REVISION | `paper/manuscript/manuscript_revision_plan_v1.md` | revision_plan | yes | Prioritized revision plan: 0 P0, 3 P1, 3 P2, 2 P3; separates Codex-editable from experiment-required fixes. | P11-A2 |
| E-P11-MATRIX | `paper/claims/p11_full_manuscript_claim_matrix.md` | claim_governance | yes | 19-row full manuscript claim matrix with evidence status and decisions. | P11-A1 |
| E-P11-NUMERIC | `paper/tables/numeric_traceability_table.md` | audit_table | yes | 12-row numeric traceability table with source artifacts and interpretation boundaries. | P11-A3 |
| E-P11-CITATION | `paper/tables/citation_audit_table.md` | audit_table | yes | 16-row citation audit table covering all matrix entries. | P11-A4 |
| E-P11-PRIORITY | `paper/tables/revision_priority_table.md` | audit_table | yes | 12-row revision priority table with blocking assessment and next-step owner. | P11-A2 |
| E-P11-SUMMARY | `outputs/research_foundation/p11_full_manuscript_audit_summary.json` | metadata | yes | Machine-readable P11 summary. | P11-A1 |

| E-P12-ASSEMBLY | `paper/manuscript/manuscript_v1_assembly.md` | manuscript_assembly | yes | Revised manuscript v1 assembly with Abstract through Conclusion, evidence gaps, and revision notes. | P12-R2 |
| E-P12-CHANGELOG | `paper/manuscript/manuscript_v1_revision_changelog.md` | revision_artifact | yes | P12 revision changelog tracking 5 resolved and 3 deferred P11 issues. | P12-R1 |
| E-P12-CONSISTENCY | `paper/manuscript/manuscript_v1_consistency_check.md` | audit | yes | Post-revision consistency check confirming all boundaries preserved. | P12-R3 |
| E-P12-AUDIT | `paper/claims/p12_revision_claim_audit.md` | claim_governance | yes | P12 revision claim audit verifying no new overclaims. | P12-R1; P12-NC1; P12-NC2 |
| E-P12-RESOLVED | `paper/tables/p12_resolved_and_deferred_issues_table.md` | revision_table | yes | 13-row resolved/deferred issues table. | P12-R1 |
| E-P12-SUMMARY | `outputs/research_foundation/p12_manuscript_revision_summary.json` | metadata | yes | Machine-readable P12 summary. | P12-R1 |

| E-P13-CLEANUP | `paper/related_work/p13_reference_cleanup_report.md` | citation_report | yes | Reference cleanup report: 8 BibTeX added, 3 new manuscript citations. | P13-R1; P13-R2 |
| E-P13-BIB-AUDIT | `paper/related_work/p13_bibtex_verification_audit.md` | audit_table | yes | 8-row BibTeX verification audit with field-level verification status. | P13-R1 |
| E-P13-LIT-EXP | `paper/related_work/p13_literature_expansion_report.md` | citation_report | yes | Literature expansion report documenting RW §4/§5 improvements. | P13-R2 |
| E-P13-CLAIM-AUDIT | `paper/claims/p13_citation_claim_audit.md` | claim_governance | yes | P13 citation claim audit confirming no new overclaims. | P13-NC1; P13-NC2 |
| E-P13-REF-TABLE | `paper/tables/p13_reference_status_table.md` | reference_table | yes | 16-row reference status table for all literature entries. | P13-R1 |
| E-P13-SUMMARY | `outputs/research_foundation/p13_reference_cleanup_summary.json` | metadata | yes | Machine-readable P13 summary. | P13-R1 |

| E-M19-FIGURES | `paper/figures/method_pipeline_figure.mmd`; `paper/figures/evidence_chain_figure.mmd` | figure_asset | yes | Mermaid figure sources generated by `scripts/generate_m19_figures.py`. | M19-F1; M19-F2 |
| E-M19-REPORT | `paper/figures/m19_figure_rendering_report.md` | report | yes | Figure rendering report documenting generation process and post-generation steps. | M19-F1; M19-F2 |
| E-M19-SUMMARY | `outputs/research_foundation/m19_figure_table_assets_summary.json` | metadata | yes | Machine-readable M19 summary. | M19-F1 |

| E-M19.1-GAP-FIG | `paper/figures/current_evidence_gap_v1.md` | figure_spec | yes | Evidence-gap figure spec (Figure 3) with Mermaid diagram. | M19.1-I1 |
| E-M19.1-CAPTIONS | `paper/figures/figure_caption_pack_v1.md`; `paper/tables/table_caption_pack_v1.md` | caption_pack | yes | 7 caption entries (3 figures + 4 tables). | M19.1-I1 |
| E-M19.1-TABLES | `paper/tables/main_paper_table_pack_v1.md`; `paper/tables/appendix_table_pack_v1.md` | table_pack | yes | 3 main + 11 appendix table candidates. | M19.1-I1 |
| E-M19.1-PLAN | `paper/manuscript/figure_table_integration_plan_v1.md` | integration_plan | yes | Integration plan with insertion points and rendering instructions. | M19.1-I1 |
| E-M19.1-AUDIT | `paper/claims/m19_1_figure_table_claim_audit.md` | claim_governance | yes | Figure/table claim audit confirming 0 caption violations. | M19.1-I1 |
| E-M19.1-SUMMARY | `outputs/research_foundation/m19_1_figure_table_completion_summary.json` | metadata | yes | Machine-readable M19.1 summary. | M19.1-I1 |

| E-P14-V2 | `paper/manuscript/manuscript_v2_assembly.md` | manuscript_assembly | yes | Polished manuscript v2 with integrated figure/table references. | P14-V1 |
| E-P14-REPORT | `paper/manuscript/manuscript_v2_polish_report.md` | revision_report | yes | Polish report: 7 integration changes, claim-boundary preservation confirmed. | P14-V1 |
| E-P14-CONSISTENCY | `paper/manuscript/manuscript_v2_consistency_check.md` | audit | yes | V2 consistency check: all 5 assets cross-referenced consistently. | P14-V1 |
| E-P14-AUDIT | `paper/claims/p14_manuscript_v2_claim_audit.md` | claim_governance | yes | V2 claim audit: 0 claim changes, 0 overclaims. | P14-V1; P14-NC1 |
| E-P14-MAIN-ASSETS | `paper/tables/p14_main_paper_asset_plan.md` | asset_plan | yes | 5 main-paper asset plan with source/caption/claim-boundary mappings. | P14-V2 |
| E-P14-APP-ASSETS | `paper/tables/p14_appendix_asset_plan.md` | asset_plan | yes | 13 appendix/internal asset plan. | P14-V2 |
| E-P14-SUMMARY | `outputs/research_foundation/p14_manuscript_v2_polish_summary.json` | metadata | yes | Machine-readable P14 summary. | P14-V1 |

| E-M20-PROTOCOL | `paper/experiments/m20_future_experiment_protocol_v1.md` | experiment_protocol | yes | 4-tier future experiment protocol with claim-upgrade criteria. | M20-P1 |
| E-M20-METRICS | `paper/experiments/m20_metric_definitions_v1.md` | metric_definitions | yes | 35 metrics defined across velocity response, model evaluation, navigation outcome, and coverage. | M20-P1 |
| E-M20-DESIGN | `paper/experiments/m20_trial_design_matrix_v1.md` | trial_design | yes | Command grid, trial counts, held-out split, surface/session plan. | M20-P1 |
| E-M20-NAV | `paper/experiments/m20_navigation_outcome_protocol_v1.md` | navigation_protocol | yes | Navigation outcome protocol with collision/near-miss definitions and advisory condition rules. | M20-P1 |
| E-M20-SCHEMA | `configs/future_experiment_protocol_schema_v1.json` + examples + validator + tests | schema_and_tools | yes | JSON schema, 2 examples, validator script, 7 tests. | M20-P1 |
| E-M20-AUDIT | `paper/claims/m20_experiment_protocol_claim_audit.md` | claim_governance | yes | M20 claim audit confirming protocol-only boundaries. | M20-NC1; M20-NC2 |
| E-M20-MATRIX | `paper/tables/m20_claim_upgrade_evidence_matrix.md` | claim_table | yes | 11-row claim-upgrade evidence matrix. | M20-P1 |
| E-M20-SUMMARY | `outputs/research_foundation/m20_future_experiment_protocol_summary.json` | metadata | yes | Machine-readable M20 summary. | M20-P1 |

| E-M21.1-NAV-TMPL | `examples/future_experiments/m21_future_navigation_task_template.json` | json_template | yes | M21.1 navigation task JSON placeholder template. | M21-P1 |
| E-M21.1-SUMMARY | `outputs/research_foundation/m21_1_data_collection_pack_completion_summary.json` | metadata | yes | M21.1 completion patch summary. | M21-P1 |

## P16 LaTeX Scaffold Evidence (format-scaffold only)

| E-P16-SCAFFOLD | `paper/latex/main.tex`; `paper/latex/macros.tex`; `paper/latex/references.bib` | latex_scaffold | yes | Non-final LaTeX scaffold (main, macros, BibTeX). No PDF built. | P16-L1 |
| E-P16-SECTIONS | `paper/latex/sections/00-07_*.tex` (8 files) | latex_scaffold | yes | Section scaffolds (abstract fully converted, 01-06 placeholders, 07 appendix plan). | P16-L1 |
| E-P16-FIG-README | `paper/latex/figures/README.md` | scaffold_doc | yes | Figure status: 3 figures not rendered. | P16-L1 |
| E-P16-TAB-README | `paper/latex/tables/README.md` | scaffold_doc | yes | Table status: 3 main tables not converted. | P16-L1 |
| E-P16-BUILD | `paper/latex/build_notes_v1.md` | scaffold_doc | yes | Build notes: no PDF built; blockers documented. | P16-L1 |
| E-P16-CLAIM-AUDIT | `paper/latex/p16_latex_scaffold_claim_audit.md` | claim_governance | yes | P16 scaffold claim audit. | P16-L1 |
| E-P16-ASSET-STATUS | `paper/tables/p16_latex_scaffold_asset_status.md` | scaffold_table | yes | 16-row asset status table. | P16-L1 |
| E-P16-SUMMARY | `outputs/research_foundation/p16_latex_scaffold_summary.json` | metadata | yes | P16 summary. | P16-L1 |

**Evidence boundary**: These assets support the claim that a non-final LaTeX scaffold exists. They do not support publication readiness, scientific performance claims, navigation safety improvement, or final PDF/submission package existence.

## P17 Figure/Table LaTeX Assets (format-asset only)

| E-P17-TABLES | `paper/latex/tables/table1-3_*.tex` (3 files) | latex_asset | yes | Non-final LaTeX tables from existing table packs. | P17-L1 |
| E-P17-FIG-COPY | `paper/latex/figures/*.mmd` (2 copies) | latex_asset | yes | Mermaid sources copied for future rendering. | P17-L1 |
| E-P17-REPORT | `paper/latex/p17_figure_table_asset_report.md` | report | yes | P17 asset production report. | P17-L1 |
| E-P17-AUDIT | `paper/latex/p17_figure_table_claim_audit.md` | claim_governance | yes | P17 claim audit. | P17-L1 |
| E-P17-STATUS | `paper/tables/p17_latex_asset_status.md` | asset_table | yes | P17 asset status table. | P17-L1 |
| E-P17-SUMMARY | `outputs/research_foundation/p17_figure_table_latex_assets_summary.json` | metadata | yes | P17 summary. | P17-L1 |

**Evidence boundary**: These assets are non-final format production only. No scientific evidence added.
