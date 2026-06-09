# P13 Literature Expansion Report

## Expansion objective

Strengthen Related Work §4 (risk- and uncertainty-aware navigation) and §5 (field robotics metrics and evaluation) citation support. This was P11 issue R-03, deferred from P12.

## New sources added

No new sources beyond the 8 matrix-only entries already in the P1 literature matrix. All citations added are from existing P1 seed literature.

## Why each source was needed

- **FanArxiv2021Costmaps** (Related Work §4): extends the risk-aware traversability context beyond STEP. Fan et al. learn costmap distributions for challenging environments, directly relevant to uncertainty-aware navigation evaluation.
- **BenrabahSensors2024** (Related Work §4, §5): recent review paper providing a taxonomy of traversability risk assessment methods and metrics. Strengthens both the risk-awareness (§4) and field-metrics (§5) discussion.
- **FrancisTOHRI2025** (Related Work §5): provides evaluation principles, scenarios, and metrics frameworks for robot navigation. Nvidia research publication with concrete metric definitions.

## Related Work §4/§5 citation support before P13

- §4 (Risk-aware navigation): 1 citation (FanRSS2021STEP).
- §5 (Field metrics): 1 citation (FanRSS2021STEP).

## Related Work §4/§5 citation support after P13

- §4 (Risk-aware navigation): 4 citations (FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024, plus prior FuCVPRW2022 reference).
- §5 (Field metrics): 3 citations (FanRSS2021STEP, BenrabahSensors2024, FrancisTOHRI2025).

## New or improved literature clusters

- Risk-aware cluster (§4): now includes learning-based costmaps and review/taxonomy sources, not just the STEP framework.
- Field metrics cluster (§5): now includes a review paper with metric taxonomy and a dedicated evaluation guidelines paper.

## Remaining literature gaps

- **Commercial SDK calibration**: P1 did not surface papers specifically on calibration workflows for commercial closed-source robot SDKs. This remains a gap for any final novelty claim.
- **Broader system identification**: additional black-box system-ID literature review would strengthen the gap analysis before submission.
- **Uncertainty calibration**: no papers on calibrating categorical robot reliability labels against empirical data were reviewed.

## Why P13 does not establish final novelty

All citations are context citations — they position the candidate gap, not prove it. The Related Work draft still uses "does not yet establish" and "motivates further literature review." No claim of novelty, first-ness, or performance superiority was added or strengthened.
