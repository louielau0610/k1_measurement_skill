# M27-B K1 No-Hardware Boundary

M27-B is a no-hardware milestone. It adds a K1 adapter skeleton so future
implementation work has a contract-compatible place to land, but it does not
enable real K1 operation.

Enforced boundaries:

- `BoosterK1AdapterConfig` requires `dry_run=true`.
- `allow_hardware=true` is rejected.
- `BoosterK1Adapter` accepts only `fake_booster_runtime`.
- K1 fake registration is explicit and test-local.
- The default dry-run service still registers only the mock adapter.
- The CLI manifest still marks Booster K1 unavailable in the new runtime.
- Lateral velocity and yaw rate are unsupported in M27-B because M27-A evidence
  covers the legacy forward-only command chain.
- Telemetry is normalized only from fake odometry and fake state.
- Command receipts prove fake runtime acceptance only; they do not imply
  physical movement.

Forbidden in M27-B:

- real Booster SDK imports in ordinary runtime paths
- socket, UDP, DDS, FastDDS, ROS2, or hardware connections
- K1 default runtime registration
- hardware verification claims
- G1 or GO1 implementation

M27-C is the first milestone allowed to introduce a real SDK integration plan
behind a separate, fail-closed runtime boundary.
