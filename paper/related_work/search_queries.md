# P1 Seed Literature Search Queries

中文优先说明：P1 的目标是建立第一版可核查 seed literature matrix，而不是写完整 related work，也不是宣布 novelty。检索日期：2026-06-09。检索环境可用；主要使用 web search、官方会议/期刊页面、OpenReview、arXiv、机构 repository 和出版商页面。

## Research Objective

为 “Navigation-Aware Velocity Response Calibration for Closed-Source Legged Robots” 建立初始文献地图，关注 command-to-motion response mismatch、black-box / deployment-layer calibration、sim-to-real mismatch、navigation-locomotion coupling、uncertainty-aware risk mapping 和 field robotics evaluation metrics。

## Search Buckets

- Bucket A: Legged robot velocity tracking and command-following mismatch.
- Bucket B: Black-box robot calibration and system identification.
- Bucket C: Sim-to-real and locomotion calibration.
- Bucket D: Navigation and locomotion coupling.
- Bucket E: Uncertainty-aware robotics and safety/risk mapping.
- Bucket F: Field robotics evaluation metrics.

## Exact Queries Used

- `"legged robot velocity tracking error command velocity actual velocity"`
- `"quadruped robot command tracking mismatch"`
- `"black-box system identification robot command response"`
- `"legged locomotion sim-to-real actuator model latency"`
- `"navigation locomotion coupling legged robot planner controller mismatch"`
- `"uncertainty-aware robot navigation risk assessment"`
- `"field robotics navigation evaluation collision near miss success rate"`
- `site:roboticsproceedings.org legged locomotion sim-to-real velocity tracking quadruped`
- `site:arxiv.org legged locomotion sim-to-real actuator model latency quadruped`
- `site:ieeexplore.ieee.org uncertainty aware robot navigation risk assessment`
- `Rapid Motor Adaptation for Legged Robots RSS 2021 authors DOI`
- `Learning agile and dynamic motor skills for legged robots Science Robotics 2019 DOI Hwangbo`
- `Walk These Ways Tuning Robot Control for Generalization with Multiplicity of Behavior CoRL 2022`
- `Coupling Vision and Proprioception for Navigation of Legged Robots CoRL 2022`
- `Learning Risk-aware Costmaps for Traversability in Challenging Environments authors`
- `A Review on Traversability Risk Assessments for Autonomous Ground Vehicles Methods and Metrics DOI`
- `robot navigation evaluation metrics success rate collision rate near miss paper`

## Sources Searched

- Robotics: Science and Systems official proceedings.
- OpenReview.
- CVF Open Access.
- arXiv.
- CMU Robotics Institute publication pages.
- CaltechAUTHORS.
- MDPI / Sensors.
- NVIDIA Research publication page.
- Science Robotics metadata through DOI/Crossref-indexed source.
- Oxford / ETH repository snippets when official venue metadata needed follow-up.

## Inclusion Criteria

- Robotics or robot-navigation relevance.
- Metadata available from an official or reputable academic source.
- Clear relationship to one or more P1 buckets.
- Abstract or metadata inspected.
- Entry can be summarized without inventing results.

## Exclusion Criteria

- SEO summaries or generated paper pages without source metadata.
- Reddit/social posts.
- ResearchGate-only entries when no official/arXiv/venue page was available.
- Papers too far from robotics deployment, locomotion, risk, or evaluation.
- Sources where title, authors, year, or venue could not be verified.

## Citation Verification Rules

- Do not fabricate titles, authors, venues, DOI, arXiv IDs, URLs, or results.
- Mark arXiv-only or venue-uncertain items as `partially_verified`.
- Include BibTeX only when metadata is sufficiently verified.
- Do not claim full-text reading unless the full text was inspected.
- Treat novelty and performance superiority as unsupported until P2/P3 evidence exists.

## Unresolved Search Gaps

- More direct literature on closed-source commercial quadruped SDK command-response calibration is still needed.
- More direct prior work on externally measured commanded-velocity vs executed-velocity curves for legged robots is still needed.
- More formal literature on propagating low-level velocity-response uncertainty into high-level navigation advisory layers should be searched in P2.
- Final venue metadata for several arXiv seeds should be verified before manuscript citation.

