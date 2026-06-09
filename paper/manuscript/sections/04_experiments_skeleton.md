# Experiments and Evaluation Skeleton

中文优先说明：本文件是 Experiments/Evaluation skeleton，不是最终实验章节。不得把计划实验写成已完成结果。

## Current available evidence

- Structural/software validation:
  - schema exists。
  - dataset exists。
  - response model script produces output。
  - risk mapper script produces output。
  - M17 evaluation report exists。
- Dataset evidence:
  - 5 Measurement v0-derived response records。
  - sparse, single-robot, single-environment evidence。
- Literature/positioning evidence:
  - P1 matrix: 16 seed entries。
  - P2: six clusters and five candidate contributions。

## Current reproducible artifacts

- Dataset build / validation artifacts:
  - `outputs/research_datasets/velocity_response_dataset_v1.json`
  - `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json`
- Model artifacts:
  - `outputs/research_models/response_model_predictions_v1.json`
  - `outputs/research_models/response_model_evaluation_v1.json`
- Risk artifacts:
  - `outputs/research_risk/navigation_risk_map_v1.json`
  - `outputs/research_risk/navigation_risk_evaluation_v1.json`
- Evaluation artifacts:
  - `outputs/research_evaluation/m17_pipeline_evaluation_report.json`

## Dataset summary

- Records count: 5。
- Numeric records count: 4。
- Qualitative-only records count: 1。
- Current source: `outputs/research_evaluation/m17_pipeline_evaluation_report.json`
- Limitation:
  - mostly single trial per speed。
  - limited environment coverage。
  - odometer-primary evidence。

## Response model evaluation currently possible

- Available:
  - script execution and output validation。
  - response predictions count。
  - exact-source reconstruction sanity check。
- Not available:
  - held-out prediction error。
  - generalization error。
  - calibrated uncertainty error。
  - performance superiority over baselines。

## Risk-map evaluation currently possible

- Available:
  - risk assessments count。
  - warning categories count。
  - risk level counts。
  - boundary checks showing no compensation / safe adapter authority。
- Not available:
  - real navigation outcome evaluation。
  - collision rate。
  - near-miss rate。
  - navigation success rate。
  - before/after advisory comparison。

## Metrics currently available

- dataset record count。
- numeric records count。
- qualitative-only count。
- response predictions count。
- risk assessments count。
- warning category counts。
- risk level counts。
- validation pass/fail。

## Metrics not yet available

- collision rate。
- near-miss rate。
- navigation success rate。
- path deviation。
- stop distance。
- response delay。
- calibrated uncertainty。
- multi-environment generalization。
- cross-robot generalization。
- compensation performance。
- safe command adapter performance。

## Claims supported by current evidence

- The repository implements an offline artifact-governed pipeline。
- The current dataset contains sparse Measurement v0-derived K1 response evidence。
- The response model foundation emits conservative labels and predictions。
- The risk mapper emits offline advisory warnings。
- The claim audit separates structural evidence from performance evidence。

## Claims not supported by current evidence

- improved navigation safety。
- reduced collision rate。
- reduced near-miss rate。
- improved navigation success rate。
- calibrated uncertainty。
- performance superiority。
- compensation readiness。
- safe command adapter readiness。
- publication readiness。

## Required future experiments

- repeated trials per command velocity。
- multi-surface trials。
- multi-session trials。
- external ground truth tracking。
- expanded command grid including `v_x` and `w_z`。
- real navigation task protocol。
- baseline comparison protocol。
- claim upgrade audit after experiment completion。

## Future evaluation protocol

- Keep structural validation, dataset evidence, model sanity checks, and risk-map readiness separate。
- Add real navigation outcome evaluation only after an approved protocol exists。
- Store all outcome metrics as artifacts before updating claims。
- Upgrade claims only through `paper/claims/claim_upgrade_plan.md`。

