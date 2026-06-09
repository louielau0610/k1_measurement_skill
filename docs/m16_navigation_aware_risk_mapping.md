# M16 导航感知可靠性与风险映射

M16 的目标是把 M15R response model prediction 转换为离线 navigation-aware reliability / risk assessment。M16 只输出 advisory risk map 和 warning metadata，不控制机器人、不修改命令、不接入实时导航栈，也不实现 safe command adapter。

## 为什么需要风险映射

M15R 回答的是 command velocity 对应的响应预测、定性标签和不确定性标签。导航任务还需要知道这些预测在 planner / human review 层面意味着什么风险。M16 在 prediction 和未来 M17 evaluation 之间加入一个保守的 risk mapping layer。

## Response Prediction 与 Risk Assessment 的区别

- response prediction：描述 `vx_cmd_mps` 对应的 predicted / qualitative velocity response。
- navigation-aware risk assessment：根据 prediction type、qualitative label、uncertainty/confidence label 和 safety boundary，输出 tracking reliability、risk level、warning category 和 downstream-use boundary。

M16 不声称真实导航安全提升，也不声称 collision / near-miss / success-rate 改善。

## 输入与输出

输入：

- `outputs/research_models/response_model_predictions_v1.json`
- 默认使用 `uncertainty_aware_hybrid_v1`

输出：

- `outputs/research_risk/navigation_risk_map_v1.json`
- `outputs/research_risk/navigation_risk_evaluation_v1.json`

## Risk Mapping Rules

- out-of-range 或 unsupported prediction：输出 unsupported/high risk，并要求 warning。
- deadzone / ineffective / no motion：tracking unreliable，risk critical/high，warning category 为 `deadzone_or_no_motion`。
- weak tracking：tracking weak，risk high/medium，warning category 为 `weak_tracking`。
- under-tracking：tracking limited，risk medium/high，warning category 为 `under_tracking`。
- near-stable 但需要 repeat / yaw validation：tracking limited，risk medium，warning category 为 `high_uncertainty`。
- stable reference 且 uncertainty 不高：tracking reliable reference，risk low/medium；仍保留 sparse-data limitation。
- high 或 medium_high uncertainty：risk 不低于 medium。
- low 或 unknown confidence：risk 不低于 medium，并记录原因。

## 标签集合

Tracking reliability labels：

- `reliable_reference`
- `limited`
- `weak`
- `unreliable`
- `unsupported`

Navigation risk levels：

- `low`
- `medium`
- `high`
- `critical`
- `unsupported`

Warning categories：

- `none`
- `deadzone_or_no_motion`
- `weak_tracking`
- `under_tracking`
- `high_uncertainty`
- `out_of_range`
- `qualitative_only`
- `mixed_evidence`
- `unsupported_prediction`
- `safety_boundary`

## Downstream Use Boundary

Allowed downstream uses:

- `offline_analysis`
- `research_evaluation`
- `planner_warning_advisory`
- `human_review`

Disallowed downstream uses:

- `automatic_compensation`
- `inverse_command_mapping`
- `real_time_navigation_control`
- `safe_command_adapter_execution`
- `robot_motion_commanding`

## 为什么 M16 仍然是离线 / advisory

当前数据来自 sparse single-robot dataset，uncertainty/confidence 仍是 labels，不是 calibrated probabilities。缺少真实导航任务结果、collision / near-miss / success-rate 指标，也缺少 yaw/lateral/delay/stop-distance 的完整响应维度。因此 M16 只能作为 offline advisory risk map。

## 为什么不实现补偿、导航控制或 safe command adapter

M16 只把 response model output 转成 risk labels。它不输出 corrected command，不做 inverse command mapping，不控制 planner，也不执行 robot motion command。`compensation_ready=false` 与 `safe_command_adapter_ready=false` 必须保持。

## M17 如何评估

M17 可以评估 warning distribution、command-region risk classification 和 paper-style report structure。真实 navigation outcome metrics 只能在后续设计好的导航实验中记录，不能由 M16 artifact 伪造。

## Limitations

- no real navigation outcomes yet；
- no collision / near-miss / success-rate metrics yet；
- sparse single-robot dataset；
- uncertainty labels are not calibrated probabilities；
- missing yaw/lateral/delay/stop-distance metrics。
