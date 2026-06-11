# M19R Claim Evidence Update

| claim | pre-M19 status | M19R status | evidence |
| --- | --- | --- | --- |
| Repeated trials infrastructure | implemented | implemented | scripts, schema, tests |
| Repeated real K1 validation execution | pending | metadata found | 72-row M19 CSV covering three surfaces, eight commands, three targeted repeats |
| Actual velocity response statistics | pending | blocked | `measured_actual_velocity` missing and not computable from available files |
| Yaw drift statistics | pending | blocked | `yaw_drift_statistic` missing and not computable from available files |
| Region classification from repeated data | pending | blocked | output labels remain `pending_measurement_extraction` |
| Uncertainty from repeated trials | pending | blocked | requires measured actual velocity |
| Cross-robot generalization | not supported | not supported | single K1 only |
| All-K1-unit generalization | not supported | not supported | no multi-unit evidence |
| Compensation/safe adapter | not implemented | not implemented | out of scope |
| Navigation improvement | not claimed | not claimed | no navigation experiment evidence |

M19R records real execution metadata but adds no new empirical response-model claim until actual velocity and yaw drift are extracted from valid measurement logs.

M19R-B adds a measurement completion pack: exact replacement-trial planning, a blank annotation template, a measurement protocol, and annotation QC. It does not fill real measurements and does not add response-model or risk-map empirical claims.

M19R-C-prep records that replacement trials completed the execution-level M19 design and creates a valid-only annotation template. It does not add measured velocity/yaw values, response-model validation, risk-map validation, navigation improvement, or cross-robot generalization.

M19R-C annotation intake validation adds a QC gate for future filled measurements. The current template passes structural validation, but no empirical response-model or risk-map claim is added until real actual velocity and yaw drift values are present.

M19R-C SDK state logger prep adds tooling to discover and log SDK state sources, but local discovery did not detect an importable Booster SDK. This is measurement-readiness tooling only and adds no empirical response-model, risk-map, navigation, or cross-robot claim.

M19R-C ROS2 odometer prep updates the planned measurement source priority to `/odometer_state` after robot-side interface discovery. This remains measurement-source validation only; no M19 empirical response or risk-map claim is added.
