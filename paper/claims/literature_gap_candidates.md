# Literature Gap Candidates

中文优先说明：P1 只提出 candidate gaps，用于 P2 继续核查。以下内容不是 novelty claim，不可直接写成 “our work is the first / outperforms / solves”。

## Candidate gap 1: closed-source / black-box deployment-layer command-to-motion calibration

- Supporting prior work: TanRSS2018, YangRAL2022, DaoArxiv2026, MargolisRSS2022.
- Why the gap may exist: prior work often assumes simulator/control-stack access, internal policy training, or model/state-estimator access, while our K1 context is an external SDK / closed-source deployment layer.
- Evidence still needed: broader system-identification search, commercial quadruped SDK calibration search, and comparison against controller-access methods.
- Risk of overclaiming: high; black-box calibration is a broad field and may exist under other terminology.
- Current claim status: `candidate_gap_only`; `requires_more_literature`; `requires_experiment`; `not_yet_a_claim`.

## Candidate gap 2: navigation-aware interpretation of low-level velocity response mismatch

- Supporting prior work: FuCVPRW2022, GrandiaTRO2023, FanRSS2021STEP, GangapurwalaArxiv2020.
- Why the gap may exist: related work couples navigation and locomotion capability, but P1 found fewer sources that start from externally measured command-to-motion response curves and translate them into navigation advisory artifacts.
- Evidence still needed: search planner-controller mismatch literature and full-text review of navigation safety advisor papers.
- Risk of overclaiming: medium; navigation costmaps and traversability systems already encode robot capability in several ways.
- Current claim status: `candidate_gap_only`; `requires_more_literature`; `requires_experiment`; `not_yet_a_claim`.

## Candidate gap 3: uncertainty/reliability labels as bridge between response modeling and planner advisory

- Supporting prior work: FanRSS2021STEP, FanArxiv2021Costmaps, BenrabahSensors2024, FrancisTOHRI2025.
- Why the gap may exist: uncertainty-aware navigation often addresses map/traversability uncertainty, while our project labels uncertainty in low-level command response before navigation evaluation exists.
- Evidence still needed: formal uncertainty propagation literature, calibration of confidence labels, and navigation trials with outcomes.
- Risk of overclaiming: high; current project labels are not calibrated probabilities.
- Current claim status: `candidate_gap_only`; `requires_more_literature`; `requires_experiment`; `not_yet_a_claim`.

## Candidate gap 4: artifact-governed pipeline from measurement to risk map

- Supporting prior work: TanRSS2018, FanRSS2021STEP, FrancisTOHRI2025, BenrabahSensors2024.
- Why the gap may exist: P1 found many method papers but fewer artifact-governance examples that enforce claim boundaries from measurement through model and risk-report outputs.
- Evidence still needed: reproducibility / artifact-evaluation literature and stronger comparison against benchmarking/reporting protocols.
- Risk of overclaiming: medium; artifact governance is common in software and robotics benchmarking, so final novelty must be carefully scoped.
- Current claim status: `candidate_gap_only`; `requires_more_literature`; `requires_experiment`; `not_yet_a_claim`.

