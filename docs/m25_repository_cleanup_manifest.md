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
| `configs/m25_full_range_velocity_profile_template.yaml` | config | M25 template with K1 domain (safe max resolved via M25-S confirmation file). | Config. |
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

## M25-T Legacy Defaults And Active-Path Classification

M25-T audited `max_vx_cmd_mps`, `safe_command_speed_max`, `0.4` defaults, low-speed/deadzone defaults, and yaw-drift gates across active code, configs, scripts, tests, and docs.

| Path | Classification | Notes |
|------|----------------|-------|
| `k1_measurement/command_runner.py` | active-current-path | Generic `CommandRunner` no longer silently defaults to `0.4`; validation fails closed until an explicit max is supplied. |
| `k1_measurement/m25_real_collection_preflight.py` | active-current-path | Resolves `safe_command_speed_max` from validated K1 confirmation, propagates safety provenance, and validates the fixed K1 SDK sequence. |
| `k1_measurement/full_range_velocity_profile.py` | active-current-path | Requires a configured safe maximum for executable M25 plans and rejects commands above the resolved limit. |
| `configs/m25_k1_s2_real_collection.yaml` | active-current-path | Concrete K1 domain `[0.35, 0.60]` with `command_source: booster_sdk_kPrepare_kWalking_Move`; `control_mode`/`gait_mode` optional. |
| `configs/m25_k1_safe_speed_operator_confirmation.yaml` | active-current-path | Authoritative current K1 safe-speed evidence: `safe_command_speed_max: 0.6`. |
| `outputs/full_range_velocity_profile/m25r_*_collection_package.*` | active-current-path | Regenerated with motion-path metadata and safety provenance; exploration has 12 trials, formal has 30 and remains review-gated. |
| `config/experiment_forward_v0.yaml` | historical-only | Legacy M5/M8 dry-run baseline with `max_vx_cmd_mps: 0.4` and `[0.1, 0.2, 0.3, 0.4]`; not the M25 execution source. |
| `k1_measurement/trial_manager.py` | historical-only | Consumes the legacy baseline config for old dry-run tests; M25 package generation does not depend on it for safety limits. |
| `tests/test_trial_manager.py`, `tests/test_field_session.py`, `tests/test_profile_builder.py` | test-fixture | Preserve legacy low-speed expectations for earlier milestone regressions. |
| `scripts/analyze_m19_repeated_validation.py` | historical-only | Contains deadzone and yaw-risk thresholds for M19 repeated-validation analysis only. |
| `scripts/analyze_real_k1_forward_velocity.py` | historical-only | Contains old yaw-repeat recommendations and deadzone labels for early real-K1 analysis artifacts only. |
| `scripts/analyze_m24c_s2_profile_refresh.py`, `scripts/analyze_m24f_corrected_s2_profile_refresh.py`, `scripts/analyze_m24i_controlled_s2_replication.py` | historical-only | Preserve yaw columns/summary statistics for M24 analyses; not imported by M25 planning/preflight. |
| `calibration_core/*compensation*`, `scripts/*compensat*`, `tests/test_m22*`, `tests/test_m23*` | historical-only | Offline compensation and physical-compensation history retained for reproducibility, not active M25 execution. |
| `tests/test_m25_full_range_velocity_profile.py`, `tests/test_m25_real_collection_preflight.py`, `tests/test_command_runner.py` | active-current-path/test-fixture | Protect M25 safe-limit behavior, optional K1 mode context, package counts, and fail-closed runner behavior. |

No obsolete-active-default remains in the M25 real-execution path. The old `0.4` limit is retained only in explicitly historical or fixture contexts. M25 execution does not import deadzone analysis modules and does not depend on yaw-drift gates.
