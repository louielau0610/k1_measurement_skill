# P8 Manuscript-Level Claim Audit

## Purpose

Manuscript-level claim audit for the P8 assembly v0. Verifies that claims are consistent across all sections, no section overclaims, and the abstract/conclusion boundaries are respected.

## Inputs inspected

All P3-P7 section drafts, P3-P7 claim audits, M18 claim audit, claim registry, evidence table, non-claims, literature matrix, seed references .bib.

## Allowed manuscript-level claims

- The repository contains an offline, artifact-governed, five-stage pipeline. (allowed_structural_claim, supported by M13-M18 artifacts, all sections)
- The pipeline converts real K1 measurement artifacts into dataset records, response predictions, risk assessments, and evaluation artifacts. (allowed_structural_claim, §1, §3, §4, §5)
- Dataset v1 contains 5 records (4 numeric, 1 qualitative-only at 0.10 m/s). (allowed_structural_claim, §3, §4)
- The response model produces conservative predictions with categorical uncertainty labels. (allowed_structural_claim, §3, §4, §5)
- The risk map produces advisory assessments with warning metadata. (allowed_structural_claim, §3, §4, §5)
- Claim governance separates structural evidence from performance claims. (allowed_structural_claim, §3, §4, §5)
- Current evidence is structural and does not support performance or safety claims. (allowed_structural_claim, all sections)

## Candidate contributions

All 4 contribution statements remain "candidate"/"tentative" across all sections. Status: `candidate_contribution_wording`.

## Claims requiring more experiments

- Predictive accuracy of the response model. (§4, §5)
- Calibrated uncertainty estimates. (§4, §5, §6)
- Navigation outcome impact of advisory risk labels. (§4, §5, §7)
- Cross-environment generalization. (§4, §5, §6)

## Claims requiring more literature

- Novelty of deployment-layer black-box response calibration. (§2, §5)
- Final gap claim relative to system-ID and commercial SDK literature. (§2, §5)

## Prohibited claims

All 15+ prohibited claims from M18 audit remain absent from all sections:
- No final novelty, no performance superiority, no navigation safety improvement, no collision reduction, no success-rate improvement, no compensation readiness, no safe command adapter readiness, no publication readiness, no calibrated uncertainty (in positive sense), no generalization claim.

## Abstract/conclusion warning

Abstract and Conclusion are intentionally placeholder-only in P8 assembly. No abstract or conclusion prose exists. This satisfies the "do not write final abstract/conclusion" requirement for P8.

## Section-specific claim risks

| section | risk | mitigation |
| --- | --- | --- |
| Introduction §3 | candidate gap wording could be interpreted as novelty claim | Explicitly states "before any final gap or novelty claim can be made" |
| Related Work §6 | "seed literature does not yet establish" could be read as absence-of-evidence claim | Follows with "further literature review... before any final gap claim" |
| Method §3.5 | exact-source MAE=0.0 could be misinterpreted as accuracy | Labeled "structural sanity check, not predictive accuracy claim" |
| Experiments §4.4 | MAE=0.0 appears in evaluation section | Contextualized as sanity check, held-out evaluation listed as unavailable |
| Discussion §5.2 | "candidate contribution" could be read as strong uniqueness claim | Followed by "does not claim that no prior work examines externally measured robot response" |

## Claim audit table

| manuscript_claim_or_wording | status | sections_affected | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- | --- |
| Five-stage artifact-governed pipeline exists. | allowed_structural_claim | §1, §3, §4, §5 | M13-M18 artifacts | "artifact-governed, five-stage pipeline" | "validated performance pipeline" |
| Dataset v1: 5 records, 4 numeric, 1 qualitative-only. | allowed_structural_claim | §3, §4 | dataset v1 + model eval | "5 records, 4 numeric, 1 qualitative-only" | "comprehensive dataset" |
| Model produces conservative predictions with categorical uncertainty. | allowed_structural_claim | §3, §4, §5 | model predictions + eval | "conservative response predictions with categorical uncertainty labels" | "accurate velocity predictions" |
| Exact-source MAE=0.0 is structural sanity check. | allowed_structural_claim | §3, §4 | model eval | "structural sanity check, not predictive accuracy" | "predictive accuracy of 0.0 m/s" |
| Risk map produces advisory assessments. | allowed_structural_claim | §3, §4, §5 | risk map + eval | "advisory risk assessments with warning metadata" | "validated navigation risk" |
| Contribution: artifact-governed pipeline. | candidate_contribution_wording | §1, §5 | M13-M18 + P2-P5 | "candidate contribution" | "final contribution / novel pipeline" |
| Contribution: dataset and model contract. | candidate_contribution_wording | §1, §5 | M14-M15R | "tentative... requires more evidence" | "novel dataset/model method" |
| Contribution: advisory risk layer. | candidate_contribution_wording | §1, §5 | M16 | "offline advisory risk interpretation" | "navigation safety improvement" |
| Contribution: claim-governed evaluation. | candidate_contribution_wording | §1, §5 | M17 + claim docs | "claim-governed evaluation package" | "publication-ready" |
| No navigation safety improvement. | allowed_structural_claim | §4, §5, §6 | M17 non-claims + risk eval | "navigation safety improvement has not been evaluated" | "improves navigation safety" |
| No calibrated uncertainty. | allowed_structural_claim | §3, §4, §5, §6 | M15R model + model eval | "not calibrated probabilities" | "calibrated uncertainty estimates" |
| No compensation or safe adapter. | allowed_structural_claim | §1, §3, §4, §5, §6 | all code safety flags | "not implemented and remains future work" | "compensation-ready" |
| Abstract is placeholder only. | allowed_structural_claim | manuscript header | no abstract prose exists | — | "final abstract" |
| Conclusion is placeholder only. | allowed_structural_claim | manuscript footer | no conclusion prose exists | — | "final conclusion" |
