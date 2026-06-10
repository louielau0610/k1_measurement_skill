# M19R Missing Measurement Report

Real M19 trial execution metadata was found, but empirical analysis is blocked.

- Validation status: `blocked_missing_actual_velocity_or_yaw`
- Total CSV rows: 72
- Valid formal rows after debug exclusion: 67
- Valid rows missing `measured_actual_velocity`: 67
- Valid rows missing `yaw_drift_statistic`: 67
- Rows with missing raw log files: 72
- Rows with missing normalized record files: 72

The available CSV cannot support repeated response statistics without velocity and yaw extraction. Command velocity, notes, or trial duration were not used as substitutes for measurements.
