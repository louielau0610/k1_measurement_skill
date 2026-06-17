# Booster K1 Adapter Principles

## Intent

M27-B creates a safe landing zone for future K1 migration work without enabling
real K1 operation. The adapter skeleton proves the new `RobotAdapter` contract
can represent K1 lifecycle, command, safety, identity, capability, and telemetry
concepts using only a deterministic fake runtime.

## Non-Goals

- No real Booster SDK import.
- No vendor runtime implementation.
- No hardware connection or physical command.
- No default CLI/runtime K1 availability.
- No G1 or GO1 implementation.
- No hardware verification claim.

## Invariants

- `dry_run` must be true.
- `allow_hardware` must be false.
- Runtime mode must be `fake_booster_runtime`.
- Velocity limits and timeouts are explicit, finite, and non-negative.
- Legacy K1 M27-B command support is forward-only: `Move(vx, 0.0, 0.0)`.
- Command acceptance means fake runtime receipt only, never physical motion.
- Missing fake telemetry is marked with a quality flag instead of fabricating
  pose or body twist.
- Registration is explicit through `register_booster_k1_fake_adapter`; import
  side effects must not register K1.

## Failure Modes

Preflight can fail for hardware gate, unsupported runtime mode, or fake runtime
health. Commands can be rejected for disconnected state, wrong lifecycle state,
expired TTL, unsupported `vy`/`wz`, safety envelope violation, missing or stale
operator authorization, or fake runtime rejection. Stop can return a structured
unacknowledged receipt.

## Extension Rules

Real Booster SDK integration belongs in a future fail-closed module such as
`vendor_runtime.py`, and only after M27-C defines the hardware-gated validation
flow. New real-runtime code must remain outside import-time paths and must not
change the default mock-only CLI registration.

## Verification

Use the M27-B targeted tests, full `tests/calibration_skill`, the engineering
artifact validator, the hermetic full suite, and the local release gate before
claiming readiness beyond fake-runtime-only.
