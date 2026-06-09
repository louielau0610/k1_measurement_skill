# Manuscript v0 Consistency Audit

## Purpose

Cross-section audit of the P8 manuscript v0 assembly. Identifies terminology drift, contribution wording inconsistencies, claim boundary violations, citation gaps, figure/table references, section flow issues, and remaining gaps.

## Inputs inspected

All 7 manuscript section drafts (00-05), 9 table artifacts, 2 figure specs, 5 P3-P7 claim audits, literature matrix, seed references .bib, M17 evaluation JSON, scaffold, and section README.

## 1. Terminology consistency

| preferred_term | consistency_status | notes |
| --- | --- | --- |
| artifact-governed pipeline | consistent | Used uniformly across Introduction, Method, Discussion. |
| black-box / closed-source / command-response | consistent with minor variants | "black-box command-to-motion response", "closed-source legged robot", "deployment-layer response characterization" — all equivalent. |
| velocity response dataset | consistent | "Dataset v1" used consistently. |
| uncertainty-aware response model | consistent | "uncertainty_aware_hybrid_v1", "response model foundation". |
| categorical uncertainty label | consistent | Always "categorical reliability marker, not calibrated probability." |
| advisory navigation risk mapping | consistent | "advisory risk assessment", "offline/advisory" across Method, Experiments, Discussion. |
| structural validation | consistent | Clear distinction from "performance validation" maintained in Experiments and Discussion. |
| claim-governed evaluation | consistent | "claim governance", "claim-governed evaluation package" used coherently. |
| candidate contribution | consistent | All contribution statements use "candidate"/"tentative" language. |

**Verdict**: No significant terminology drift. Minor allowed variants are semantically equivalent. Preferred terms established in `paper/tables/terminology_consistency_table.md`.

## 2. Contribution wording consistency

The same 4 contribution bullets appear in Introduction §5 and are echoed in Discussion §5.1-5.5. The P5 Method draft describes pipeline stages without making separate contribution claims. The Discussion adds interpretation but keeps contributions tentative.

| contribution | Introduction | Discussion | consistent? |
| --- | --- | --- | --- |
| artifact-governed pipeline | "artifact-governed measurement-to-model-to-risk-map pipeline" | "demonstrates that an offline, artifact-governed pipeline can transform..." | yes |
| dataset and model contract | "sparse-evidence velocity response dataset and model contract" | "schema-valid dataset of 5 command-response records" | yes |
| advisory risk layer | "offline advisory risk interpretation layer" | "advisory risk assessments that can inform downstream planning" | yes |
| claim-governed evaluation | "claim-governed evaluation package" | "claim-governance infrastructure that accompanies the pipeline" | yes |

All use "candidate contribution" / "tentative" framing. No section upgrades any contribution to "final."

**Verdict**: Consistent. All contributions remain tentative.

## 3. Claim consistency

| prohibited claim | Introduction | Related Work | Method | Experiments | Discussion |
| --- | --- | --- | --- | --- | --- |
| final novelty | not claimed | not claimed | not claimed | not claimed | not claimed |
| performance superiority | not claimed | not claimed | not claimed | not claimed | not claimed |
| navigation safety improvement | not claimed | not claimed | not claimed | "no safety improvement" | "open question" |
| collision reduction | not claimed | not claimed | not claimed | "no collision data" | "open question" |
| calibrated uncertainty | "not calibrated probabilities" | "not calibrated probabilities" | "not calibrated probabilities" | "not calibrated" | "not calibrated" |
| compensation readiness | "not implemented" | "not implemented" | "not implemented" | "not available" | "future work" |
| publication readiness | not claimed | not claimed | not claimed | not claimed | not claimed |

**Verdict**: No prohibited claim appears in any section. All sections maintain the conservative claim boundary.

## 4. Citation consistency

**Keys used across all sections**: TanRSS2018, HwangboSciRobot2019, KumarRMA2021, MargolisRSS2022, FuCVPRW2022, FanRSS2021STEP, YangRAL2022, MaRSS2024DrEureka — all 8 confirmed present in `seed_references.bib`.

**Verification status**: 7 verified, 1 partially verified (KumarRMA2021). Partially verified key used only in Introduction §3 and Discussion §5.2 — context statements, not core claims.

**8 uncited matrix entries**: RudinCoRL2021, MargolisCoRL2022, DaoArxiv2026, GangapurwalaArxiv2020, GrandiaTRO2023, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025 — lack BibTeX entries. Documented in P3/P4 draft limitations.

