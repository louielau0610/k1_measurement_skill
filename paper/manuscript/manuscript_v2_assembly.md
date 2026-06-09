# Manuscript v2 Assembly

> **Manuscript v2 draft. Not submission ready.**
> Based on P14 polish after M19/M19.1 figure/table integration.
> Structural/artifact-level evidence only. Real navigation outcome evidence remains unavailable.
> **No publication readiness claim. No final novelty claim. No performance/safety claim.**

## Working title (tentative)

**Artifact-Governed Black-Box Command-to-Motion Response Modeling for Closed-Source Legged Robot Deployment**

> Final title not selected. Options documented at `paper/manuscript/sections/00_title_and_contribution_options_v1.md`.

---

## Abstract

> Source: `paper/manuscript/sections/00_abstract_draft_v1.md` (primary, 193 words)

Closed-source legged robots present a deployment challenge: navigation systems issue velocity commands through manufacturer-provided SDK interfaces, but the mapping from commanded velocity to actual robot motion is opaque to the user. When commanded motion does not faithfully translate into executed motion — through deadzone behavior, under-tracking, or systematic mismatch — downstream planning decisions may rely on inaccurate assumptions about robot capability. This paper presents an offline, artifact-governed pipeline for characterizing the black-box command-to-motion response relationship of a closed-source quadruped. The pipeline converts real measurement artifacts into a schema-validated velocity response dataset, produces conservative response predictions with categorical uncertainty and reliability labels, and translates prediction evidence into advisory navigation-risk assessments with explicit warning metadata. All pipeline stages carry documented safety flags confirming that compensation, inverse command mapping, and safe command adaptation are not implemented. Evaluated on sparse forward-velocity evidence from a single K1 robot, the current implementation produces a consistent, reproducible chain of artifacts: five dataset records (four numeric, one qualitative-only), five response predictions with uncertainty labels, and five advisory risk assessments across three risk levels. The work provides an evidence-governed foundation for studying deployment-layer reliability in closed-source legged robots, establishes clear boundaries between structural artifact validation and unsupported performance claims, and identifies the repeated multi-trial experiments required before navigation outcome or safety claims can be evaluated.

---

## 1. Introduction

> Source: `paper/manuscript/sections/01_introduction_draft_v1.md` (P4, P12 revised)

[Introduction content from section draft — see source file for full text.]

---

## 2. Related Work

> Source: `paper/manuscript/sections/02_related_work_draft_v1.md` (P3, P13 updated)

[Related Work content from section draft — see source file for full text. Covers sim-to-real, adaptation, navigation-coupled locomotion, risk-aware navigation, field metrics, black-box calibration, and project positioning. §4 and §5 strengthened with P13 citations.]

---

## 3. Method

> Source: `paper/manuscript/sections/03_method_draft_v1.md` (P5)

**[Figure 1]** *Artifact-Governed Velocity Response Pipeline* — pipeline overview showing measurement artifacts through schema, dataset, model, risk mapper, and claim governance. Prohibited execution paths (compensation, navigation control, safe adapter) explicitly marked. Mermaid source: `paper/figures/method_pipeline_figure.mmd`. Caption: `paper/figures/figure_caption_pack_v1.md` (Figure 1).

**[Table 1]** *Method Stage I/O Contract* — five-stage input/output table with producer scripts and explicit non-goals. Source: `paper/tables/main_paper_table_pack_v1.md` (Table 1).

[Method section content from draft — see source file for full text. Covers system boundary, problem formulation with formal notation, five pipeline stages with pseudo-algorithms, reproducibility, and scope/limitations.]

---

## 4. Experiments and Evaluation

> Source: `paper/manuscript/sections/04_experiments_draft_v1.md` (P6)

**[Figure 2]** *Evidence Chain and Claim Governance* — evidence flow from raw measurement through validation, prediction, risk mapping, and evaluation, branching into claim categories with prohibited claims marked. Mermaid source: `paper/figures/evidence_chain_figure.mmd`. Caption: `paper/figures/figure_caption_pack_v1.md` (Figure 2).

