# M24-H Controlled S2 Replication Execution Protocol

**Status**: Execution pack. The first physical attempt before the subprocess hotfix is invalid/debug.
**Physical run status**: `not_run`

## Physical Setup

1. Position Booster K1 on S2_marble_floor.
2. Mark start pose and straight path (~3m minimum).
3. Ensure path is clear of obstacles.
4. Confirm battery > 50%.

## Trial Parameters

| Parameter | Value |
|-----------|-------|
| Surface | S2_marble_floor only |
| Condition | direct_refresh_controlled only |
| Command velocities | 0.40, 0.45, 0.50, 0.55 m/s |
| Repeats per velocity | 5 |
| Total trials | 20 |
| Compensated commands | FORBIDDEN |
| Profile update during run | FORBIDDEN |

## Operator Checklist (Per Trial)

- [ ] Robot at marked start pose.
- [ ] Path clear ahead.
- [ ] Operator confirms reset.
- [ ] Respond `y` to permit prompt.
- [ ] Wait for trial to complete (~10s).
- [ ] Verify robot stopped.

## Invalid Trial Criteria

Mark trial invalid if:
- Robot collides or slips.
- Robot deviates from straight path.
- State log missing or corrupted.
- Operator aborts.
- ROS2 odometer unavailable.

## Metadata Recording

Fill `controlled_metadata.json` before session:
- `robot_id`, `warmup_status`, `start_pose_label`, `path_label`, `battery_level_start`.

Update `battery_level_end` after session.

## Split-Process Architecture

- Logger subprocess: `log_m24h_controlled_s2_replication_trial.py` (rclpy only; accepts `direct_refresh_controlled`)
- SDK subprocess: `send_m23b_k1_velocity_command.py` (Booster SDK only; runner passes `--log-dir <session_state_logs_dir>`)
- Runner: orchestrates both, imports neither rclpy nor SDK

## Hotfix Note

The first M24-H physical attempt failed before robot motion because the runner invoked the old M23-B logger, which rejects `direct_refresh_controlled`, and did not pass the SDK sender's required `--log-dir`. That attempted session is invalid/debug. Formal controlled replication must use the hotfixed runner.

## Post-Run

1. Corrected extraction (`extract_m24h_controlled_s2_replication_trials.py`).
2. QC (`qc_m24h_controlled_s2_replication_session.py`).
3. Verify 20 trials, 4 groups × 5 repeats, all extraction OK.

## Claim Boundary

- Physical trials: not yet executed.
- Tracking improvement: not claimed.
- Profile adoption: not adopted.
- Deployment: not ready.
- GO1/G1: blocked.
