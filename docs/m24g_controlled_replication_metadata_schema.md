# M24-G Controlled Replication Metadata Schema

This schema defines metadata for a future controlled S2 replication session. It avoids requiring fields that may not be reliably captured on the robot; optional fields should be blank rather than guessed.

## Required Fields

| Field | Requirement | Notes |
|-------|-------------|-------|
| `session_id` | required | Unique controlled replication session identifier. |
| `surface` | required | Must be `S2_marble_floor`. |
| `robot_id` | required | Operator-visible robot identifier. |
| `warm_up_status` | required | Example: `completed`, `not_completed`, `unknown`. |
| `start_pose_label` | required | Marked start pose used for every trial. |
| `path_label` | required | Marked straight path used for every trial. |
| `operator_reset_confirmation` | required | Operator confirms reset before each trial. |
| `trial_distance_path_clearance_confirmation` | required | Operator confirms path clearance before each trial. |
| `command_velocity_mps` | required | Direct command velocity. |
| `desired_velocity_mps` | required | Desired velocity, equal to command for direct trials. |
| `repeat_index` | required | Repeat number within the velocity group. |
| `extraction_window_method` | required | Expected value: command phase with 1 second trim. |
| `notes` | required | Empty string allowed when no notes are needed. |

## Optional Fields

| Field | Requirement | Notes |
|-------|-------------|-------|
| `firmware_software_notes` | optional | Fill if the version or robot-side environment is available. |
| `battery_level` | optional | Fill if a reliable value is available. |
| `operator_id` | optional | Fill if useful for traceability. |
| `ambient_notes` | optional | Fill for unusual surface, lighting, or room conditions. |
| `logger_topic_notes` | optional | Fill if ROS2 topic availability differs from expected. |

## Boundary

Missing optional metadata must not be fabricated. Required metadata should be captured during execution; if a required field is unavailable for a trial, the trial should be reviewed or invalidated before analysis.
