# Paper Framing Options v1

中文优先说明：以下是 paper framing options，不是最终题目，不是投稿承诺，不是 publication readiness claim。

## Option 1: Deployment-layer calibration framing

- Title candidate: Deployment-Layer Velocity Response Calibration for Closed-Source Legged Robots
- Central problem: Closed-source legged robots may expose velocity commands without exposing controller internals.
- Method emphasis: external measurement, dataset schema, response model, claim-governed reporting.
- Likely contribution structure: black-box response pipeline; sparse evidence labels; evaluation governance.
- Required experiments: repeated K1 trials, multi-surface tests, held-out prediction evaluation.
- Risks: high novelty risk unless more black-box calibration literature is reviewed.
- Best target venue category: workshop or conference short paper.
- Current feasibility: plausible but not ready.

## Option 2: Navigation-aware reliability framing

- Title candidate: Navigation-Aware Reliability Labels from Legged Robot Velocity Response Measurements
- Central problem: navigation systems may need low-level execution reliability signals.
- Method emphasis: response mismatch to warning metadata and risk categories.
- Likely contribution structure: response model; advisory risk mapping; claim boundary between warning and control.
- Required experiments: navigation trials, collision/near-miss/success metrics, baseline comparisons.
- Risks: very high if safety improvement is implied before trials.
- Best target venue category: not ready; future conference full paper only after experiments.
- Current feasibility: conceptually useful, experimentally immature.

## Option 3: Artifact-governed research pipeline framing

- Title candidate: Claim-Governed Measurement Artifacts for Legged Robot Deployment Research
- Central problem: early robot deployment research can overstate sparse evidence.
- Method emphasis: schema, validation, model outputs, non-claims, literature verification, claim-upgrade plan.
- Likely contribution structure: artifact governance; reproducible reports; conservative paper pipeline.
- Required experiments: fewer than Option 2, but needs artifact-governance literature and user-facing evaluation.
- Risks: may be seen as process/tooling rather than robotics method.
- Best target venue category: workshop.
- Current feasibility: strongest short-term option.

## Option 4: Black-box command-response modeling framing

- Title candidate: Black-Box Command-to-Motion Response Modeling for Legged Robot Deployment
- Central problem: commanded velocity may not match executed motion, especially at deployment limits.
- Method emphasis: measured response curve, uncertainty labels, sparse-data model foundation.
- Likely contribution structure: dataset schema; response model; limitations and future experiments.
- Required experiments: larger command grid, repeated trials, external ground truth, comparison to baseline models.
- Risks: high if generalized beyond K1 or sparse data.
- Best target venue category: workshop or conference short paper after expanded data.
- Current feasibility: plausible after M18 plus experiments.

## Option 5: Closed-source legged robot deployment safety framing

- Title candidate: Toward Safer Closed-Source Legged Robot Deployment via Velocity Response Evidence
- Central problem: closed-source deployment can hide low-level behavior relevant to safety.
- Method emphasis: advisory warnings and risk interpretation.
- Likely contribution structure: measurement pipeline; warning layer; future safety evaluation.
- Required experiments: real navigation outcomes, hazard annotations, repeatable safety protocol.
- Risks: highest overclaiming risk; current evidence does not support safety claims.
- Best target venue category: not ready.
- Current feasibility: defer until substantial experiments exist.

