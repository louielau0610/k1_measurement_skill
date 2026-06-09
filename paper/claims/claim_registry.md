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

| P3-RW1 | P3 creates a citation-safe Related Work draft v1 synthesizing P1/P2 literature. | supported_structural_claim | `paper/manuscript/sections/02_related_work_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final manuscript prose. |
| P3-RW2 | The Related Work draft covers seven prior-work clusters and uses 8 verified/partially verified seed citations. | supported_structural_claim | `paper/related_work/related_work_claim_map.md` | draft audit artifact | medium | no | Structural claim about draft content only. |
| P3-RW3 | The seed literature does not yet establish a directly equivalent artifact-governed closed-source command-response pipeline. | candidate_gap | `paper/positioning/gap_analysis_v1.md`; P3 draft | candidate gap | low | no | Requires more literature before upgrading to novelty. |
| P3-RW4 | The current project is positioned as candidate contributions, not final novelty. | supported_structural_claim | `paper/manuscript/sections/02_related_work_draft_v1.md` §7 | positioning artifact | medium | no | Explicitly conservative framing. |
| P3-NC1 | P3 establishes final novelty. | non_claim | none | none | none | no | P3 draft explicitly states this is not final novelty. |
| P3-NC2 | P3 establishes performance superiority over prior work. | non_claim | none | none | none | no | No comparative experiment exists. |
| P3-NC3 | P3 establishes publication readiness. | non_claim | none | none | none | no | Draft is v1 only. |

| P4-I1 | P4 creates a citation-safe Introduction draft v1 synthesizing P1-P3 literature and M18 skeleton. | supported_structural_claim | `paper/manuscript/sections/01_introduction_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final submission prose. |
| P4-I2 | P4 creates a formal Problem Statement with notation, system boundary, and current scope. | supported_structural_claim | `paper/manuscript/sections/01_problem_statement_v1.md` | manuscript draft artifact | medium | no | Formal documentation of problem scope. |
| P4-I3 | P4 provides tentative title and contribution options documenting 7 candidate titles and 3 contribution structures. | supported_structural_claim | `paper/manuscript/sections/00_title_and_contribution_options_v1.md` | manuscript options artifact | low | no | No final title or contribution structure selected. |
| P4-I4 | The deployment-layer command-to-motion mismatch is a measurable problem relevant to navigation. | allowed_context_claim | FuCVPRW2022, FanRSS2021STEP | P1/P2 literature + M13-M17 artifacts | low | no | Context framing only; not a safety claim. |
| P4-I5 | Current contributions remain tentative and require more literature and experiments. | allowed_structural_claim | — | P4 claim audit, M18 audit, P2 candidates | high | no | Explicitly conservative. |
| P4-I6 | The Introduction draft does not constitute a final abstract or final contribution claim. | non_claim | — | P4 draft headers and disclaimer | high | no | Draft safeguards in place. |
| P4-NC1 | P4 establishes final novelty. | non_claim | none | none | none | no | Draft explicitly states this. |
| P4-NC2 | P4 establishes performance superiority. | non_claim | none | none | none | no | No comparative experiment exists. |
| P4-NC3 | P4 establishes publication readiness. | non_claim | none | none | none | no | Draft is v1 only. |

| P5-M1 | P5 creates an academic Method draft v1 with formal notation, 10 subsections, and 3 pseudo-algorithms. | supported_structural_claim | `paper/manuscript/sections/03_method_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final submission prose. |
| P5-M2 | Method describes five pipeline stages with explicit input/output contracts and artifact paths. | supported_structural_claim | `paper/tables/method_stage_io_contract_table.md`; `paper/tables/method_algorithm_summary_table.md` | method tables | medium | no | Structural documentation of pipeline contracts. |
| P5-M3 | Method explicitly documents that compensation, inverse mapping, navigation control, and safe adapter are not implemented. | supported_structural_claim | `paper/manuscript/sections/03_method_draft_v1.md` §3.1, §3.6, §3.9 | method draft + non-claims | high | no | Conservative scope boundary maintained. |
| P5-NC1 | P5 establishes final novelty. | non_claim | none | none | none | no | Method draft explicitly avoids novelty language. |
| P5-NC2 | P5 establishes performance superiority. | non_claim | none | none | none | no | No comparative experiment evaluated. |
| P5-NC3 | P5 establishes publication readiness. | non_claim | none | none | none | no | Draft is v1 only. |

| P6-E1 | P6 creates an academic Experiments/Evaluation draft v1 with 5 evaluation questions and structural validation. | supported_structural_claim | `paper/manuscript/sections/04_experiments_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final submission prose. |
| P6-E2 | Dataset v1 contains 5 records: 4 numeric, 1 qualitative-only at 0.10 m/s deadzone. | supported_by_project_artifact | `outputs/research_datasets/velocity_response_dataset_v1.json`; `outputs/research_models/response_model_evaluation_v1.json` | project dataset + model eval artifact | high | no | Numbers verified against output artifacts. |
| P6-E3 | Exact-source reconstruction MAE is 0.0 — a structural sanity check, not predictive performance evidence. | sanity_check_only | `outputs/research_models/response_model_evaluation_v1.json` | model eval artifact | high | no | No held-out evaluation exists. |
| P6-E4 | Risk map reports 5 assessments with 5 warnings across 3 risk levels. | structural_validation_only | `outputs/research_risk/navigation_risk_evaluation_v1.json` | risk eval artifact | medium | no | Advisory classification only; no navigation outcomes. |
| P6-E5 | All unavailable metrics (collision, near-miss, success, generalization, calibration) are explicitly documented. | supported_by_project_artifact | `paper/tables/experiment_metrics_status_table.md` | metrics table + M17 eval | high | no | Future experiments required. |
| P6-NC1 | P6 establishes navigation safety improvement. | non_claim | none | none | none | no | No navigation outcome data exists. |
| P6-NC2 | P6 establishes performance superiority over baselines. | non_claim | none | none | none | no | Baselines not evaluated on held-out data. |
| P6-NC3 | P6 establishes calibrated uncertainty. | non_claim | none | none | none | no | Labels are categorical, not calibrated. |

