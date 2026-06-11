# M19R Repeated Validation Evidence Notes

## Infrastructure status
- M19-A repeated validation infrastructure: **implemented**.
- M19R real single-K1 trial execution metadata: **found**.
- Real trial matrix target: 3 surfaces x 8 command velocities x 3 repeats = 72 rows.
- Actual velocity and yaw drift extraction: **blocked pending measurement data**.

## Real metadata found
- Input CSV: `c:\Users\86138\Desktop\data\m19_repeated_validation_inputs\m19_trial_records.csv`
- Total rows: 72.
- Valid formal rows after invalid/debug exclusion: 67.
- Invalid/debug rows excluded: 5.
- Valid rows per surface:
  - `S1_lab_hard_floor`: 22 / 24.
  - `S2_marble_floor`: 24 / 24.
  - `S3_artificial_turf`: 21 / 24.

## Measurement blocker
- `measured_actual_velocity` is missing for all 67 valid formal rows.
- `yaw_drift_statistic` is missing for all 67 valid formal rows.
- Referenced raw log and normalized record files were not found in the inspected input tree.
- Command velocity, notes, and trial duration are not used as substitutes for actual measurements.

## Claim evidence update
- No new empirical response-model claim is added yet.
- Single-K1 multi-surface execution metadata exists, but response statistics remain pending velocity/yaw extraction.
- Cross-robot generalization remains unsupported.
- All-K1-unit generalization remains unsupported.
- Compensation controller, safe command adapter, and navigation improvement claims remain out of scope.

## M19R-B completion pack
- M19R-B adds a replacement-trial plan for the five incomplete surface-speed cells.
- M19R-B adds a blank measurement annotation template for 67 execution-valid trials plus 5 replacement placeholders.
- M19R-B adds annotation QC, but no real measurements are filled by the template.
- Empirical response analysis remains blocked until actual velocity and yaw drift are filled from acceptable evidence sources and pass QC.

## M19R-C prep update
- Replacement trials restored execution-level completeness: 72 execution-valid formal trials are now available across 24 surface-speed cells.
- The valid-only annotation template excludes 5 invalid/debug rows and includes 5 valid replacement rows.
- Actual velocity and yaw drift remain unfilled, so empirical response analysis and risk-map validation remain blocked.

## M19R-C annotation intake validation
- The annotation intake validator checks exact valid-trial ID membership, duplicate IDs, invalid/debug ID exclusion, required annotation fields, quality flags, numeric measurement parsing, and detectable placeholder tokens.
- The current valid-only annotation template passes intake validation with no filled measurements and no issues.
- This validation is a pre-analysis safeguard only; it does not compute response statistics or add empirical claims.

## M19R-C SDK state logger prep
- SDK state discovery and smoke logging scripts were added to prioritize robot-side odometer/IMU/transform logs over manual video annotation.
- In the local development workspace, the Booster SDK is not importable, so no usable SDK state source, position stream, or yaw stream is detected yet.
- The full M19C measurement run remains gated on robot-side SDK discovery and smoke logs; empirical analysis remains blocked.

## M19R-C ROS2 odometer update
- Robot-side discovery indicates `/odometer_state` provides `x`, `y`, and `theta`, making ROS2 odometer logs the primary planned measurement source.
- `/low_state.imu_state.rpy` and IMU topics are retained as yaw fallbacks or cross-checks.
- `GetFrameTransform` is downgraded because available frames are local body-part frames, not global odom/world/map frames.
- Local smoke artifacts do not confirm ROS2 availability; full M19C measurement remains gated on robot-side odometer smoke validation.

## M19C full-run infrastructure
- Physical smoke tests indicate ROS2 odometer extraction is feasible: 0.20 m/s produced near-zero motion, while 0.40 and 0.60 m/s produced nonzero extracted velocity and yaw drift.
- The full 72-trial ROS2 odometer runner, extractor, QC, and protocol are implemented.
- Empirical M19C analysis remains pending until full physical logs are collected and extracted; no response-model or risk-map claim is added yet.

## M19C-E empirical K1 profile
- M19C produced a complete 72-trial K1 empirical velocity-response dataset across three surfaces and eight command speeds.
- The dataset supports tested-K1 evidence of speed-response nonlinearity, surface dependence, low-speed deadzone behavior, and yaw-drift variation.
- The result is a single-K1, odometer-measured calibration profile; it does not prove cross-robot generalization, navigation improvement, or compensation-controller validity.
