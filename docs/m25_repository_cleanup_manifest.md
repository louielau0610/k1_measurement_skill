# M25 Repository Cleanup Manifest

## Summary

M25 creates a new active full-range velocity profiling path and marks deadzone research, deadzone compensation, yaw drift modeling, yaw compensation, and yaw-based validation as out of scope for the active M25 pipeline.

No tracked repository files were deleted in this pass. The audit found many historical milestone files and raw data artifacts containing deadzone or yaw fields. They were preserved because they are historical evidence, raw immutable measurement data, regression fixtures, or mixed-purpose infrastructure.

## Deleted Files

None.

## Renamed Or Moved Files

None inside the tracked repository.

## Substantially Refactored Mixed-Purpose Files

None. Existing mixed-purpose historical modules remain available for legacy tests and prior milestone reproducibility. New M25 code does not import them.

## Active M25 Files Added

| Path | Category | Reason | Reference cleanup |
|------|----------|--------|-------------------|
| `k1_measurement/full_range_velocity_profile.py` | code | New M25 domain contract, planner, session validation, candidate profile builder, and historical audit utilities. | Does not import deadzone or yaw compensation modules. |
| `scripts/validate_m25_full_range_velocity_config.py` | code | CLI for M25 configuration validation. | New isolated entry point. |
| `scripts/plan_full_range_velocity_profile.py` | code | CLI for exploration and formal planning artifacts. | New isolated entry point. |
| `scripts/validate_m25_collected_session.py` | code | CLI for collected-session contract validation. | New isolated entry point. |
| `scripts/build_m25_candidate_profile.py` | code | CLI for candidate-profile dry-run/build. | New isolated entry point. |
| `scripts/audit_m25_historical_compatibility.py` | code | CLI for historical compatibility audit. | New isolated entry point. |
| `configs/m25_full_range_velocity_profile_template.yaml` | config | Default M25 template with unresolved safe maximum. | New isolated config. |
| `tests/test_m25_full_range_velocity_profile.py` | test | Focused M25 contract, planning, profile, audit, CLI, and import-boundary tests. | New isolated tests. |

## Intentionally Preserved Historical Or Raw Artifacts

The following categories were intentionally preserved:

- `data/m19c_ros2_odometer_logs/`: raw ROS2 odometer logs that can support extraction verification and historical reproducibility.
- `data/m19c_full_72_measurement_run/`: historical raw/full-run evidence.
- `data/compensation_experiments/m24b_s2_profile_refresh/`: physical profile-refresh session data and corrected extraction artifacts.
- `data/compensation_experiments/m24h_controlled_s2_replication/`: controlled replication session data and corrected extraction artifacts.
- `outputs/real_k1_validation_m19/`: historical M19 summaries, tables, and the existing gold profile.
- `outputs/compensation_research/` and `outputs/compensation_experiments/`: prior milestone reports and generated evidence used by existing tests and status history.
- `calibration_core/*compensation*` and M22-M24 scripts/tests: legacy offline compensation and physical experiment history retained for reproducibility; not imported by the M25 pipeline.
- Raw yaw columns in historical CSV/JSON files: retained as immutable source fields; ignored by M25 modeling and validation.

## Retention Reasons

Historical files were retained when they met at least one of these conditions:

- active tests still depend on them;
- they are raw or near-raw real-robot evidence;
- they preserve provenance for M19, M23, or M24 decisions;
- they contain reusable velocity measurement/session/logging/extraction infrastructure;
- deleting them would remove auditability without improving the active M25 contract.

## Reference Cleanup Confirmation

The active M25 module and CLI wrappers do not import deadzone detection, deadzone compensation, yaw drift modeling, yaw compensation, real-time yaw broadcast, or yaw-based benefit-gate modules. Remaining deadzone/yaw references are historical, raw-schema compatibility, explicit out-of-scope statements, or legacy milestone material.

## M25-R Second Audit

M25-R performed a stricter dependency-aware audit of the dirty working tree, generated outputs, historical artifacts, and active M25 files.

### Deleted Files

None.

### Retained Dirty Or Untracked Paths

| Path | Decision | Evidence |
|------|----------|----------|
| `AGENTS.md` | retain | User-authored documentation rule; unrelated to M25-R implementation. |
| `outputs/compensation_experiments/m24e_extraction_anomaly_report.md` | retain | Timestamp-only generated diff; not staged, not raw data. |
| `outputs/compensation_experiments/m24e_extraction_anomaly_summary.json` | retain | Timestamp-only generated diff; not staged, not raw data. |
| `outputs/compensation_experiments/m24e_extraction_audit_decision.json` | retain | Timestamp-only generated diff; not staged, not raw data. |
| `outputs/compensation_experiments/m24e_extraction_audit_decision.md` | retain | Timestamp-only generated diff; not staged, not raw data. |
| `outputs/compensation_experiments/m24e_m24c_crosscheck.md` | retain | Timestamp-only generated diff; not staged, not raw data. |
| `outputs/real_k1_validation_m19/m19_validation_report.md` | requires user review | Historical evidence rewrite; not safe to discard or stage. |
| `outputs/real_k1_validation_m19/repeated_validation_summary.json` | requires user review | Large historical evidence rewrite; not safe to discard or stage. |
| `data/measurement_sessions/` | ignore via `.gitignore` | Local raw/session execution tree; preserved and ignored for future status hygiene. |
| `docs/project_overview.md` | retain | Pre-existing documentation artifact. |
| `docs/modules/calibration_core_implementation.md` | retain | Pre-existing documentation artifact. |
| `docs/modules/calibration_core_principles.md` | retain | Pre-existing documentation artifact. |
| `docs/modules/platforms_implementation.md` | retain | Pre-existing documentation artifact. |
| `docs/modules/platforms_principles.md` | retain | Pre-existing documentation artifact. |

### Generated Output Policy Changes

`.gitignore` now ignores local `data/measurement_sessions/` trees, M25 fixture CSVs, temporary resolved safe-speed validation configs, and M25 local preflight write probes. Existing tracked scientific summaries remain tracked.

### Active Artifact Audit Result

No active M25-R code imports deadzone or yaw-compensation modules. No M26 model-fitting code was added. Obsolete generated files were not deleted because the only conclusive candidates were either already tracked historical summaries, raw/session-like data, or unrelated timestamp-only changes whose ownership predates M25-R.