| P7-D1 | P7 creates an academic Discussion and Limitations draft v1 with 5 discussion subsections, 5 limitation subsections, and 4 future-work subsections. | supported_structural_claim | `paper/manuscript/sections/05_discussion_limitations_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final conclusion. |
| P7-D2 | Deployment-layer response modeling differs from policy training, adaptation, and compensation. | candidate_interpretation | TanRSS2018, HwangboSciRobot2019, KumarRMA2021, MargolisRSS2022 | P1-P2 lit + P3-P5 drafts | low | no | Requires more system-ID literature. |
| P7-D3 | Claim-upgrade requirements table documents evidence needed to upgrade each claim type. | supported_structural_claim | `paper/tables/claim_upgrade_requirements_table.md` | method table | medium | no | Structural documentation of upgrade paths. |
| P7-NC1 | P7 establishes final novelty. | non_claim | none | none | none | no | Discussion explicitly avoids novelty language. |
| P7-NC2 | P7 writes a final conclusion. | non_claim | none | none | none | no | §8 states "not a final conclusion." |
| P7-NC3 | P7 establishes navigation safety improvement. | non_claim | none | none | none | no | No navigation outcome data exists. |

| P8-A1 | P8 assembles a manuscript v0 from P3-P7 section drafts with consistent heading numbering. | supported_structural_claim | `paper/manuscript/manuscript_v0_assembly.md` | manuscript assembly artifact | medium | no | Assembly only; not submission ready. |
| P8-A2 | P8 creates a cross-section consistency audit identifying 8 issues (0 blocking, 3 high evidence gaps, 3 medium). | supported_structural_claim | `paper/manuscript/manuscript_v0_consistency_audit.md` | audit artifact | medium | no | Evidence gaps correctly documented. |
| P8-A3 | P8 creates manuscript-level claim audit confirming no prohibited claims in any section. | supported_structural_claim | `paper/claims/p8_manuscript_claim_audit.md` | claim audit artifact | high | no | All sections maintain conservative boundary. |
| P8-A4 | Abstract and Conclusion are intentionally placeholder-only. | supported_structural_claim | manuscript assembly | assembly artifact | high | no | Satisfies P8 non-goals. |
| P8-NC1 | P8 establishes submission readiness. | non_claim | none | none | none | no | Explicitly marked "not submission ready." |
| P8-NC2 | P8 writes a final abstract or conclusion. | non_claim | none | none | none | no | Both are placeholder-only. |

| P9-C1 | P9 creates a confident but bounded Conclusion draft v1 completing the manuscript narrative. | supported_structural_claim | `paper/manuscript/sections/06_conclusion_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final submission. |
| P9-C2 | Conclusion summarizes pipeline, evaluation results, and future work within evidence boundaries. | supported_by_project_artifact | P6 eval + P5 method + P8 assembly | manuscript + project artifacts | high | no | All claims traceable to project artifacts. |
| P9-NC1 | P9 establishes final novelty. | non_claim | none | none | none | no | Conclusion avoids "novel"/"first" language. |
| P9-NC2 | P9 establishes performance superiority or safety improvement. | non_claim | none | none | none | no | No such claims made. |
| P9-NC3 | P9 claims publication readiness. | non_claim | none | none | none | no | Abstract remains unwritten. |

| P10-A1 | P10 creates an academic Abstract draft v1 with primary (193w), short, and extended variants. | supported_structural_claim | `paper/manuscript/sections/00_abstract_draft_v1.md` | manuscript draft artifact | medium | no | Draft only; not final submission abstract. |
| P10-A2 | Abstract accurately compresses the manuscript: problem, method, results, significance, boundary. | supported_by_project_artifact | P8 assembly + P9 conclusion + P6 eval | manuscript + project artifacts | high | no | All numbers artifact-backed. |
| P10-NC1 | P10 establishes final novelty. | non_claim | none | none | none | no | Abstract avoids "novel"/"first." |
| P10-NC2 | P10 establishes performance superiority or safety improvement. | non_claim | none | none | none | no | No such claims in abstract. |
| P10-NC3 | P10 claims publication readiness. | non_claim | none | none | none | no | Abstract marked "draft v1, not final." |

