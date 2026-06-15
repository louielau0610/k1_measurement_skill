# ADR-0001: Unified Domain Contracts and Platform Adapters

**Status**: Accepted
**Date**: 2026-06-15
**Milestone**: M26-A

## Context

The repository has evolved through 25+ milestones focused on Booster K1 velocity
measurement and compensation. It now needs to support three distinct platforms
(Booster K1, Unitree G1, Unitree GO1) spanning two morphology classes (biped
humanoid, quadruped). The current architecture has platform-specific logic
leaking into generic core modules (e.g., `SUPPORTED_EMPIRICAL_PLATFORM =
"booster_k1"` in `calibration_core/compensation_models.py`, K1 gold profile
path hardcoded in `calibration_core/profile_loader.py`).

Without an explicit architectural boundary between domain logic and platform
implementations, adding G1 and GO1 support will compound these violations.

## Decision

We will adopt an architecture based on:

**Unified domain contracts** — Platform-independent value objects, invariants,
and abstract interfaces defined in a `domain/` and `ports/` layer.

**Platform-specific adapters** — Each platform's vendor SDK integration is
isolated in its own adapter package under `adapters/`.

The domain layer will contain pure value objects (e.g., `VelocityCommand`,
`TelemetrySample`, `RobotIdentity`) with no vendor SDK imports, no I/O, and no
platform-specific constants.

The ports layer will define abstract interfaces (Protocols) for all external
dependencies: `RobotAdapter`, `TelemetryStream`, `MonotonicClock`,
`OperatorAuthorization`, `EmergencyStop`.

Adapters will implement ports interfaces and contain ALL vendor SDK imports.

## Alternatives Considered

### A. Single codebase with if/else platform branching
- **Rejected**: Does not scale beyond 2-3 platforms. Makes testing harder.
  Vendor SDK imports become entangled with domain logic.

### B. Separate repositories per platform
- **Rejected**: Duplicates domain logic, contracts, and application code.
  Makes cross-platform calibration consistency hard to guarantee.

### C. Plugin architecture with dynamic discovery
- **Deferred**: Adds complexity. The adapter registry pattern is sufficient for
  three platforms. Revisit if the platform count grows beyond ~5.

## Consequences

### Positive
- Clear separation of concerns: domain logic is testable without any hardware SDK
- New platforms can be added by implementing ports interfaces only
- Vendor SDK updates affect only the relevant adapter
- Mock adapter enables full pipeline testing without hardware

### Negative
- Initial refactoring cost to extract K1-specific logic from core modules
- Protocol-based interfaces add abstraction overhead
- Adapter registry must handle import errors gracefully

## Migration Impact

- `calibration_core/compensation_models.py`: Replace `SUPPORTED_EMPIRICAL_PLATFORM` with registry lookup
- `calibration_core/profile_loader.py`: Move `load_k1_gold_profile()` to K1 adapter
- `calibration_core/__init__.py`: Remove K1-specific exports
- `calibration_core/platform_registry.py`: Already follows this pattern; preserve
- All `platforms/` packages: Migrate to `adapters/` with updated imports

## Validation Requirements

- All existing K1 tests must pass after migration
- Core package must be importable with no vendor SDK installed
- Mock adapter must exercise the full pipeline
- No regressions in K1 measurement or compensation workflows
