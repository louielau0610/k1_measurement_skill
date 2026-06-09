# P13 Citation Claim Audit

## Purpose

Verify that P13 citation additions preserve all claim boundaries and do not introduce overclaims.

## Citation changes made

- 8 BibTeX entries added to `seed_references.bib` from verified P1 metadata.
- 3 new citation keys cited in Related Work §4 (§5): FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025.
- Total manuscript citation keys: 8 (original) + 3 (newly cited) = 11 cited keys across all sections.

## Claim changes made

None. The Related Work text additions are purely context citations. No claim wording was strengthened, no gap claim was upgraded to novelty, and no performance comparison was introduced.

## Claims unchanged

All 19 P11 claims remain identical in classification. No claim was upgraded. No new claim type was introduced.

## Sources safe for context claims

- FanArxiv2021Costmaps (partially_verified): used in Related Work §4 as context for risk-aware costmap learning — not for core novelty claim.
- BenrabahSensors2024 (verified): review paper used in §4 and §5 as context for taxonomy and metrics — not for core novelty claim.
- FrancisTOHRI2025 (verified): evaluation guidelines used in §5 as context for metrics frameworks — not for core novelty claim.

## Sources not safe for core claims

Partially verified sources (DaoArxiv2026, GangapurwalaArxiv2020, GrandiaTRO2023, FanArxiv2021Costmaps) should not be used to support "this gap is novel," "no prior work exists," or "our method outperforms" statements. They are currently used only for literature context or not cited in the manuscript.

## Prohibited literature-based overclaims

The following remain absent:
- "no prior work exists in closed-source calibration"
- "first artifact-governed pipeline"
- "the reviewed literature proves the gap"
- "our method outperforms all reviewed approaches"

## Remaining risks

- FanArxiv2021Costmaps is a preprint — venue not confirmed. If peer review reveals issues, the citation should be reviewed.
- BenrabahSensors2024 authors field approximated from P1 — full author list should be verified if journal citation is needed.
- No commercial SDK calibration literature reviewed — this remains a gap for novelty claims.

## Claim audit table

| claim_or_citation_use | source_keys | status | allowed_use | prohibited_use | action_needed |
| --- | --- | --- | --- | --- | --- |
| Risk-aware traversability context (§4) | FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024 | literature_context | position candidate gap | prove gap is novel | none |
| Field metrics context (§5) | FanRSS2021STEP, BenrabahSensors2024, FrancisTOHRI2025 | literature_context | justify metric vocabulary | claim our metrics follow these standards | none |
| All BibTeX entries added | 8 new entries | various (verified/partial) | track citations | claim these sources support novelty | DOI verification |
| No novelty claim added | — | candidate_contribution | — | "first," "novel," "gap is proven" | none |
