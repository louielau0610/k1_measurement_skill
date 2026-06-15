# Current Repository Inventory — M26-A Audit

**Date**: 2026-06-15
**Branch**: `engineering/m26a-program-reset-audit`
**Status**: Complete

## Overview

This document summarizes the repository inventory performed for M26-A.
The complete machine-readable audit is at:
`outputs/engineering/m26a_repository_audit.json`.

## Repository Structure Summary

### Python Packages

| Package | Path | Files | Role |
|---|---|---|---|
| `calibration_core` | `calibration_core/` | 19 `.py` files | Cross-platform calibration core (domain, compensation, extraction, profiles) |
| `k1_measurement` | `k1_measurement/` | 21 `.py` files | K1-specific measurement tooling, field logging, visualization, metrics |
| `platforms/booster_k1` | `platforms/booster_k1/` | 10 `.py` files + config | Booster K1 hardware-validated adapter |
| `platforms/unitree_g1` | `platforms/unitree_g1/` | 4 files + config | Unitree G1 scaffold adapter (not implemented) |
| `platforms/unitree_go1` | `platforms/unitree_go1/` | 4 files + config | Unitree GO1 scaffold adapter (not implemented) |

### Scripts

- **93 Python scripts** in `scripts/`
- Categories: analysis, audit, compensation (offline), extraction, field session,
  K1 SDK/ROS2 logging, profile building, QC, validation, discovery, report generation

### Configurations

- 12 YAML/JSON config files in `configs/` and `config/`
- Authoritative safety config: `configs/m25_k1_safe_speed_operator_confirmation.yaml`

### Tests

- **62 test files** in `tests/`
- All pytest-based, all runnable without hardware SDK

### Documentation

- **72+ Markdown files** in `docs/`
- Coverage: M7-M25 milestones, compensation research, S2 profile refresh,
  measurement foundation, paper-related docs

### Outputs

- 15 subdirectories under `outputs/`
- Includes: compensation experiments, research datasets, validation results,
  gold profile, full-range velocity profile outputs

### Data

- 8 subdirectories under `data/`
- Raw measurement sessions, processed data, compensation experiment logs

## Key Audit Findings

### Safety-Critical Paths

1. **`platforms/booster_k1/adapter.py`** — `BoosterK1CommandAdapter`
   - Contains the validated command sequence `kPrepare -> kWalking -> Move(vx, 0.0, 0.0)`
   - Raises `NotImplementedError` if execution not explicitly enabled
   - **Classification**: verified_in_repository

2. **`configs/m25_k1_safe_speed_operator_confirmation.yaml`**
   - `safe_command_speed_max: 0.6`
   - Confirmed by operator at 2026-06-15
   - **Classification**: verified_in_repository

3. **`scripts/send_m23b_k1_velocity_command.py`**
   - Contains conditional velocity command sending
   - Requires explicit execution flags
   - **Classification**: verified_in_repository

4. **`k1_measurement/command_runner.py`** — `K1CommandRunner`
   - Dry-run by default (`dry_run=True`)
   - Validates speed against safe maximum
   - **Classification**: verified_in_repository

### Architecture Boundary Violations

1. **`calibration_core/compensation_models.py`** — `SUPPORTED_EMPIRICAL_PLATFORM = "booster_k1"`
   - Hardcoded K1 platform string in a "generic" core module
   - **Disposition**: Migrate to platform registry lookup

2. **`calibration_core/profile_loader.py`** — `load_k1_gold_profile()`
   - Hardcoded K1 gold profile path in core
   - **Disposition**: Parameterize profile path; keep convenience function in K1 adapter

3. **`calibration_core/__init__.py`** — exports `load_k1_gold_profile`
   - K1-specific function in core public API
   - **Disposition**: Move to K1 adapter or deprecate in core

4. **`calibration_core/platform_registry.py`** — imports from all three platform packages at function scope
   - Dynamically imports `platforms.booster_k1`, `platforms.unitree_g1`, `platforms.unitree_go1`
   - **Disposition**: Acceptable as registry pattern; ensure import errors are caught

### Implicit Defaults and Duplicated Constants

1. **Safe speed maximum**: Defined in `configs/m25_k1_safe_speed_operator_confirmation.yaml` (`0.6`),
   also appears in `k1_measurement/full_range_velocity_profile.py` and test files
2. **Valid command domain**: `[0.35, 0.60]` appears in multiple config files and Python modules
3. **Command sequence**: `kPrepare -> kWalking -> Move(vx, 0.0, 0.0)` referenced in multiple places
4. **Gold profile path**: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json` hardcoded in `profile_loader.py`

### Import-Time Side Effects

- **None detected** — No global socket connections, no ROS2 subscriptions at import,
  no automatic hardware initialization
- `rclpy` imports are try/except guarded in ROS2-related modules
- `booster_robotics_sdk` imports are conditional in smoke test scripts

### Network Side Effects

- **ROS2 read-only**: `ros2 topic list`, `ros2 bag record` via `subprocess.run()`
- No outbound command publishing at import time
- `field_logging.py`: builds `ros2 bag record` command strings, does not execute automatically
- `ros2_readonly_validator.py`: topic discovery via subprocess, graceful fallback if ROS2 unavailable

### Filesystem Mutation Paths

- Profile exporters (`profile_exporter.py`): writes JSON/Markdown
- Field session creators: create directories, write configs, CSVs
- Script outputs: all scripts write to `outputs/` or `data/`
- No destructive filesystem operations detected

### Stale or Historical-Only Paths

1. `docs/` files for completed milestones (M0-M8, M13-M17) — historical record, not stale
2. `paper/` directory — paused, not stale
3. `reports/dummy_measurement_report.md` — example artifact, not stale
4. `config/experiment_forward_v0.yaml` — M8 legacy config, may be superseded

### Files with Ambiguous Role

1. `copilot-instructions.md` — expected at workspace root but not found in package directory
2. `docs/modules/` — recently added untracked files, purpose being established
3. `templates/` — only 2 template files, limited usage

### Robot-Specific Logic Leaking into Generic Modules

| File | Leaked Concern | Severity |
|---|---|---|
| `calibration_core/compensation_models.py:14` | `SUPPORTED_EMPIRICAL_PLATFORM = "booster_k1"` | Medium |
| `calibration_core/profile_loader.py` | `load_k1_gold_profile()` function | Medium |
| `calibration_core/__init__.py` | Exports `load_k1_gold_profile` | Low |
| `calibration_core/command_adapter.py` | Protocol uses `kWalking` in docstring example | Low |

## Inventory Completeness

The audit covers:

- [x] Python packages and modules
- [x] Command-line entry points (scripts)
- [x] Configuration files
- [x] JSON/YAML schemas
- [x] Test structure
- [x] Generated outputs
- [x] Raw and processed datasets
- [x] Physical execution paths
- [x] K1 SDK import locations
- [x] Command-sending functions
- [x] Telemetry acquisition paths
- [x] Safety configuration and provenance paths
- [x] Calibration model code
- [x] Compensation code
- [x] Profile registries
- [x] Repository documentation
- [x] Packaging metadata
- [x] CI configuration (none found)
- [x] Dependency files
- [x] Duplicated or conflicting constants
- [x] Implicit defaults
- [x] Robot-specific logic leaking into generic modules
- [x] Import-time side effects
- [x] Network side effects
- [x] Filesystem mutation paths
- [x] Stale or historical-only paths
- [x] Files with ambiguous role

For detailed per-file findings, see `outputs/engineering/m26a_repository_audit.json`.
