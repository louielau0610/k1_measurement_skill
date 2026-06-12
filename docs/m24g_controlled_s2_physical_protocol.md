# M24-G Controlled S2 Physical Protocol

This protocol standardizes a future controlled direct-response replication on Booster K1. M24-G itself does not run the robot.

## Scope

- Surface: `S2_marble_floor` only.
- Condition: `direct_refresh_controlled` only.
- Commands: direct velocity commands only.
- Compensated commands: none.
- Core velocities: 0.40, 0.45, 0.50, and 0.55 m/s.
- Core repeats: 5 per velocity.
- Optional extension velocities: 0.35 and 0.60 m/s.

## Start Pose and Path

- Use one marked start pose label for the full session.
- Align the robot body with the marked path direction before every trial.
- Use one straight path label for the full session.
- Keep the usable path length long enough for idle, command, and stop phases without contacting obstacles.
- Confirm path clearance before each trial.

## Reset and Warm-Up

- Warm up the robot with a short direct walking check before recording controlled trials.
- Record warm-up status in session metadata.
- After each trial, return the robot to the marked start pose.
- Confirm operator reset before starting the next trial.
- Do not change surface, path, or start pose within the controlled session.

## Timing

- Idle phase: 2 seconds.
- Command phase: 6 seconds.
- Stop/settle phase: 2 seconds.
- Extraction window method: command phase with a 1 second trim at the start and end unless a later execution pack explicitly documents a different method.

## Operator Checklist

- Robot is on `S2_marble_floor`.
- Path is clear for the full trial.
- Start pose label is visible and unchanged.
- Robot heading matches the path direction.
- Battery level is recorded if available.
- Firmware/software notes are recorded if available.
- `/odometer_state` logging is active before command execution.
- Emergency stop path is available.

## Trial Invalidation Rules

Invalidate a trial if:

- The robot is not reset to the start pose.
- The path is obstructed.
- The robot contacts an obstacle or is manually touched during command.
- Logger data are missing or timestamp order is invalid.
- The wrong velocity is commanded.
- The wrong surface or condition is used.
- The operator cannot confirm path clearance or reset.

## Metadata to Record

Record the fields in `docs/m24g_controlled_replication_metadata_schema.md` for the session and for every trial. Optional fields should be filled when reliably available and left blank when not available.
