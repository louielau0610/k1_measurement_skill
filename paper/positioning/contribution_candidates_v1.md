# Contribution Candidates v1

中文优先说明：以下都是 candidate contributions，不是 final contributions，不是 novelty claims，也不是 performance claims。

## Candidate Contribution 1: Artifact-governed black-box command-to-motion response pipeline

- Candidate statement: A conservative artifact-governed pipeline for recording, validating, modeling, and reporting black-box command-to-motion response evidence.
- Related prior-work clusters: Cluster 1; Cluster 6.
- Supporting project artifacts: M13 schema, M14 dataset, M15R model outputs, M17 pipeline evaluation, claim registry.
- Supporting literature evidence: `TanRSS2018`, `YangRAL2022`, `MargolisRSS2022`, `DaoArxiv2026`.
- Missing evidence: broader black-box system identification search, repeated trials, and comparison with existing calibration pipelines.
- Overclaiming risk: high if described as novel, solved, or general.
- Current status: `candidate_contribution`; `requires_more_literature`; `requires_more_experiment`.

## Candidate Contribution 2: Measurement-to-dataset-to-model pipeline for closed-source legged robot velocity response

- Candidate statement: A reproducible measurement-to-dataset-to-response-model workflow for sparse real K1 velocity response evidence under closed-source deployment constraints.
- Related prior-work clusters: Cluster 1; Cluster 2; Cluster 6.
- Supporting project artifacts: `configs/velocity_response_dataset_schema_v1.json`, `outputs/research_datasets/velocity_response_dataset_v1.json`, `outputs/research_models/response_model_predictions_v1.json`.
- Supporting literature evidence: `TanRSS2018`, `HwangboSciRobot2019`, `MargolisRSS2022`, `YangRAL2022`.
- Missing evidence: more sessions, more surfaces, more command dimensions, and external ground truth.
- Overclaiming risk: medium-high if claimed as calibration-grade or compensation-ready.
- Current status: `candidate_contribution`; `requires_more_experiment`.

## Candidate Contribution 3: Uncertainty/reliability-labeled response modeling under sparse real robot evidence

- Candidate statement: A conservative response modeling foundation that labels uncertainty and confidence without pretending sparse evidence is calibrated probability.
- Related prior-work clusters: Cluster 2; Cluster 4; Cluster 5.
- Supporting project artifacts: M15R predictions/evaluation and M17 limitation list.
- Supporting literature evidence: `FanRSS2021STEP`, `FanArxiv2021Costmaps`, `BenrabahSensors2024`, `FrancisTOHRI2025`.
- Missing evidence: uncertainty calibration, repeated measurements, and prediction error evaluation on held-out trials.
- Overclaiming risk: high if labels are called calibrated uncertainty.
- Current status: `candidate_contribution`; `requires_more_experiment`.

## Candidate Contribution 4: Navigation-aware risk interpretation of low-level velocity-response mismatch

- Candidate statement: An offline advisory interpretation layer that maps velocity-response uncertainty and mismatch into navigation-relevant warning metadata.
- Related prior-work clusters: Cluster 3; Cluster 4; Cluster 5.
- Supporting project artifacts: M16 navigation risk map, M16 evaluation, M17 report.
- Supporting literature evidence: `FuCVPRW2022`, `FanRSS2021STEP`, `FanArxiv2021Costmaps`, `GrandiaTRO2023`.
- Missing evidence: navigation task trials, collision/near-miss/success metrics, and baseline comparisons.
- Overclaiming risk: very high if stated as safety improvement or navigation control.
- Current status: `requires_more_experiment`; `candidate_contribution`.

## Candidate Contribution 5: Claim-governed evaluation package separating structural evidence from performance evidence

- Candidate statement: A research-governance package that explicitly separates structural pipeline artifacts, literature context, candidate gaps, prohibited claims, and missing performance evidence.
- Related prior-work clusters: Cluster 5; Cluster 6.
- Supporting project artifacts: M17 evaluation report, P1 verification report, P2 claim upgrade plan, claim registry, evidence table, non-claims.
- Supporting literature evidence: `BenrabahSensors2024`, `FrancisTOHRI2025`, `FanRSS2021STEP`.
- Missing evidence: reproducibility/artifact-governance literature comparison and future experimental validation.
- Overclaiming risk: medium if framed as a field-performance contribution.
- Current status: `candidate_contribution`; `requires_more_literature`.

