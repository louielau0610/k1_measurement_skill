# M21 Trial Sheet Template v1

> Fill one sheet per trial. All values are placeholders until real experiments are conducted.

| field | value |
| --- | --- |
| trial_id | TO_BE_FILLED_BY_FUTURE_TRIAL |
| session_id | TO_BE_FILLED |
| date | TO_BE_FILLED |
| start_time | TO_BE_FILLED |
| end_time | TO_BE_FILLED |
| robot_model | K1 |
| robot_id | TO_BE_FILLED |
| surface_type | TO_BE_FILLED |
| operator | TO_BE_FILLED |
| vx_cmd_mps | TO_BE_FILLED |
| vy_cmd_mps | OPTIONAL_IF_AVAILABLE |
| omega_z_cmd_radps | OPTIONAL_IF_AVAILABLE |
| trial_duration_s | TO_BE_FILLED |
| advisory_condition | TO_BE_FILLED (true/false for Tiers 3/4) |
| navigation_task_id | NOT_APPLICABLE (or TO_BE_FILLED for Tiers 3/4) |
| raw_log_path | TO_BE_FILLED |
| video_path | OPTIONAL_IF_AVAILABLE |
| vx_actual_mps_mean | TO_BE_FILLED (after processing) |
| qualitative_response_label | TO_BE_FILLED (after processing) |
| tracking_error_mps | TO_BE_FILLED (after processing) |
| response_delay_s | TO_BE_FILLED (after processing) |
| stop_distance_m | TO_BE_FILLED (after processing) |
| lateral_drift_mps | TO_BE_FILLED (after processing) |
| yaw_drift_deg_per_s | TO_BE_FILLED (after processing) |
| collision_count | TO_BE_FILLED (Tiers 3/4) |
| near_miss_count | TO_BE_FILLED (Tiers 3/4) |
| task_success | TO_BE_FILLED (Tiers 3/4) |
| trial_valid | TO_BE_FILLED |
| exclusion_reason | TO_BE_FILLED (if invalid) |
| operator_notes | TO_BE_FILLED |

## Claim-safety self-check (per trial)

- [ ] No `remote_controller_state` recorded.
- [ ] No compensation flag set true.
- [ ] No safe_command_adapter flag set true.
- [ ] No navigation_safety_improvement claim made.
- [ ] All metrics from logging only — not fabricated.
