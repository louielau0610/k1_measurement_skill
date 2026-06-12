# M24-D Measurement Assumption Audit

| Assumption | M19C | M23-C | M24-C | Status | Notes |
|------------|------|-------|-------|--------|-------|
| extraction_method | ROS2 odometer profile extraction | M23-B/M23-C odometer extraction | M24-B/M24-C odometer extraction | broadly_consistent | All use odometer-derived actual velocity; exact implementation should still be audited. |
| forward_projection_method | forward projection from x/y/theta | odometer displacement/direct extracted fields | odometer forward projection window | needs_audit | M24-C near-zero result makes extraction-window and pose-reset review important. |
| command_duration | M19C repeated validation command window | 6 sec command phase | 6 sec command phase | partly_consistent | M23-C and M24-C match; M19C should be checked from original protocol. |
| idle_stop_duration | protocol dependent | 2 sec idle / 2 sec stop | 2 sec idle / 2 sec stop | partly_consistent | M23-C and M24-C match runner defaults. |
| state_topics | /odometer_state plus low_state/IMU where available | /odometer_state plus /low_state | /odometer_state plus /low_state | consistent | Topic names are aligned. |
| odometer_source | booster_interface/msg/Odometer | booster_interface/msg/Odometer | booster_interface/msg/Odometer | consistent | Same nominal odometer source. |
| imu_yaw_source | low_state or IMU cross-check | low_state/IMU cross-check | low_state IMU yaw cross-check | consistent | IMU yaw is not primary velocity evidence. |
| session_surface_label | S2_marble_floor | S2_marble_floor | S2_marble_floor | consistent | Labels match but physical condition may still differ. |
| number_of_repeats | 3 per old profile cell | 3 direct trials per overlap velocity | 5 direct-refresh repeats per velocity | different | M24-C has more repeats but near-zero response. |
| velocity_set | 0.10-0.60 selected profile speeds | 0.40,0.45,0.50,0.55 | 0.35,0.40,0.45,0.50,0.55,0.60 | overlap_partial | Overlap for three-way comparison is 0.40, 0.45, 0.50. |
| direct_vs_compensated_condition | direct profile only | direct and compensated pairs | direct_refresh only | partly_consistent | M23-C direct fields are used for consistency only. |
| trial_reset_starting_pose_controlled | not fully encoded in profile artifact | not fully encoded in pair CSV | not fully encoded in M24-C outputs | unknown | Operator reset/path effects remain hypotheses. |
| battery_warmup_environment_recorded | not available in aggregate profile | not available in pair CSV | not available in summary | unknown | Robot state or warm-up effects remain hypotheses. |
