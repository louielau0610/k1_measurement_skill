# Manuscript Scaffold

中文优先说明：本文件是 manuscript scaffold，不是完整论文草稿。所有章节只允许 bullet-point planning。

## Candidate title options

- Deployment-Layer Velocity Response Calibration for Closed-Source Legged Robots
- Black-Box Command-to-Motion Response Modeling for Legged Robot Deployment
- Claim-Governed Measurement Artifacts for Legged Robot Deployment Research
- Navigation-Aware Reliability Labels from Legged Robot Velocity Response Measurements

## Abstract placeholder

- Planned only:
  - problem context。
  - black-box K1 deployment constraint。
  - measurement-to-dataset-to-model-to-risk pipeline。
  - structural evidence available。
  - limitations and future experiments。
- Do not write final abstract prose here。

## 1. Introduction - planned content only

- Motivation: command-response mismatch in closed-source legged robot deployment。
- Problem boundary: measurement and advisory interpretation only。
- Candidate contributions: use P2/M18 candidate language only。
- Required caveat: no navigation safety improvement claim yet。

## 2. Related Work - planned content only

- P1/P2 clusters:
  - sim-to-real and learned locomotion。
  - rapid adaptation。
  - navigation-coupled locomotion。
  - risk-aware navigation。
  - field metrics。
  - black-box calibration。
- Do not write full related-work prose until P3。

## 3. Method - planned content only

- Use `paper/manuscript/sections/03_method_skeleton.md`。
- Cover:
  - system boundary。
  - notation。
  - five-stage pipeline。
  - algorithmic contracts。
  - non-goals。

## 4. Experiments - planned content only

- Use `paper/manuscript/sections/04_experiments_skeleton.md`。
- Separate:
  - structural validation。
  - dataset summary。
  - model sanity checks。
  - risk-map readiness。
  - missing real navigation outcomes。

## 5. Discussion - planned content only

- Discuss what artifact governance enables。
- Discuss sparse evidence limits。
- Discuss why candidate contributions remain tentative。
- Do not claim final novelty。

## 6. Limitations - planned content only

- sparse dataset。
- single robot。
- single environment/session。
- odometer-primary evidence。
- no calibrated uncertainty。
- no navigation outcome metrics。
- no compensation or safe adapter。

## 7. Conclusion - planned content only

- Summarize structural pipeline only。
- State future evidence requirements。
- Do not write final conclusion prose。

## Figures planned

- Method pipeline figure。
- Evidence chain / claim-governance figure。
- Future possible dataset/model/risk flow figure after figure-generation milestone。

## Tables planned

- Method artifact evidence table。
- Current metrics and missing evidence table。
- Claim audit table。
- Literature positioning table。

## Claims allowed now

- Offline artifact-governed pipeline exists。
- Dataset/model/risk-map artifacts exist。
- Current evidence supports structural/software validation。
- Candidate contributions are documented but tentative。

## Claims not allowed now

- final novelty。
- performance superiority。
- navigation safety improvement。
- collision reduction。
- near-miss reduction。
- success-rate improvement。
- compensation readiness。
- safe command adapter readiness。
- publication readiness。

