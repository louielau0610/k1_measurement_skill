# P13 Reference Cleanup Report

## Purpose

Resolve the 8 matrix-only literature entries needing BibTeX from P11/P12 and strengthen Related Work §4/§5 citation support.

## Inputs inspected

P1 literature matrix, P1 notes (RudinCoRL2021, MargolisCoRL2022, GrandiaTRO2023, FanArxiv2021Costmaps), seed_references.bib, citation verification report, P11/P12 audit documents.

## External search

None. All 8 entries metadata was already verified in P1 literature matrix and P1 notes. No additional search required.

## Matrix-only entries reviewed

| citation_key | prior_status | action_taken | verification_status | source_used | bibtex_updated | manuscript_cited | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RudinCoRL2021 | matrix-only, verified | bibtex_added_verified | verified | P1 notes + OpenReview URL | yes (inproceedings) | no (sim-to-real context) | CoRL 2021; sufficient metadata from P1 |
| MargolisCoRL2022 | matrix-only, verified | bibtex_added_verified | verified | P1 notes + OpenReview URL | yes (inproceedings) | no (adaptation context) | CoRL 2022 Oral; sufficient metadata |
| DaoArxiv2026 | matrix-only, partially_verified | bibtex_added_partially_verified | partially_verified | P1 matrix + arXiv URL | yes (@misc, eprint) | no (2026 preprint) | Preprint; metadata stable |
| GangapurwalaArxiv2020 | matrix-only, partially_verified | bibtex_added_partially_verified | partially_verified | P1 matrix + arXiv URL | yes (@misc, eprint) | no (locomotion context) | Preprint; venue TBD |
| GrandiaTRO2023 | matrix-only, partially_verified | bibtex_added_partially_verified | partially_verified | P1 notes + arXiv URL | yes (article, eprint) | no (navigation-coupled) | IEEE TRO; arXiv confirmed |
| FanArxiv2021Costmaps | matrix-only, partially_verified | bibtex_added_partially_verified | partially_verified | P1 notes + arXiv URL | yes (@misc, eprint) | yes (Related Work §4) | Cited in RW §4; context only |
| BenrabahSensors2024 | matrix-only, verified | bibtex_added_verified | verified | P1 matrix + MDPI URL | yes (article) | yes (Related Work §4, §5) | Sensors 2024; review paper |
| FrancisTOHRI2025 | matrix-only, verified | bibtex_added_verified | verified | P1 matrix + NVIDIA URL | yes (article) | yes (Related Work §5) | ACM TOHRI; metrics guidelines |

## BibTeX entries added

8 entries added to `seed_references.bib`. Total BibTeX count: 8 (original) + 8 (P13) = 16 entries. All fields are from verified P1 metadata only — no fabricated DOI, arXiv, or venue fields.

## Entries deferred

None. All 8 had sufficient verified metadata from P1.

## Entries rejected

None. All 8 are from P1 seed literature and were reviewed/accepted in P1.

## Manuscript citation changes

- Related Work §4: added FanArxiv2021Costmaps and BenrabahSensors2024 (context citations for risk-aware traversability).
- Related Work §5: added BenrabahSensors2024 and FrancisTOHRI2025 (context citations for field evaluation metrics).
- No other section modified. Method, Experiments, Discussion, and Conclusion unchanged.

## Verification risks

- DaoArxiv2026 (2026 preprint): very recent; peer-review status unknown. Cited only in literature matrix, not in manuscript.
- GangapurwalaArxiv2020: arXiv preprint; final venue not confirmed in P1. Not cited in manuscript.
- FanArxiv2021Costmaps: arXiv preprint; peer-reviewed venue unresolved. Cited only as context in Related Work §4.
- GrandiaTRO2023: IEEE TRO journal confirmed in arXiv metadata; P1 marked partially_verified. Not cited in manuscript.

## Remaining citation tasks

- Full DOI/author list verification for all 16 entries (deferred to pre-submission check).
- Related Work §4/§5 could still benefit from 1-2 additional peer-reviewed sources on uncertainty-aware navigation evaluation.
- Literature expansion for commercial SDK calibration papers (deferred — not in P1/P13 scope).
