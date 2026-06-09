# M20 Metric Definitions v1

All metrics are defined below. No values are reported — this is a definition document for future experiment execution.

## Velocity response metrics

| metric | definition | required_raw_fields | computation_rule | unit | aggregation | claim_supported | claim_not_supported |
| --- | --- | --- | --- | --- | --- | --- | --- |
| commanded velocity | The velocity target sent to the robot | vx_cmd from command topic | direct log extraction | m/s | per-trial | structural pipeline | — |
| measured actual velocity | The odometry-derived actual velocity | vx_actual from odometry topic | direct log extraction or integration | m/s | per-trial | structural pipeline | — |
| tracking error | Difference between commanded and actual velocity | vx_cmd, vx_actual | vx_actual - vx_cmd | m/s | per-trial, mean | predictive quality (held-out) | safety improvement |
| signed tracking error | Same as tracking error, preserving sign | vx_cmd, vx_actual | vx_actual - vx_cmd | m/s | per-trial, mean | bias detection | safety |
| absolute tracking error | Absolute difference | vx_cmd, vx_actual | |vx_actual - vx_cmd| | m/s | per-trial, MAE | magnitude accuracy | safety |
| response ratio | Ratio of actual to commanded velocity | vx_cmd, vx_actual | vx_actual / vx_cmd | dimensionless | per-trial, mean | gain characterization | safety |
| response delay | Time between command issue and detectable velocity response | timestamps from command and odometry | t_response - t_command | s | per-trial | latency modeling | safety |
| stop distance | Distance traveled after stop command until velocity < threshold | position from odometry | position_stop - position_cmd | m | per-trial | stop behavior characterization | safety |
| lateral drift | Lateral displacement per unit time during forward command | vy_actual from odometry or position | deltay / deltat | m/s | per-trial | lateral response | navigation safety |
| yaw drift | Angular displacement per unit time during forward command | omega_actual from odometry | delta_theta / deltat | deg/s | per-trial | yaw response | navigation safety |
| trial validity | Whether trial meets logging and execution criteria | trial metadata | boolean check | — | per-trial | data quality | — |
| qualitative response label | Categorical assessment of response quality | vx_cmd, tracking assessment | qualitative assignment | category | per-command | response characterization | calibrated uncertainty |
| uncertainty/reliability label | Categorical uncertainty flag | qualitative label, numeric error | conservative assignment | category (low/medium/high/extreme) | per-prediction | uncertainty labeling | calibrated probability |

## Model evaluation metrics

| metric | definition | required_raw_fields | computation_rule | unit | claim_supported | claim_not_supported |
| --- | --- | --- | --- | --- | --- | --- |
| held-out MAE | Mean absolute error on held-out command set | vx_cmd, vx_actual, held-out flag | mean(|predicted - actual|) on held-out only | m/s | predictive quality | calibration, safety |
| held-out RMSE | Root mean squared error on held-out set | vx_cmd, vx_actual, held-out flag | sqrt(mean((predicted - actual)^2)) on held-out | m/s | predictive quality | calibration, safety |
| qualitative label agreement | Fraction of held-out commands where predicted and actual qualitative labels match | predicted_label, actual_label | agreement / total, held-out only | fraction | model consistency | accuracy, safety |
| unsupported-query rate | Fraction of held-out commands where model returns extreme uncertainty | uncertainty_label from prediction | extreme / total, held-out only | fraction | model coverage | accuracy |
| uncertainty-stratified error | Held-out error grouped by uncertainty label | uncertainty_label, held-out error | groupby uncertainty | m/s per label | uncertainty label usefulness | calibration |

## Navigation outcome metrics

| metric | definition | required_raw_fields | computation_rule | unit | claim_supported | claim_not_supported |
| --- | --- | --- | --- | --- | --- | --- |
| task success | Binary: task completed within constraints | task_end_state, time, constraints | boolean per trial | — | task performance | safety improvement |
| task failure category | Reason for failure | failure annotation | category per trial | category | failure analysis | safety |
| collision count | Number of robot-environment/obstacle contacts | collision log, video annotation | count per trial or session | count | safety evaluation (descriptive) | safety improvement (unless reduced) |
| near-miss count | Number of close-proximity events without contact | proximity log, annotation | count per trial or session | count | safety evaluation (descriptive) | safety improvement (unless reduced) |
| minimum obstacle distance | Minimum distance between robot and nearest obstacle | proximity sensor or annotated position | min(distance) per trial | m | safety evaluation | safety improvement |
| path deviation | RMS deviation between commanded and actual trajectory | commanded_path, actual_path | RMS(distance) per trial | m | path tracking | safety |
| completion time | Time from task start to completion or failure | task start/end timestamps | t_end - t_start | s | task performance | safety |
| intervention count | Number of manual interventions per trial | intervention log | count per trial | count | operator burden | safety |
| stop/abort count | Number of emergency stops or aborts per trial | stop/abort log | count per trial or session | count | safety evaluation | safety improvement |
| risk-warning exposure | Number of velocity commands in trial with active risk warnings | risk_map query per command | count per trial | count | advisory exposure | safety |
| warning-to-outcome association | Statistical association between risk warning level and outcome metrics | risk_level, outcome metrics | correlation/association test | p-value or effect size | advisory usefulness | causation, safety improvement |

## Experiment coverage metrics

| metric | definition | claim_supported |
| --- | --- | --- |
| number of robots | Distinct robot units tested | generalization |
| number of surfaces | Distinct surface types tested | generalization |
| number of sessions | Distinct test sessions | repeatability |
| number of trials | Total valid trials per command | statistical power |
| number of command points | Distinct command velocities tested | response coverage |
| number of navigation tasks | Distinct navigation task protocols | outcome coverage |
| number of obstacle/course variants | Distinct obstacle configurations | outcome robustness |
