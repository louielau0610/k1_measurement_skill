# P1 Seed Literature Search Report

中文优先说明：P1 完成了第一轮 seed literature search 和 literature matrix v1。该报告只支持后续 gap analysis 和 manuscript planning，不构成完整 related-work section，不声称 novelty，不声称 publication readiness。

## Search Summary

- Search date: 2026-06-09
- External search available: yes
- Repo-scoped autoresearch skill used: yes
- Candidate sources inspected: 26
- Seed matrix entries added: 16
- Detailed notes created: 11
- Rejected / deferred sources logged: 8

## Bucket Coverage

- Bucket A: covered by HwangboSciRobot2019, KumarRMA2021, RudinCoRL2021, MargolisRSS2022, MargolisCoRL2022, GangapurwalaArxiv2020.
- Bucket B: covered by TanRSS2018, YangRAL2022, DaoArxiv2026.
- Bucket C: covered by TanRSS2018, HwangboSciRobot2019, KumarRMA2021, RudinCoRL2021, MargolisRSS2022, MargolisCoRL2022, MaRSS2024DrEureka.
- Bucket D: covered by FuCVPRW2022, FanRSS2021STEP, GrandiaTRO2023, GangapurwalaArxiv2020.
- Bucket E: covered by FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024.
- Bucket F: covered by FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025, GangapurwalaArxiv2020.

## Strongly Relevant Papers

- TanRSS2018: actuator modeling, latency, and system identification for sim-to-real quadruped locomotion.
- MargolisRSS2022: velocity-command curriculum and online system identification in high-speed quadruped locomotion.
- YangRAL2022: calibration from velocity prediction error in legged robots.
- FuCVPRW2022: planner should be aware of low-level locomotion capability.
- FanRSS2021STEP: uncertainty-aware traversability and CVaR risk-aware planning.
- FanArxiv2021Costmaps: risk-aware costmaps and tail-risk interpretation.

## Partially Relevant Papers

- HwangboSciRobot2019: important sim-to-real legged locomotion context, but not command-response calibration.
- RudinCoRL2021: important sim-to-real training context, but not response mismatch modeling.
- MargolisCoRL2022: deployment-time tuning context, but not closed-source black-box measurement.
- GrandiaTRO2023: perception-planning-control integration, but assumes access to control stack.
- FrancisTOHRI2025: evaluation metric guidance, but social-navigation scope differs.
- BenrabahSensors2024: risk metric taxonomy, but not legged velocity-response-specific.

## Weak or Rejected Papers

Rejected or deferred items are recorded in `paper/related_work/rejected_sources.md`. Most were rejected because they were SEO summaries, social posts, ResearchGate-only sources, too broad, or not sufficiently connected to robotics deployment evidence.

## Search Limitations

- P1 inspected abstracts and metadata, not full papers.
- Some arXiv records require venue verification before final manuscript citation.
- Search coverage is still seed-level and likely misses older system-identification and controller-calibration literature.
- P1 did not search paywalled IEEE metadata deeply beyond accessible snippets/pages.
- P1 did not perform citation chasing from full reference lists.

## Recommended Next Search Directions

- Search ICRA/IROS/RA-L/TRO for black-box system identification and deployment-layer calibration.
- Search legged robot command tracking and velocity tracking metrics directly from full-text PDFs.
- Search navigation-planner/controller mismatch in mobile robotics beyond legged robots.
- Search risk-aware planning literature using CVaR, chance constraints, and uncertainty propagation.
- Verify final venues and DOI metadata for all partially verified arXiv entries.

## What This Means for Project Positioning

P1 supports a cautious positioning: prior work strongly establishes sim-to-real mismatch, actuator/latency modeling, online adaptation, planner-locomotion coupling, and uncertainty-aware traversability/risk mapping as relevant topics. A plausible gap remains around artifact-governed, closed-source, deployment-layer command-to-motion response measurement for navigation advisory use, but this remains a candidate gap only. P1 does not establish novelty, performance superiority, compensation readiness, navigation safety improvement, or publication readiness.

