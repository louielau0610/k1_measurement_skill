# ADR-0004: Capability-Driven Platform Support

**Status**: Accepted
**Date**: 2026-06-15
**Milestone**: M26-A

## Context

The calibration skill targets three platforms with different capabilities,
communication protocols, and maturity levels:

- **Booster K1**: Hardware-validated, full capability set known
- **Unitree G1**: Scaffold only, capabilities based on upstream documentation
- **Unitree GO1**: Scaffold only, capabilities based on upstream documentation

The system must be able to determine at runtime what a connected platform can
and cannot do, and adapt its behavior accordingly. It must not assume
capabilities that have not been verified.

## Decision

We will adopt a **capability-driven platform support** model:

1. **CapabilityDescriptor**: Each platform adapter reports its capabilities
   explicitly via a `CapabilityDescriptor` with enumerated status values.

2. **Explicit capability statuses**:
   - `verified_existing` — tested and confirmed on physical hardware
   - `upstream_documented` — documented by vendor but not verified
   - `planned` — on the implementation roadmap
   - `unsupported` — explicitly not available
   - `unknown` — cannot determine without investigation
   - `requires_hardware_verification` — implemented but not physically tested

3. **Required vs. optional capabilities**: The application layer defines which
   capabilities are required for each operation. Missing required capabilities
   block the operation. Missing optional capabilities allow degraded operation.

4. **No capability assumption**: Unknown capabilities are treated as unavailable
   until verified. The system does not assume a platform supports a feature
   just because similar platforms do.

5. **Verification-gated status upgrades**: Capabilities can only be upgraded to
   `verified_existing` after physical acceptance milestones are completed.

## Alternatives Considered

### A. Assume capabilities based on platform class
- **Rejected**: Different firmware versions, SDK versions, and robot
  configurations may have different capabilities even within the same platform
  family.

### B. Try-and-fail approach (attempt operation, handle errors)
- **Rejected**: Unsafe for motion commands. Could send invalid commands to the
  robot.

### C. Static capability manifest per platform
- **Partially accepted**: A static manifest is the starting point, but the
  adapter must also query the connected robot for dynamic capabilities (e.g.,
  firmware-dependent features).

## Consequences

### Positive
- Clear visibility into what each platform can and cannot do
- Safe handling of platform differences
- No false assumptions about unverified platforms
- Supports gradual capability rollout (add capabilities as they are verified)

### Negative
- More upfront work to define capability taxonomy
- Runtime capability checks add complexity to application logic
- Static manifests may drift from reality if not updated

## Migration Impact

- Define `CapabilityDescriptor` and `CapabilityStatus` in domain layer
- Add `get_capabilities()` to `RobotAdapter` interface
- Populate K1 capabilities from verified existing implementation
- Populate G1 and GO1 capabilities from upstream documentation (with `unknown`
  for unverified items)
- Update preflight to check required capabilities before proceeding

## Validation Requirements

- K1 capability descriptor matches verified implementation
- G1 and GO1 capability descriptors correctly mark all hardware capabilities as
  `unknown` or `upstream_documented` (not `verified_existing`)
- Preflight blocks operations when required capabilities are unavailable
- Capability matrix JSON parses successfully and contains only valid status values
