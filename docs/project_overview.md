# Project Overview

## Purpose

This repository is an engineering-grade velocity calibration toolkit for legged
robot platforms. The current executable `calibration_skill` runtime is
hardware-free by default: mock dry-run support is the user-facing CLI path, and
Booster K1 support includes an explicit fake-runtime test path plus the
M27-D.1 audit-closed vendor binding package. The vendor path is not registered
by default and remains blocked from real execution unless explicit hardware
gates and enable flags are supplied.

## Module Map

- `calibration_skill/domain/`: platform-independent value objects, enums,
  capability records, safety envelopes, telemetry samples, command receipts,
  and structured errors.
- `calibration_skill/ports/`: Protocol interfaces for robot adapters,
  factories, clocks, storage, telemetry, authorization, and emergency stop.
- `calibration_skill/adapters/mock.py`: deterministic mock adapter used by the
  default dry-run service.
- `calibration_skill/adapters/booster_k1/`: K1 fake-runtime adapter skeleton,
  fail-closed hardware gate, and M27-D.1 vendor binding/runtime. Ordinary
  imports do not import direct SDK modules. The authoritative direct modules are
  `B1LocoClient`, `ChannelFactory`, and `RobotMode`; the
  `booster_robotics_sdk_python` package probe is diagnostic only.
- `calibration_skill/skill/`: mock-only service layer and stable CLI manifest.
- `calibration_skill/runtime/dry_run.py`: default mock-only service composition.
- `scripts/`: validation, packaging, release-gate, and historical experiment
  scripts.
- `tests/calibration_skill/`: contract, boundary, adapter, CLI, and release
  tests.

## Safety Rules

- Default CLI/runtime remains mock-only and dry-run-only.
- K1 fake adapter registration is explicit and test-local.
- M27-B K1 config requires `dry_run=true` and rejects `allow_hardware=true`.
- M27-D.1 vendor runtime creation requires a complete, unexpired hardware gate,
  matching robot ID, safety policy ID/hash, `vendor_runtime` adapter mode,
  explicit vendor runtime enablement, explicit hardware execution enablement,
  and direct SDK entry-module discovery before any direct import attempt.
- No Booster SDK import is allowed in ordinary runtime paths.
- Zero command acceptance is not physical stop evidence. Internal
  `SAFE_STOPPED` state is command-derived and cannot satisfy physical
  safe-state verification.
- Health checks are binding readiness checks, not transport communication
  verification.
- `GetMode()` is optional/unverified best effort and must not block binding
  construction or provide physical safe-state evidence.
- No hardware connection, socket, DDS, FastDDS, ROS2, UDP, or physical command
  is part of M27-D.1 validation.
- Gold profiles, raw measurement data, and historical outputs are not modified
  by adapter tests.

## Verification Commands

```powershell
py -3.12 scripts/validate_engineering_artifacts.py
py -3.12 -m compileall calibration_skill calibration_core k1_measurement platforms scripts tests -q
py -3.12 -m pytest tests/calibration_skill -q
py -3.12 scripts/run_tests_hermetically.py -- py -3.12 -m pytest tests/ --tb=no -q
py -3.12 scripts/run_local_release_gate.py --summary outputs/engineering/m27d1_release_gate_summary.json
```

## Documentation Maintenance

When behavior, public contracts, safety boundaries, or workflow commands change,
update this overview plus the relevant `docs/modules/*_implementation.md` and
`docs/modules/*_principles.md` files in the same change.
