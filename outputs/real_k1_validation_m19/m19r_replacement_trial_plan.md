# M19R-B Replacement Trial Plan

This plan lists only surface-speed cells with fewer than 3 valid formal trials after M19R QC.
It does not modify empirical statistics and does not fabricate measurements.

| surface_id | command_velocity | current_valid_count | missing_count | replacement_trial_id | invalid/debug trial IDs |
| --- | ---: | ---: | ---: | --- | --- |
| S1_lab_hard_floor | 0.10 | 2 | 1 | `M19_REP_S1_lab_hard_floor_U010_R4` | M19_S1_lab_hard_floor_B1_U010_R1 |
| S1_lab_hard_floor | 0.40 | 2 | 1 | `M19_REP_S1_lab_hard_floor_U040_R4` | M19_S1_lab_hard_floor_B1_U040_R1 |
| S3_artificial_turf | 0.20 | 2 | 1 | `M19_REP_S3_artificial_turf_U020_R4` | M19_S3_artificial_turf_B1_U020_R1 |
| S3_artificial_turf | 0.30 | 2 | 1 | `M19_REP_S3_artificial_turf_U030_R4` | M19_S3_artificial_turf_B3_U030_R3 |
| S3_artificial_turf | 0.60 | 2 | 1 | `M19_REP_S3_artificial_turf_U060_R4` | M19_S3_artificial_turf_B2_U060_R2 |

Recommended command profile for each replacement row: prepare mode, walking mode, then forward `Move(vx, 0, 0)` for 6.0 s with analysis over 1.0-6.0 s after command start.
Replacement measurements must be collected from logs, video-assisted distance-time evidence, or documented manual distance-time/yaw readings.
