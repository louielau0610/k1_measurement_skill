# P4 Introduction Claim Audit

## Purpose

P4 creates a citation-safe Introduction draft v1, a formal Problem Statement, and title/contribution options. This audit verifies that every paragraph is safe, every citation is traceable, and no prohibited wording appears.

## Inputs inspected

- `.agents/skills/autoresearch/SKILL.md`
- `paper/related_work/literature_matrix.md`
- `paper/related_work/seed_references.bib`
- `paper/related_work/seed_literature_search_report.md`
- `paper/related_work/related_work_claim_map.md`
- `paper/manuscript/sections/02_related_work_draft_v1.md`
- `paper/claims/p3_related_work_claim_audit.md`
- `paper/claims/literature_gap_candidates.md`
- `paper/positioning/gap_analysis_v1.md`
- `paper/positioning/related_work_positioning_table.md`
- `paper/positioning/contribution_candidates_v1.md`
- `paper/claims/claim_upgrade_plan.md`
- `paper/positioning/paper_framing_options_v1.md`
- `paper/claims/m18_claim_audit.md`
- `paper/claims/claim_registry.md`
- `paper/claims/evidence_table.md`
- `paper/claims/non_claims.md`
- `paper/manuscript/manuscript_scaffold.md`
- `paper/manuscript/sections/03_method_skeleton.md`
- `paper/manuscript/sections/04_experiments_skeleton.md`
- `paper/tables/method_artifact_evidence_table.md`
- `paper/tables/current_metrics_and_missing_evidence_table.md`
- `outputs/research_evaluation/m17_pipeline_evaluation_report.json`
- `outputs/research_foundation/m18_method_skeleton_summary.json`
- `outputs/research_foundation/p3_related_work_summary.json`

## Citation safety checks

- **Cited in Introduction draft**: 8 citation keys (TanRSS2018, HwangboSciRobot2019, KumarRMA2021, MargolisRSS2022, FuCVPRW2022, FanRSS2021STEP, YangRAL2022, MaRSS2024DrEureka).
- **Cited in title/contribution options**: 5 citation keys (TanRSS2018, YangRAL2022, MargolisRSS2022, FanRSS2021STEP, FuCVPRW2022).
- **All cited keys present in `seed_references.bib`**: confirmed.
- **Rejected sources cited**: none.
- **Unverified sources cited**: none.
- **Fabricated citations**: none.
- **Fabricated metadata**: none.

## Introduction claims allowed

- Deployment-layer command-to-motion mismatch is a measurable real-robot problem. (allowed_context_claim)
- Closed-source robots make the command-response relationship opaque. (allowed_context_claim)
- Prior work in sim-to-real, adaptation, navigation-coupled locomotion, and risk-aware planning is relevant context. (allowed_context_claim)
- The repository implements a five-stage artifact-governed pipeline. (allowed_structural_claim)
- Current evidence is structural and does not support performance or safety claims. (allowed_structural_claim)
- Contributions are tentative and require more evidence. (allowed_structural_claim)

## Introduction claims requiring more evidence

- The gap for closed-source deployment-layer calibration is real. (requires_more_literature)
- Any contribution is final or novel. (requires_more_literature + requires_more_experiment)
- Response labels are calibrated uncertainty. (requires_more_experiment)
- Risk labels improve navigation outcomes. (requires_more_experiment)

## Contribution wording audit

The Introduction draft uses the following contribution formulations:

| contribution | wording used | status |
| --- | --- | --- |
| Pipeline | "an artifact-governed measurement-to-model-to-risk-map pipeline" | candidate_contribution_wording |
| Dataset/model | "a sparse-evidence velocity response dataset and model contract" | candidate_contribution_wording |
| Risk layer | "an offline advisory risk interpretation layer" | candidate_contribution_wording |
| Claim governance | "a claim-governed evaluation package" | candidate_contribution_wording |

All contribution statements are prefaced with "The work currently contributes" and followed by "All contributions remain tentative... not final novelty." This framing is conservative and acceptable.

## Problem statement audit

The problem statement defines formal variables, system boundary, input/output, current scope, and future evidence needs. It correctly:

- Marks `v_y` and `omega_z` as schema-supported but not yet measured.
- Labels uncertainty/confidence as metadata flags, not calibrated probabilities.
- Clarifies that risk assessment is offline/advisory, not navigation control.
- Lists compensation, safe adapter, and navigation control as out of scope.

No prohibited claims appear in the problem statement.

## Abstract-warning notes

No abstract was written. The Introduction draft §7 is a "Paper organization placeholder" explicitly marked as a draft note. The title/contribution options are explicitly marked as tentative. This satisfies the "do not write a final abstract" requirement.

## Prohibited wording

The following terms are absent from all P4 drafts when used as positive claims:

- "novel" (used only in negating context: "not final novelty", "does not establish novelty")
- "first"
- "state-of-the-art"
- "outperforms"
- "solves"
- "guarantees safety"
- "proves"
- "generalizes to all"
- "calibrated probabilities" (used only as "not calibrated probabilities")
- "improves navigation safety"
- "reduces collision rate"

## Novelty-claim boundary

P4 does not cross into novelty territory. The Introduction draft §3 uses the P3-established language: "The current seed literature does not yet establish... motivates the present repository as a candidate contribution... before any final gap or novelty claim can be made." Contribution statements are explicitly marked as tentative. The title/contribution options document explicitly states "No final title selected. No final contribution structure claimed."

## Claim audit table

| wording_or_claim | status | citations | project_evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- | --- |
| Deployment mismatch is a measurable problem for legged robots. | allowed_context_claim | TanRSS2018, HwangboSciRobot2019, MargolisRSS2022 | M13-M14 project artifacts | "deployment-layer response characteristic" | "proven safety hazard" |
| Closed-source SDK makes command-response opaque. | allowed_context_claim | — | M7-M8 measurement protocol | "the connection... is a black-box system" | "therefore unsafe for deployment" |
| Prior work covers sim-to-real, adaptation, navigation coupling, and risk-aware planning. | allowed_context_claim | TanRSS2018, HwangboSciRobot2019, KumarRMA2021, MargolisRSS2022, FuCVPRW2022, FanRSS2021STEP | P1 matrix, P3 draft | "prior work addresses several adjacent problems" | "prior work ignores deployment mismatch" |
| Seed literature does not yet establish equivalent closed-source pipeline. | candidate_gap_wording | TanRSS2018, YangRAL2022, MargolisRSS2022 | P2 gap analysis, P3 draft | "The current seed literature does not yet establish..." | "no prior work exists" |
| Five-stage pipeline exists and is reproducible. | allowed_structural_claim | — | M13-M18 artifacts | "implements an artifact-governed pipeline" | "validated performance pipeline" |
| Pipeline is measurement-only and advisory. | allowed_structural_claim | — | M17 non-claims, M18 audit | "measurement-only and advisory" | "ready for compensation" |
| Artifact-governed pipeline is a tentative contribution. | candidate_contribution_wording | — | M13-M17 + P2-P3 docs | "All contributions remain tentative" | "final contributions" |
| Response labels are not calibrated probabilities. | allowed_context_claim | — | M15R outputs, M17 limitations | "not calibrated probabilities" | "calibrated uncertainty estimates" |
| Risk map provides advisory metadata only. | allowed_context_claim | FanRSS2021STEP | M16 outputs | "offline advisory risk interpretation" | "navigation safety improvement" |
| No abstract has been finalized. | allowed_structural_claim | — | scaffold and draft markers | "not a substitute for a paper abstract" | "final abstract" |
