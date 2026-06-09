# Title and Contribution Options v1

> **Status**: tentative options only. No final title selected. No final contribution structure claimed. All options are for drafting and discussion purposes.

## Candidate titles

| # | title | emphasis | framing_option | risks |
| --- | --- | --- | --- | --- |
| 1 | Deployment-Layer Velocity Response Calibration for Closed-Source Legged Robots | Deployment-layer calibration | Option 1 (deployment-layer calibration) | Novelty risk if broader system-ID literature not reviewed. |
| 2 | Black-Box Command-to-Motion Response Modeling for Legged Robot Deployment | Black-box response modeling | Option 4 (black-box command-response) | High if generalized beyond K1 or sparse data. |
| 3 | Navigation-Aware Reliability Labels from Legged Robot Velocity Response Measurements | Navigation-aware reliability | Option 2 (navigation-aware reliability) | Very high if safety improvement implied before navigation trials. |
| 4 | Claim-Governed Measurement Artifacts for Legged Robot Deployment Research | Artifact governance | Option 3 (artifact-governed pipeline) | May be seen as process/tooling rather than robotics method. |
| 5 | Toward Safer Closed-Source Legged Robot Deployment via Velocity Response Evidence | Deployment safety | Option 5 (closed-source deployment safety) | Highest overclaiming risk; current evidence does not support safety claims. |
| 6 | Velocity Response Characterization for Black-Box Legged Robot Deployment | Characterization emphasis | Option 1 / Option 4 hybrid | Moderate risk; descriptive rather than claim-heavy. |
| 7 | An Artifact-Governed Pipeline for Measuring and Modeling Closed-Source Quadruped Velocity Response | Artifact-governed + measurement emphasis | Option 3 / Option 4 hybrid | Lower overclaiming risk; emphasizes process over outcome. |

## Cautious contribution structures

### Structure A: Pipeline-first (artifact governance emphasis)

**Intended emphasis**: the pipeline itself — its staged design, schema contracts, reproducibility scripts, and claim governance — is the primary contribution.

**Supporting artifacts**:
- M13 schema and M14 dataset (existence and structure).
- M15R model predictions and uncertainty labels.
- M16 risk map and evaluation.
- M17 pipeline evaluation package.
- P1-P3 literature and claim governance documents.

**Literature positioning**: closest to paper framing Option 3. Emphasizes the distinction between structural artifact evidence and missing performance evidence.

**Missing evidence**: artifact-governance literature comparison; reproducibility by independent users; expanded K1 dataset.

**Overclaiming risk**: medium if structural validation is treated as field performance. Mitigated by the strong claim-governance layer.

### Structure B: Calibration-first (response modeling emphasis)

**Intended emphasis**: the measured command-response relationship itself — the dataset, model, and uncertainty labels — as a deployment-layer calibration artifact.

**Supporting artifacts**:
- Measurement v0 field records.
- Velocity response dataset v1.
- M15R hybrid response model.
- Uncertainty/confidence labels with explicit limitations.

**Literature positioning**: closest to paper framing Option 1 or Option 4. Connects to system identification, kinematic calibration, and black-box robotics literature [@TanRSS2018] [@YangRAL2022] [@MargolisRSS2022].

**Missing evidence**: broader black-box system-identification literature review; repeated multi-session K1 trials; prediction accuracy on held-out data; comparison with existing calibration approaches.

**Overclaiming risk**: high if described as a general calibration solution or if novelty is claimed before broader literature review. Mitigated by explicitly documenting that current evidence is sparse and single-robot.

### Structure C: Risk-interpretation-first (navigation advisory emphasis)

**Intended emphasis**: the translation from low-level velocity response mismatch to navigation-relevant advisory risk metadata.

**Supporting artifacts**:
- M16 navigation risk map and evaluation.
- M15R uncertainty labels as risk inputs.
- M17 unavailable metrics documentation.
- P1/P2 risk-aware navigation and field-metrics literature [@FanRSS2021STEP] [@FuCVPRW2022].

**Literature positioning**: closest to paper framing Option 2. Connects risk-aware traversability literature to a new signal source (command-response mismatch rather than terrain perception).

**Missing evidence**: navigation outcome trials; collision/near-miss/success metrics; baseline comparisons; calibration of risk labels against real navigation performance.

**Overclaiming risk**: very high if described as safety improvement, collision reduction, or navigation control. Mitigated only by the strong conservative language in M16/M17 non-claims.

## Recommendation

Structure A (pipeline-first) has the strongest current evidence support and lowest overclaiming risk. Structure B requires more literature before contribution framing is safe. Structure C should be deferred until navigation outcome experiments exist. All options remain tentative and may be revised or combined after P5 (Method draft) and P6 (Experiments draft).
