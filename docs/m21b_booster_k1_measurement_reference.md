# M21-B: Booster K1 Measurement Reference Implementation Hardening

M21-B hardens Booster K1 as the **first hardened measurement reference platform** in the cross-platform calibration skill.

## Motivation

The measurement module (Step 1 of the roadmap) needs a reproducible, safety-first measurement workflow before proceeding to velocity compensation (Step 2/3). M21-B wraps the validated M19C-E behavior into a standardized, split-process measurement session framework.

## Architecture

### Split-Process Design

The Booster K1 measurement workflow enforces a strict process separation:

```
┌─────────────────────────┐     ┌──────────────────────────┐
│  SDK Command Process    │     │  ROS2 Logger Process     │
│  (robot-side)           │     │  (robot-side, separate)  │
│                         │     │                          │
│  Booster SDK native     │     │  rclpy + subscription    │
│  kPrepare → kWalking    │     │  /odometer_state         │
│  Move(vx, 0, 0)         │     │  /low_state.imu_state    │
└─────────────────────────┘     └──────────────────────────┘
         │                                │
         │  never combined in same        │
         │  Python runtime process        │
         ▼                                ▼
   Measurement Runner orchestrates both via operator prompts
```

**Reason**: The Booster SDK native command client and rclpy have incompatible runtime requirements. Combining them in one process risks initialization conflicts, resource contention, and silent failures. The split-process design ensures:
- The SDK command path remains clean and debuggable.
- The ROS2 logger can be started/stopped independently.
- Operator maintains full awareness of which process is active.

### Dry-Run Safety

- **Default**: Dry-run only. No hardware movement.
- **Execute**: Requires explicit `--execute` flag.
- **Per-trial permit**: Each trial requires operator confirmation by default (`[y/N]` prompt).
- **Permit can be disabled**: `--no-permit` for automated runs (use with caution).

### Append-Only Trial Records

- Trial records are written to `trial_records.csv` in append mode.
- Invalid trials are recorded with explicit `invalid_reason`.
- No trial data is ever deleted or overwritten within a session.

## Session Layout

```
data/measurement_sessions/booster_k1/<session_id>/
├── session_metadata.json       # All required metadata fields
├── trial_plan.csv              # Deterministic trial schedule
├── trial_records.csv           # Append-only per-trial outcomes
├── state_logs/                 # Per-trial state log CSVs
│   ├── K1_S1_B1_U020_R1.csv
│   └── ...
├── extracted_measurements.csv  # Extracted velocity + yaw drift
├── extraction_summary.json     # Extraction batch summary
├── extraction_report.md        # Human-readable extraction report
├── qc_summary.json             # QC check results
├── qc_report.md                # Human-readable QC report
├── response_statistics.csv     # Aggregated response statistics
├── profile.json                # Velocity profile
└── profile.md                  # Human-readable profile
```

## Workflows

### Dry-Run Workflow

```bash
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor
```

Output:
- Prints trial plan.
- Creates session directory with metadata.
- **No hardware movement**.
- Instructs user to re-run with `--execute` for real trials.

### Execute Workflow

```bash
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute
```

1. Creates session directory.
2. Writes `session_metadata.json`.
3. Writes `trial_plan.csv`.
4. For each trial:
   a. Prints split-process instructions (start ROS2 logger, send SDK command).
   b. Prompts operator for confirmation `[y/N]`.
   c. Records trial outcome in `trial_records.csv` (append-only).
5. Summary printed at end.

### Extraction Workflow

```bash
python scripts/extract_booster_k1_measurements.py --session-dir data/measurement_sessions/booster_k1/<id>
```

Reads:
- `session_metadata.json`
- `state_logs/*.csv`

Produces:
- `extracted_measurements.csv`
- `extraction_summary.json`
- `extraction_report.md`

Extracts:
- `measured_actual_velocity` (from odometer displacement over command window)
- `yaw_drift_statistic` (from odometer theta or IMU yaw)
- Per-sample velocity statistics

### QC Workflow

```bash
python scripts/qc_booster_k1_measurement_session.py --session-dir data/measurement_sessions/booster_k1/<id>
```

Checks:
- Session metadata exists
- Trial plan exists
- Trial records exist
- State logs directory exists
- Extraction output exists
- No duplicate trial IDs
- Required fields present
- Expected repeats per surface-speed cell
- No command_velocity copied into measured_actual_velocity
- Invalid trials have explicit reasons

## Relation to M19C-E Gold Profile

M21-B **does not overwrite** any M19C-E artifacts:

| M19C-E Artifact | Status |
|-----------------|--------|
| `data/m19c_ros2_odometer_logs/` | Unchanged |
| `data/m19_repeated_validation_inputs/m19c_trial_records.csv` | Unchanged |
| `outputs/real_k1_validation_m19/k1_gold_profile_v1.json` | Unchanged |
| `outputs/measurement_v1/booster_k1_reference_manifest.json` | Updated (added M21-B paths) |

New M21-B session data goes into `data/measurement_sessions/booster_k1/`.

## Module Files

| File | Purpose |
|------|---------|
| `platforms/booster_k1/session.py` | Session layout, metadata builder |
| `platforms/booster_k1/measurement_runner.py` | Split-process measurement orchestration |
| `platforms/booster_k1/measurement_logger.py` | ROS2 logger process interface |
| `platforms/booster_k1/measurement_extractor.py` | Velocity + yaw drift extraction |
| `platforms/booster_k1/measurement_qc.py` | Session integrity QC |
| `scripts/run_booster_k1_measurement.py` | Unified measurement CLI |
| `scripts/extract_booster_k1_measurements.py` | Unified extraction CLI |
| `scripts/qc_booster_k1_measurement_session.py` | Unified QC CLI |

## Fixture/Replay Test Mode

For CI and offline testing without hardware:

- `tests/fixtures/fixture_helpers.py` — Builds synthetic session directories with:
  - Minimal `session_metadata.json` (marked as test fixture)
  - Synthetic trial plan and records
  - Synthetic state logs with realistic velocity data
- Fixture data is clearly labeled as test-only (not empirical robot results).
- Fixture outputs are not exported as robot measurement profiles.

## Limitations

- Single Booster K1 unit validated
- Three tested surfaces (lab hard floor, marble, artificial turf)
- ROS2 odometer-based measurement only
- No IMU-only measurement fallback
- Split-process design requires two terminal sessions on the robot
- Per-trial permit default slows down automated batch runs (by design)

## What Is NOT Claimed

- ❌ Velocity compensation (future Step 2/3)
- ❌ Inverse response model
- ❌ Command remapping
- ❌ Navigation control
- ❌ Safe command adaptation
- ❌ GO1 hardware validation (future Step 4)
- ❌ G1 hardware validation (future Step 4)
- ❌ Cross-platform empirical validation
- ❌ Publication readiness
- ❌ Navigation performance improvement

## Phase Gates

| Gate | Status |
|------|--------|
| `velocity_compensation_ready` | `false` |
| `unitree_go1_measurement_ready` | `false` |
| `unitree_g1_measurement_ready` | `false` |
| `cross_platform_empirical_validation` | `false` |
| `navigation_improvement_claimed` | `false` |
| `booster_k1_reference_ready` | `true` |
