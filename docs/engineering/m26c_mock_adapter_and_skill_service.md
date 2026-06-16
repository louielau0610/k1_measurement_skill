# M26-C Mock Adapter and Skill Service

M26-C adds the first executable layer above the M26-B contracts while staying
hardware-free. It introduces only a mock adapter, an explicit adapter registry,
and a deterministic dry-run skill service.

## Implemented Components

- `calibration_skill/adapters/registry.py`: explicit in-memory registration for
  mock adapter factories only. It rejects duplicate registration, unknown
  platforms, real platforms, missing `ConnectionConfig`, and `dry_run=false`.
- `calibration_skill/adapters/mock.py`: strict `MockRobotAdapter` conforming to
  the M26-B `RobotAdapter` port. It simulates connection, preflight, locomotion
  readiness, velocity command receipt, stop, safe-state restore, and deterministic
  telemetry with an injected monotonic clock.
- `calibration_skill/skill/service.py`: deterministic service layer for
  `preflight`, `dry_run_velocity_command`, `dry_run_collect_telemetry`,
  `dry_run_stop`, and `dry_run_end_to_end`.
- `calibration_skill/runtime/dry_run.py`: composition helper that registers only
  the mock adapter and returns a `SkillService`.

## Boundaries

M26-C does not register K1, G1, or GO1 factories. It does not import Booster,
Unitree, ROS2, DDS, UDP, or vendor runtime modules. It does not scan files,
entry points, plugins, or network interfaces. Importing `calibration_skill`
does not register adapters and does not perform I/O.

The mock adapter uses only bench-verified dry-run evidence. No mock capability
is marked `hardware_verified`; acceptance of a mock command explicitly means a
contract-level receipt was generated and does not imply physical movement.

## Failure Injection

`MockFailureConfig` supports deterministic injection for:

- preflight blocker;
- connection failure;
- locomotion transition failure;
- command rejection;
- stale telemetry;
- stop unacknowledged.

Each failure is exposed through structured errors or deterministic rejected
receipts.

## Validation

Focused tests:

- `tests/calibration_skill/test_adapter_registry.py`
- `tests/calibration_skill/test_mock_adapter.py`
- `tests/calibration_skill/test_skill_service.py`
- `tests/calibration_skill/test_dry_run_end_to_end.py`
- `tests/calibration_skill/test_dry_run_audit.py`
- `tests/calibration_skill/test_m26c_architecture_boundaries.py`

The full calibration-skill target validates M26-B contracts plus the M26-C
runtime layer.
