# Method Skeleton

中文优先说明：本文件是 Method section skeleton，不是最终论文正文。所有条目都应在后续 M19/P3/P4 中继续核查和扩展。

## Method objective

- 构建一个 offline、artifact-governed 的 velocity response research pipeline。
- 研究对象：closed-source K1 deployment layer 中 `v_x^cmd` 与 `v_x^actual` 的响应关系。
- 当前目标：生成可复查的 dataset、response prediction、risk assessment 和 claim evidence artifacts。
- 当前不目标：不实现补偿、不控制导航、不发布机器人命令。

## System boundary

- 输入边界：
  - Measurement v0 artifacts。
  - `configs/velocity_response_dataset_schema_v1.json`
  - environment / robot state metadata where available。
- 输出边界：
  - `outputs/research_datasets/velocity_response_dataset_v1.json`
  - `outputs/research_models/response_model_predictions_v1.json`
  - `outputs/research_risk/navigation_risk_map_v1.json`
  - `outputs/research_evaluation/m17_pipeline_evaluation_report.json`
- Safety boundary:
  - no compensation。
  - no inverse command mapping。
  - no navigation control。
  - no safe command adapter。

## Problem formulation

- Command/condition input:
  - `x = [v_x^cmd, environment, robot_state_optional]`
- Response/risk output:
  - `y = [v_x^actual, response_label, uncertainty_label, risk_level]`
- Response model contract:
  - `f_theta: x -> response prediction`
- Navigation advisory mapping contract:
  - `g: response prediction -> navigation risk assessment`
- Current evidence:
  - sparse single-robot Measurement v0-derived dataset。
  - uncertainty/confidence labels, not calibrated probabilities。

## Overview of proposed pipeline

- Measurement evidence is normalized into a schema-governed response dataset。
- Dataset records are validated before modeling。
- Response model generates prediction contracts and conservative labels。
- Risk mapper converts predictions into offline advisory risk assessments。
- Claim-governed evaluation separates structural evidence from unsupported performance claims。

## Stage 1: Measurement artifact construction

- Implemented artifact:
  - Measurement v0 artifacts under `outputs/real_k1_field_tests/`。
- Mapping document:
  - `docs/measurement_v0_to_velocity_response_schema_v1_mapping.md`
- Current limitations:
  - single robot。
  - single session。
  - odometer-primary evidence。
  - external ground truth not yet available。

## Stage 2: Velocity response dataset construction

- Schema:
  - `configs/velocity_response_dataset_schema_v1.json`
- Dataset:
  - `outputs/research_datasets/velocity_response_dataset_v1.json`
- Validation report:
  - `outputs/research_datasets/velocity_response_dataset_v1_validation_report.json`
- Current dataset summary:
  - 5 records。
  - 4 numeric records。
  - 1 qualitative-only record。
- Boundary:
  - missing response dimensions remain explicit limitations, not fabricated values。

## Stage 3: Uncertainty-aware response modeling

- Producer:
  - `scripts/run_velocity_response_model_v1.py`
- Outputs:
  - `outputs/research_models/response_model_predictions_v1.json`
  - `outputs/research_models/response_model_evaluation_v1.json`
- Model contract:
  - sparse response prediction。
  - uncertainty/confidence labels。
  - minimal baseline hooks for future comparison。
- Boundary:
  - no calibrated uncertainty claim。
  - no performance superiority claim。
  - no compensation readiness claim。

## Stage 4: Navigation-aware reliability / risk mapping

- Producer:
  - `scripts/run_navigation_risk_mapping_v1.py`
- Outputs:
  - `outputs/research_risk/navigation_risk_map_v1.json`
  - `outputs/research_risk/navigation_risk_evaluation_v1.json`
- Contract:
  - `g(response prediction) -> advisory risk assessment`
  - risk level and warning metadata only。
- Boundary:
  - no navigation controller。
  - no real navigation outcome evaluation。
  - no collision / near-miss / success-rate claim。

## Stage 5: Claim-governed evaluation

- Evaluation report:
  - `outputs/research_evaluation/m17_pipeline_evaluation_report.json`
- Claim files:
  - `paper/claims/claim_registry.md`
  - `paper/claims/evidence_table.md`
  - `paper/claims/non_claims.md`
  - `paper/claims/claim_upgrade_plan.md`
  - `paper/claims/m18_claim_audit.md`
- Purpose:
  - classify structural claims, literature context claims, candidate contributions, future experiments, and prohibited claims。

## Inputs and outputs

| Stage | Inputs | Outputs |
| --- | --- | --- |
| Measurement | Real K1 Measurement v0 artifacts | measurement profile and mapping inputs |
| Dataset | Measurement v0 mapping; schema v1 | dataset v1; validation report |
| Model | dataset v1; schema v1 | response predictions; model evaluation |
| Risk | response predictions | navigation risk map; risk evaluation |
| Governance | M13-M17 artifacts; P1-P2 positioning | claim audit; manuscript scaffold |

## Algorithmic contracts

- Dataset construction:
  - Measurement fields must be mapped only when available。
  - unavailable fields remain missing/optional。
- Response modeling:
  - predictions must preserve source limitations。
  - labels must not be treated as calibrated probabilities。
- Risk mapping:
  - warnings are advisory metadata。
  - risk output must not authorize command execution。
- Claim audit:
  - project evidence and literature evidence remain separate。

## What this method does not do

- Does not implement velocity compensation。
- Does not implement inverse command mapping。
- Does not implement navigation control。
- Does not implement safe command adapter logic。
- Does not run robot commands。
- Does not claim improved navigation safety。
- Does not claim final novelty。
- Does not claim publication readiness。

## Current evidence and limitations

- Current evidence supports structural/software artifact existence and reproducibility。
- Current evidence does not support:
  - navigation safety improvement。
  - collision reduction。
  - near-miss reduction。
  - success-rate improvement。
  - calibrated uncertainty。
  - generalization across robots/surfaces/sessions。

## Future expansion points

- repeated velocity-response trials。
- multi-surface and multi-session datasets。
- `v_x` plus `w_z` command grid。
- external ground truth。
- response delay / stop-distance / yaw drift dimensions。
- navigation task trials with outcome labels。
- baseline comparisons and claim-upgrade review。