**Verdict**: All citations traceable. No rejected or unverified sources cited. BibTeX entries needed for 8 matrix-only items before submission.

## 5. Figure/table reference consistency

| reference | introduced in | content exists | status |
| --- | --- | --- | --- |
| method pipeline figure | Method §3 Overview | `paper/figures/method_pipeline_figure_spec.md` | spec only; no rendered figure |
| evidence chain figure | — | `paper/figures/evidence_chain_figure_spec.md` | spec only; no rendered figure |
| method artifact evidence table | Method §3.7-3.8 | `paper/tables/method_artifact_evidence_table.md` | table exists |
| experiment metrics table | Experiments §4.7 | `paper/tables/experiment_metrics_status_table.md` | table exists |
| claim upgrade table | Discussion §5.5 | `paper/tables/claim_upgrade_requirements_table.md` | table exists |
| EQ artifact map | Experiments §4.1 | `paper/tables/evaluation_question_artifact_map.md` | table exists |

**Verdict**: All referenced tables exist. Figures are specifications only — rendering is deferred to M19.

## 6. Section flow consistency

| transition | assessment |
| --- | --- |
| Introduction → Related Work | ✓ Introduction motivates the black-box problem; Related Work positions it against prior art. |
| Related Work → Method | ✓ Related Work identifies candidate gap; Method describes the pipeline that addresses it. |
| Method → Experiments | ✓ Method defines pipeline stages; Experiments reports stage outputs. |
| Experiments → Discussion | ✓ Experiments reports structural results; Discussion interprets their meaning and limitations. |
| Discussion → Conclusion | ✗ Conclusion is placeholder only — not yet written. |

**Verdict**: Narrative flow is coherent through Discussion. Conclusion gap is a known remaining task (P9).

## 7. Remaining manuscript gaps

| gap | severity | blocking for next? |
| --- | --- | --- |
| Final title not selected | low | no |
| Abstract not written | medium | yes, for P10 |
| Conclusion not written | medium | yes, for P9 |
| Figures not rendered (specs only) | medium | yes, for M19 |
| 8 BibTeX entries missing for matrix-only papers | medium | yes, before submission |
| No real navigation outcome evidence | high | yes, for any safety/performance claim |
| No held-out evaluation | high | yes, for predictive performance claim |
| No cross-environment replication | high | yes, for generalization claim |
| Single robot, single session | high | yes, for robustness claim |
| Publication readiness not claimed | expected | correct per claim governance |

## Recommended next milestones

1. **P9**: Conclusion draft — synthesizes manuscript into a conservative closing section.
2. **P10**: Abstract draft — written last, after all sections and conclusion are reviewed.
3. **M19**: Figure generation — render pipeline and evidence-chain figures from specs.
4. **Literature expansion**: Add 8 missing BibTeX entries; broaden system-ID and commercial SDK search.
5. **Experimental expansion**: Multi-trial, multi-surface K1 data collection before performance claims.

## Issue table

| issue_id | category | location | issue | severity | recommended_fix | blocking_for_next_step |
| --- | --- | --- | --- | --- | --- | --- |
| C-01 | section_gap | manuscript §6 | Conclusion is placeholder only | medium | Write conclusion in P9 | yes, for P10 abstract |
| C-02 | section_gap | manuscript abstract | Abstract is placeholder only | medium | Write abstract in P10 | yes, for manuscript completeness |
| C-03 | figure_gap | manuscript planned figures | Figures are specs only, not rendered | medium | Render figures in M19 | no, prose can stand alone |
| C-04 | citation_gap | all sections | 8 matrix entries lack BibTeX entries | medium | Add BibTeX entries before submission | no, existing 8 keys suffice for v0 |
| C-05 | evidence_gap | Experiments, Discussion | No real navigation outcome evidence | high | Navigation trials required before safety claims | yes, for any performance/safety claim |
| C-06 | evidence_gap | Experiments, Discussion | No held-out evaluation exists | high | Repeated trials + hold-out split required | yes, for predictive accuracy claim |
| C-07 | evidence_gap | Experiments, Discussion | Single robot, single surface, single session | high | Multi-robot, multi-surface experiments required | yes, for generalization claim |
| C-08 | heading_numbering | manuscript assembly | Section heading renumbering done during assembly | low | Review for LaTeX export consistency in future milestone | no |
