# Booster K1 Adapter Principles

## Intent

M27-B creates a safe landing zone for future K1 migration work without enabling
real K1 operation. M27-C adds the real-vendor boundary as a fail-closed
placeholder. Together they prove the new `RobotAdapter` contract can represent
K1 lifecycle, command, safety, identity, capability, telemetry, SDK detection,
and hardware-gate concepts without enabling physical execution.

## Non-Goals

- No real Booster SDK import.
- No vendor runtime implementation.
- No hardware connection or physical command.
- No default CLI/runtime K1 availability.
- No real vendor runtime construction in M27-C.
- No G1 or GO1 implementation.
- No hardware verification claim.

## Invariants

- `dry_run` must be true.
- `allow_hardware` must be false.
- Runtime mode must be `fake_booster_runtime`.
- Vendor runtime mode is `vendor_runtime_placeholder` and remains unavailable.
- `BoosterK1HardwareGate` requires explicit confirmations and explicit `now_ns`.
- Velocity limits and timeouts are explicit, finite, and non-negative.
- Legacy K1 M27-B command support is forward-only: `Move(vx, 0.0, 0.0)`.
- Command acceptance means fake runtime receipt only, never physical motion.
- Missing fake telemetry is marked with a quality flag instead of fabricating
  pose or body twist.
- Registration is explicit through `register_booster_k1_fake_adapter`; import
  side effects must not register K1.
- Vendor registration is explicit through `register_booster_k1_vendor_adapter`,
  and still raises structured unavailable errors.

## Failure Modes

Preflight can fail for hardware gate, unsupported runtime mode, or fake runtime
health. Commands can be rejected for disconnected state, wrong lifecycle state,
expired TTL, unsupported `vy`/`wz`, safety envelope violation, missing or stale
operator authorization, or fake runtime rejection. Stop can return a structured
unacknowledged receipt.

Vendor runtime creation can fail for missing gate, incomplete gate, expired
gate, SDK unavailable, runtime disabled by policy, or runtime not implemented.
All failures serialize through `DomainError` without traceback payloads.

## Extension Rules

Real Booster SDK integration belongs behind `vendor_runtime.py`, and only after
M27-D defines the bench validation flow. New real-runtime code must remain
outside import-time paths and must not change the default mock-only CLI
registration.

## Verification

Use the M27-B targeted tests, full `tests/calibration_skill`, the engineering
artifact validator, the hermetic full suite, and the local release gate before
claiming readiness beyond fake-runtime-only.

## M27-D.1 Principles

- The package probe `booster_robotics_sdk_python` is diagnostic only.
- Authoritative direct SDK dependencies are `B1LocoClient.B1LocoClient`,
  `ChannelFactory.ChannelFactory`, and `RobotMode.RobotMode`.
- Direct SDK imports must occur only after complete hardware gate validation,
  adapter mode `vendor_runtime`, explicit vendor runtime enablement, explicit
  hardware execution enablement, and direct-module discovery.
- Missing hardware gates, policy mismatches, and authorization/configuration
  failures must not be reported as SDK unavailable.
- Zero command acceptance never proves physical stopping and must not move the
  lifecycle to `MOVING`.
- Internal `SAFE_STOPPED` is command-derived software state. Physical safe-state
  verification requires independent post-command telemetry.
- Health checks without a verified SDK communication operation are binding
  readiness checks with `communication_verified=false`.
- `GetMode()` is optional/unverified best effort until repository evidence
  proves the exact method and behavior.