**[Table 2]** *Current Evaluation Metrics* — summary of available structural metrics (5 records, 5 predictions, 5 risk assessments) and unavailable performance/safety metrics. Source: `paper/tables/main_paper_table_pack_v1.md` (Table 2).

[Experiments section content from draft — see source file for full text. Covers 5 evaluation questions, reproducible artifact chain, dataset evidence, model evaluation, risk evaluation, claim-governed evaluation, current vs. missing metrics, and future experimental protocol.]

---

## 5. Discussion and Limitations

> Source: `paper/manuscript/sections/05_discussion_limitations_draft_v1.md` (P7)

**[Table 3]** *Evidence Boundary / Claim-Upgrade Requirements* — maps each claim type to current status and required evidence before upgrade. Source: `paper/tables/main_paper_table_pack_v1.md` (Table 3).

[Discussion and Limitations content from draft — see source file for full text. Covers pipeline demonstration, deployment-layer positioning, uncertainty labels, advisory risk mapping, claim governance, dataset/model/risk/system/generalization limitations, and future work.]

---

## 6. Conclusion

> Source: `paper/manuscript/sections/06_conclusion_draft_v1.md` (P9)

[Conclusion content from section draft — see source file for full 619-word conclusion.]

---

## Main-Paper Figure and Table Plan

| asset | type | location | source |
| --- | --- | --- | --- |
| Figure 1 | method pipeline diagram | Method §3 | `paper/figures/method_pipeline_figure.mmd` |
| Figure 2 | evidence chain diagram | Experiments §4 | `paper/figures/evidence_chain_figure.mmd` |
| Table 1 | method I/O contract | Method §3 | `paper/tables/main_paper_table_pack_v1.md` |
| Table 2 | current evaluation metrics | Experiments §4 | `paper/tables/main_paper_table_pack_v1.md` |
| Table 3 | claim-upgrade requirements | Discussion §5 | `paper/tables/main_paper_table_pack_v1.md` |

## Appendix/Supplement Plan

| asset | type | location |
| --- | --- | --- |
| Figure 3 | evidence gap boundary (optional) | Appendix |
| Tables A-D | audit/supplement tables | Appendix A-G |
| Numeric traceability | detailed metric-to-artifact map | Appendix A |
| Citation audit | 16-row citation status table | Appendix B |
| Terminology reference | 10-term consistency table | Appendix D |
| Full claim matrix | 19-row manuscript claim audit | Appendix F |

Full appendix table pack: `paper/tables/appendix_table_pack_v1.md`.

## Current Claim Boundaries

All claims in this assembled manuscript are governed by:
- `paper/claims/claim_registry.md`
- `paper/claims/evidence_table.md`
- `paper/claims/non_claims.md`
- P11 full-manuscript claim audit
- P14 manuscript v2 claim audit

**Key boundaries**:
- No final novelty claim. No performance superiority claim. No navigation safety improvement claim.
- Uncertainty labels are categorical, not calibrated probabilities.
- Risk map is advisory/offline, not navigation control.
- Compensation, inverse command mapping, and safe command adapter are not implemented.
- Publication readiness is not claimed.

## Remaining Evidence Gaps

- No real navigation outcome evidence.
- No held-out command evaluation.
- Single robot, single surface, single session.
- Sparse command grid (5 forward-velocity points; no v_y or omega_z).
- No calibrated uncertainty.
- No collision, near-miss, or success-rate metrics.
- Figures not rendered to SVG (Mermaid .mmd sources only).

These gaps require future experiments and final rendering before any performance, safety, or generalization claim can be supported.

## P14 Revision Notes

- Revised: P14 (manuscript v2 polish).
- Figure/table references integrated at Method (Figure 1, Table 1), Experiments (Figure 2, Table 2), Discussion (Table 3).
- Appendix/supplement asset plan separated from main-paper assets.
- Prose preserved from section drafts — no new scientific content.
- All claim boundaries verified against P11/P12/P13/M19.1 audits.
- Previous assembly: manuscript v1 (P12).
