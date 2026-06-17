# M26-E No-Vendor Runtime Boundary

M26-E keeps the dry-run calibration skill importable and runnable without vendor SDKs or ROS2/DDS runtime modules.

## Forbidden Runtime Imports

The dry-run package must not import:

- Booster SDK modules
- Unitree SDK2 modules
- `unitree_legged_sdk`
- `rclpy`
- CycloneDDS modules
- FastDDS modules

It also must not open application network sockets, start DDS, send UDP, spawn vendor processes, or connect to a robot.

## Verification

M26-E verifies the boundary with:

- source scanning in `scripts/validate_engineering_artifacts.py`
- runtime import guards in `tests/calibration_skill/test_no_vendor_runtime.py`
- release-gate no-vendor smoke command
- CLI smoke tests that run `manifest`, `examples`, `validate`, and `invoke` against mock dry-run requests

The runtime guard replaces Python import handling in a clean process and fails if a forbidden SDK or ROS/DDS module is imported while the CLI imports or invokes `dry_run_end_to_end`.

## Hardware Adapter Boundary

K1 remains `legacy_existing` outside the new dry-run skill runtime. G1 and GO1 remain scaffolded or not started. M26-E does not migrate K1 command behavior, implement G1 or GO1 adapters, or claim runtime support for any physical robot platform.

Future hardware packages should enter through optional extras or separate adapter distributions, each with explicit dependency declarations, fail-closed safety gates, and hardware-specific validation evidence.