| P11-A1 | P11 creates a full-manuscript claim audit covering 19 claims across 7 sections. 0 overclaims found. | supported_structural_claim | `paper/manuscript/full_manuscript_claim_audit_v1.md` | audit artifact | high | no | Confirms claim-governance integrity. |
| P11-A2 | P11 creates a prioritized revision plan: 0 P0, 3 P1, 3 P2, 2 P3. | supported_structural_claim | `paper/manuscript/manuscript_revision_plan_v1.md` | revision plan artifact | medium | no | Codex can execute P1/P2 items in P12. |
| P11-A3 | All 12 numeric items verified traceable to source artifacts. | supported_by_project_artifact | `paper/tables/numeric_traceability_table.md` | numeric audit artifact | high | no | No fabricated numbers. |
| P11-A4 | All 8 cited keys in .bib; 8 matrix-only entries documented as missing. | supported_by_literature | `paper/tables/citation_audit_table.md` | citation audit artifact | high | no | No rejected/unverified sources cited. |
| P11-NC1 | P11 establishes submission readiness. | non_claim | none | none | none | no | submission_readiness=not_submission_ready. |
| P11-NC2 | P11 writes new manuscript sections. | non_claim | none | none | none | no | new_manuscript_sections_written=false. |

| P12-R1 | P12 resolves 5/8 Codex-editable P11 issues: stale references, path verification, heading consistency, figure notes. | supported_structural_claim | `paper/manuscript/manuscript_v1_revision_changelog.md` | revision artifact | high | no | All claim boundaries preserved. |
| P12-R2 | P12 creates manuscript v1 assembly with Abstract through Conclusion, evidence gaps, and revision notes. | supported_structural_claim | `paper/manuscript/manuscript_v1_assembly.md` | manuscript assembly artifact | medium | no | Not submission ready. |
| P12-R3 | P12 post-revision consistency check confirms all terminology, claims, citations, and numbers remain consistent. | supported_structural_claim | `paper/manuscript/manuscript_v1_consistency_check.md` | consistency artifact | high | no | revision_v1_complete. |
| P12-NC1 | P12 establishes submission readiness. | non_claim | none | none | none | no | submission_readiness=not_submission_ready. |
| P12-NC2 | P12 adds new scientific results or sections. | non_claim | none | none | none | no | new_scientific_results_added=false. |

| P13-R1 | P13 adds 8 verified BibTeX entries to seed_references.bib (total 16 entries). All fields from P1 metadata only. | supported_structural_claim | `paper/related_work/seed_references.bib` | citation artifact | high | no | No fabricated fields. |
| P13-R2 | P13 strengthens Related Work §4 (3->4 citations) and §5 (1->3 citations) with P1-verified sources. | literature_context | `paper/manuscript/sections/02_related_work_draft_v1.md` | manuscript section | medium | no | Context only; no novelty claim. |
| P13-NC1 | P13 establishes final novelty. | non_claim | none | none | none | no | No claim wording changed. |
| P13-NC2 | P13 fabricates citation metadata. | non_claim | none | none | none | no | fabricated_metadata=false. |

| M19-F1 | M19 generates method pipeline figure (.mmd) with 12 nodes, validation lane, and prohibited execution path markings. | supported_structural_claim | `paper/figures/method_pipeline_figure.mmd` | figure asset | medium | no | Ready for SVG rendering. |
| M19-F2 | M19 generates evidence chain figure (.mmd) with 15 nodes and color-coded claim categories. | supported_structural_claim | `paper/figures/evidence_chain_figure.mmd` | figure asset | medium | no | Ready for SVG rendering. |
| M19-NC1 | M19 establishes publication readiness. | non_claim | none | none | none | no | submission_readiness=not_submission_ready. |

| M19.1-I1 | M19.1 completes figure/table caption packs, table packs, evidence-gap figure, integration plan, and figure/table claim audit. | supported_structural_claim | 8 new asset files | presentation asset | medium | no | No new scientific claims. |
| M19.1-NC1 | M19.1 establishes publication readiness. | non_claim | none | none | none | no | submission_readiness unchanged. |

| P14-V1 | P14 creates polished manuscript v2 assembly with integrated figure/table references and main/appendix asset separation. | supported_structural_claim | `paper/manuscript/manuscript_v2_assembly.md` | manuscript assembly artifact | medium | no | Not submission ready. |
| P14-V2 | P14 creates main-paper and appendix asset plans (5 main + 13 appendix) with consistent cross-references. | supported_structural_claim | `paper/tables/p14_main_paper_asset_plan.md` | asset plan artifact | low | no | All captions claim-safe. |
| P14-NC1 | P14 establishes submission readiness. | non_claim | none | none | none | no | submission_readiness=not_submission_ready. |
