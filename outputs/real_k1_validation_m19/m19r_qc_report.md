# M19R Real Test QC Report

Validation status: `blocked_missing_actual_velocity_or_yaw`

Input CSV: `c:\Users\86138\Desktop\data\m19_repeated_validation_inputs\m19_trial_records.csv`

Total rows: 72

Valid formal rows after debug exclusion: 67

Invalid/debug rows excluded: 5

## Valid Rows Per Surface
- S1_lab_hard_floor: 22 valid / 24 total
- S2_marble_floor: 24 valid / 24 total
- S3_artificial_turf: 21 valid / 24 total

## Incomplete Surface-Speed Cells
- S1_lab_hard_floor @ 0.10 m/s: 2 valid / 3 total
- S1_lab_hard_floor @ 0.40 m/s: 2 valid / 3 total
- S3_artificial_turf @ 0.20 m/s: 2 valid / 3 total
- S3_artificial_turf @ 0.30 m/s: 2 valid / 3 total
- S3_artificial_turf @ 0.60 m/s: 2 valid / 3 total

## Measurement Availability
- measured_actual_velocity available or computed: False
- yaw_drift_statistic available or computed: False
- valid rows missing actual velocity: 67
- valid rows missing yaw drift: 67
- rows with missing raw log files: 72
- rows with missing normalized files: 72

No empirical response-model claim is added while measurement extraction is blocked.
