# P3 Related Work Claim Audit

## Purpose

P3 creates a citation-safe Related Work draft v1 that synthesizes P1/P2 literature and respects M18 claim boundaries. This audit verifies that every paragraph is safe, every citation is traceable, and no prohibited wording appears.

## Inputs inspected

- `paper/related_work/literature_matrix.md` (16 entries, 11 verified, 5 partially verified)
- `paper/related_work/seed_references.bib` (8 BibTeX entries)
- `paper/related_work/citation_verification_report.json`
- `paper/related_work/rejected_sources.md`
- `paper/claims/literature_gap_candidates.md`
- `paper/positioning/gap_analysis_v1.md`
- `paper/positioning/related_work_positioning_table.md`
- `paper/positioning/contribution_candidates_v1.md`
- `paper/claims/claim_upgrade_plan.md`
- `paper/positioning/paper_framing_options_v1.md`
- `paper/claims/claim_registry.md`
- `paper/claims/evidence_table.md`
- `paper/claims/non_claims.md`
- `paper/claims/m18_claim_audit.md`
- `paper/manuscript/manuscript_scaffold.md`
- `paper/manuscript/sections/03_method_skeleton.md`
- `paper/manuscript/sections/04_experiments_skeleton.md`
- `.agents/skills/autoresearch/SKILL.md`

## Citation safety checks

- **Cited in draft**: 8 citation keys, all verified or partially verified and all present in `seed_references.bib`.
- **Not cited (no BibTeX entry)**: RudinCoRL2021, MargolisCoRL2022, DaoArxiv2026, GangapurwalaArxiv2020, GrandiaTRO2023, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025.
- **Rejected sources**: none cited.
- **Fabricated citations**: none.
- **Fabricated metadata**: none.

## Related-work claims allowed

- Prior work establishes sim-to-real mismatch as a relevant legged robot problem. (supported_by_prior_work)
- Prior work establishes deployment adaptation and system identification as relevant contexts. (literature_context_claim)
- Prior work establishes navigation/locomotion coupling and risk-aware traversability as relevant contexts. (literature_context_claim)
- The seed literature does not yet establish a directly equivalent artifact-governed closed-source command-response pipeline. (candidate_gap_wording)
- The pipeline is a candidate contribution and not final novelty. (allowed_context_claim)

## Related-work claims requiring more evidence

- Specific gap for closed-source deployment-layer command-response calibration. (requires_more_literature)
- Calibrated uncertainty or risk probability equivalence. (requires_more_experiment)
- Navigation outcome impact of advisory risk labels. (requires_more_experiment)
- Generality across robots, surfaces, or sessions. (requires_more_experiment)

## Prohibited wording

- "improves navigation safety"
- "reduces collision rate"
- "outperforms prior work"
- "solves closed-source robot calibration"
- "calibrated probabilities"
- "state-of-the-art"
- "novel" (as final claim)
- "guarantees safety"

## Candidate gap wording

The draft uses the following conservative candidate-gap language:

- "The current seed literature does not yet establish a directly equivalent artifact-governed pipeline..."
- "This motivates further literature review..."
- "...before any final gap or novelty claim can be made."

These formulations follow P2/M18 positioning: they identify a plausible gap without claiming it is proven.

## Novelty-claim boundary

The draft does not contain any final novelty claim. Section 7 explicitly states "The project is positioned as a set of candidate contributions, not as final novelty." The "Known limitations" section reinforces this boundary.

## Citation issues or uncertainties

1. KumarRMA2021 is partially verified (arXiv metadata confirmed; RSS 2021 venue needs verification). Cited in the draft as adaptation work; metadata is sufficiently stable for this purpose.
2. Eight P1 matrix entries lack BibTeX entries in `seed_references.bib`. These are recorded in the draft limitations and should be addressed in a future literature-expansion milestone.
3. Sections 4 and 5 each rely primarily on a single citation (FanRSS2021STEP). Broader review is needed.

## Claim audit table

| wording_or_claim | status | citations | evidence | allowed_revision | prohibited_revision |
| --- | --- | --- | --- | --- | --- |
| Sim-to-real and learned locomotion are relevant context for legged deployment mismatch. | allowed_context_claim | TanRSS2018, HwangboSciRobot2019, MaRSS2024DrEureka | verified literature metadata | "These works primarily target..." | "outperforms sim-to-real methods" |
| Adaptation-based locomotion compensates for deployment variation. | allowed_context_claim | KumarRMA2021, MargolisRSS2022 | verified+partially verified | "These adaptation approaches operate at..." | "our method adapts like RMA" |
| Navigation/locomotion coupling supports advisory interpretation of low-level capability. | allowed_context_claim | FuCVPRW2022, FanRSS2021STEP | verified literature metadata | "demonstrating that awareness of low-level walking capability..." | "our risk map improves navigation safety" |
| STEP provides risk-aware traversability framework. | allowed_context_claim | FanRSS2021STEP | verified literature metadata | "provides a comprehensive framework..." | "our labels are CVaR-based" |
| Our labels are not calibrated probabilities. | allowed_context_claim | FanRSS2021STEP | project artifact + literature context | "not calibrated probabilities... conservative metadata flags" | "calibrated uncertainty estimates" |
| Current evaluation is structural, not performance evaluation. | allowed_context_claim | FanRSS2021STEP | M17 project artifact | "structural rather than performance evaluation" | "validates navigation performance" |
| Seed literature does not yet establish equivalent closed-source pipeline. | candidate_gap_wording | TanRSS2018, YangRAL2022, MargolisRSS2022 | verified literature + candidate gap docs | "The current seed literature does not yet establish..." | "no prior work exists" |
| Artifact-governed pipeline is a candidate contribution. | candidate_gap_wording | — (project artifact) | M13-M18 project artifacts | "candidate contributions, not as final novelty" | "final novelty claim" |
| Response-derived risk labels improve navigation safety. | prohibited_overclaim | — | none | — | "improves navigation safety" |
| Pipeline reduces collision rate. | prohibited_overclaim | — | none | — | "reduces collision rate" |
| Method outperforms prior work. | prohibited_overclaim | — | no comparative experiment | — | "outperforms prior work" |
| Closed-source calibration problem is solved. | prohibited_overclaim | — | sparse evidence only | — | "solves closed-source robot calibration" |
| Publication readiness. | prohibited_overclaim | — | insufficient literature + experiments | — | "publication-ready" |
| Final novelty. | prohibited_overclaim | — | insufficient literature | "candidate contribution" | "final novelty claim" |
