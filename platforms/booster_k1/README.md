# Booster K1 Platform — Hardened Measurement Reference (M21-B)

Booster K1 is the **first hardened measurement reference platform** for the cross-platform calibration skill. It wraps the completed M19C ROS2 odometer measurement path with a reproducible session workflow.

## Architecture

- **Split-process design**: SDK command process isolated from ROS2 logger process. rclpy and Booster SDK native command client never run in the same process.
- **Dry-run by default**: No hardware movement without explicit `--execute`.
- **Per-trial permit mode**: Each trial requires operator confirmation (can be disabled with `--no-permit`).
- **Append-only trial records**: Invalid trials are recorded with explicit reason.

## Platform Details

| Property | Value |
|----------|-------|
| Primary state source | `/odometer_state` |
| Secondary yaw source | `/low_state.imu_state.rpy` |
| Robot-side setup | `source /opt/booster/BoosterRos2Interface/install/setup.bash` |
| Validated command path | `kPrepare → kWalking → Move(vx, 0, 0)` |
| Gold profile | `outputs/real_k1_validation_m19/k1_gold_profile_v1.json` |
| Split-process required | Yes |
| Hardware validated reference | Yes |

## Module Files

| File | Purpose |
|------|---------|
| `session.py` | Session layout, metadata builder, directory management |
| `measurement_runner.py` | Split-process measurement orchestration (dry-run/execute) |
| `measurement_logger.py` | ROS2 logger process interface |
| `measurement_extractor.py` | State log extraction (velocity, yaw drift) |
| `measurement_qc.py` | Session QC (integrity, completeness, validity) |
| `adapter.py` | Command adapter scaffold (execute disabled by default) |
| `extractor.py` | Odometer extraction wrapper (M19C-compatible) |
| `ros2_odometer_logger.py` | Logger wrapper (M19C-compatible) |
| `config.yaml` | Platform configuration |

## Session Layout

```
data/measurement_sessions/booster_k1/<session_id>/
├── session_metadata.json
├── trial_plan.csv
├── trial_records.csv
├── state_logs/
├── extracted_measurements.csv
├── extraction_summary.json
├── extraction_report.md
├── qc_summary.json
├── qc_report.md
├── response_statistics.csv
├── profile.json
└── profile.md
```

## CLI Commands

```bash
# Dry-run (default, no hardware movement)
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor

# Execute with per-trial permit
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute

# Execute without per-trial permit (use with caution)
python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute --no-permit

# Extract measurements from a session
python scripts/extract_booster_k1_measurements.py --session-dir data/measurement_sessions/booster_k1/<session_id>

# QC a session
python scripts/qc_booster_k1_measurement_session.py --session-dir data/measurement_sessions/booster_k1/<session_id>
```

## Backward Compatibility

Existing M19C artifacts remain unchanged:
- `data/m19c_ros2_odometer_logs/` (gold dataset state logs)
- `data/m19_repeated_validation_inputs/m19c_trial_records.csv`
- `outputs/real_k1_validation_m19/` (gold profile, QC, analysis)
- `outputs/measurement_v1/booster_k1_reference_manifest.json`

New runs go into new session directories under `data/measurement_sessions/booster_k1/`.

## Limitations

- Single Booster K1 unit
- Three tested surfaces (lab hard floor, marble, artificial turf)
- ROS2 odometer-based measurement only
- No velocity compensation
- No GO1/G1 empirical validation
- No cross-platform generalization claim

