# M26-A — Engineering Program Reset

**Status**: Active
**Milestone**: M26-A
**Date**: 2026-06-15
**Type**: Engineering Reset, Architecture Freeze, Documentation

## Purpose

M26-A pauses all non-engineering experimental branches of work and reframes the
repository as an **engineering-grade, agent-callable legged robot velocity
calibration skill** with explicitly scoped target platforms.

## Primary Deliverable

The primary deliverable is now an **engineering-grade calibration skill**
supporting:

1. **Booster K1** — biped humanoid (hardware-validated reference)
2. **Unitree G1** — biped humanoid (scaffold only)
3. **Unitree GO1** — quadruped (scaffold only)

The architecture targets these three named platforms and represents two
morphology classes:

- Biped humanoid (K1, G1)
- Quadruped (GO1)

The repository does **not** claim universal support for all legged robots.

## Explicit Non-Goals

M26-A is **documentation, inventory, architecture, and migration planning only**.

It must **not**:

- Connect to any robot
- Send any motion command
- Install Booster or Unitree SDKs
- Perform physical tests
- Alter the current gold calibration profile
- Change compensation model behavior
- Move large groups of existing source files
- Delete historical data or artifacts
- Claim that G1 or GO1 support is implemented
- Break any existing K1 workflow

## Paused Work

The following work streams are **paused** as of M26-A:

| Work Stream | Status | Rationale |
|---|---|---|
| M25 exploration data collection | Paused | Awaiting operator-controlled real-robot procedure |
| M25 formal profile data collection | Paused | Blocked until exploration data reviewed |
| M26 full-range monotonic response model comparison | Paused | Requires real formal profile data |
| M27 inverse velocity compensation implementation | Paused | Requires M26 completion |
| M28 full-range direct-vs-compensated validation | Paused | Requires M27 completion |
| Yaw drift / yaw compensation research | Paused | Removed from active M25 objectives |
| Deadzone estimation and modeling | Abandoned | Explicitly removed from roadmap |
| Paper/manuscript work (P-series) | Paused | All paper branches frozen |
| Online yaw adjustment | Paused | Deferred |
| Physical compensation experiments | Paused | M23 negative result; requires revised approach |

## Distinction Between Support Levels

The architecture defines three distinct levels of platform support:

### Architecture Support

A platform has **architecture support** when:

- A platform entry exists in the registry
- Abstract adapter interfaces are defined
- Placeholder/scaffold adapters exist
- The platform appears in the capability matrix with documented status

This does **not** imply the adapter can control the robot.

### Bench Verification

A platform has **bench verification** when:

- The adapter imports the correct vendor SDK
- Unit tests pass with mock telemetry
- Dry-run pipeline exercises the adapter without hardware
- Schema validation passes for the platform's output contracts

This does **not** imply physical hardware validation.

### Physical Hardware Verification

A platform has **physical hardware verification** when:

- The adapter has been tested on the physical robot
- Command execution has been validated in a controlled environment
- Telemetry acquisition has been verified against ground truth
- At least one complete measurement session has been executed
- Safety limits have been confirmed by an operator

**No G1 or GO1 readiness claim is allowed before physical acceptance milestones.**

## Existing K1 Datasets

All existing K1 datasets and results remain **historical evidence** and must
**not** be rewritten. This includes:

- M19C full 72-measurement run
- M19 repeated validation datasets
- M23-B/C physical compensation experiment results (including negative result)
- M24 S2 profile refresh datasets
- M24-H controlled S2 replication datasets
- K1 gold profile (`outputs/real_k1_validation_m19/k1_gold_profile_v1.json`)
- All raw and processed measurement sessions under `data/`

## Target Architecture Principles

The target architecture is based on:

1. **Unified domain contracts** — platform-independent value objects, invariants, and interfaces
2. **Platform-specific adapters** — vendor SDK integration in isolated adapter packages
3. **Isolated vendor SDK runtimes** — vendor imports restricted to adapter boundaries
4. **Deterministic calibration/application services** — pure functions operating on domain objects
5. **Agent-callable skill interfaces** — structured JSON envelope for agent invocation

The core package must remain importable and testable **without any vendor SDK installed**.

## Validation Policy

Before any implementation milestone beyond M26-A:

- All existing K1 workflows must continue to function
- No hardware SDK shall be required to run the unit test suite
- No robot connection or command shall be attempted by non-adapter code
- The readiness tracker shall accurately reflect implementation status
