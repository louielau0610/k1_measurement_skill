# Platform Capability Matrix — M26-A

**Date**: 2026-06-15
**Status**: Assessment (no implementation)

## Capability Status Values

| Status | Definition |
|---|---|
| `verified_existing` | Capability exists in repository and has been verified |
| `upstream_documented` | Capability is documented in vendor SDK/reference but not verified |
| `planned` | Capability is planned for future implementation |
| `unsupported` | Capability is explicitly not supported by the platform |
| `unknown` | Capability status cannot be determined without further investigation |
| `requires_hardware_verification` | Capability is implemented but not yet verified on physical hardware |

## Capability Matrix

| Capability | Booster K1 | Unitree G1 | Unitree GO1 |
|---|---|---|---|
| **connect/disconnect** | `verified_existing` | `planned` | `planned` |
| **high-level body velocity command** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **vx (forward velocity)** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **vy (lateral velocity)** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **yaw rate (wz)** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **explicit stop** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **locomotion mode transition** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **robot mode observation** | `verified_existing` | `unknown` | `unknown` |
| **body velocity telemetry** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **pose/odometry telemetry** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **IMU telemetry** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **yaw/heading telemetry** | `verified_existing` | `unknown` | `unknown` |
| **battery telemetry** | `verified_existing` | `unknown` | `unknown` |
| **command acknowledgement** | `verified_existing` | `unknown` | `unknown` |
| **state stream** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **emergency stop mechanism** | `verified_existing` | `upstream_documented` | `upstream_documented` |
| **simulator availability** | `unknown` | `upstream_documented` | `upstream_documented` |
| **dry-run support** | `verified_existing` | `planned` | `planned` |
| **command TTL enforcement** | `planned` | `planned` | `planned` |
| **operator confirmation support** | `verified_existing` | `planned` | `planned` |
| **platform version reporting** | `verified_existing` | `unknown` | `unknown` |
| **firmware version reporting** | `unknown` | `unknown` | `unknown` |

## Platform-Specific Notes

### Booster K1

- **Validation status**: `hardware_validated_reference`
- **SDK**: Booster Robotics SDK
- **Middleware**: Fast-DDS
- **Command sequence**: `kPrepare → kWalking → Move(vx, 0.0, 0.0)`
- **Safe speed maximum**: 0.6 m/s (operator-confirmed)
- **Valid command domain**: [0.35, 0.60] m/s
- **Primary telemetry**: `/odometer_state`
- **Secondary telemetry**: `/low_state.imu_state.rpy`
- **Hardware validated via**: M19C full 72-measurement run
- **Key limitation**: Forward velocity only validated; vy and wz not tested in calibration context

### Unitree G1

- **Validation status**: `scaffold_only`
- **SDK**: Unitree SDK2 / `unitree_sdk2_python`
- **Middleware**: CycloneDDS
- **Adapter status**: All methods raise `NotImplementedError`
- **Key unknowns**: Actual SDK API surface, telemetry topic names, command interface, mode lifecycle
- **No physical verification has been performed**

### Unitree GO1

- **Validation status**: `scaffold_only`
- **SDK**: legacy `unitree_legged_sdk`
- **Communication**: UDP high-level command/state
- **Adapter status**: All methods raise `NotImplementedError`
- **Key unknowns**: UDP protocol details, legacy SDK compatibility, telemetry format
- **No physical verification has been performed**

## Capability Gap Analysis

### Universal Capabilities (all platforms expected to support)

| Capability | K1 | G1 | GO1 | Gap |
|---|---|---|---|---|
| Forward velocity command | ✅ | ❓ | ❓ | G1, GO1 need implementation |
| Body velocity telemetry | ✅ | ❓ | ❓ | G1, GO1 need implementation |
| Explicit stop | ✅ | ❓ | ❓ | G1, GO1 need implementation |
| Emergency stop | ✅ | ❓ | ❓ | G1, GO1 need implementation |

### K1-Specific Advantages

- Hardware-validated reference implementation
- Known safe speed envelope
- Validated telemetry sources
- Proven command sequence
- Gold calibration profile available

### G1 Unknowns (must resolve before implementation)

- Actual SDK API for locomotion control
- CycloneDDS configuration requirements
- Telemetry topic names and message types
- Robot mode lifecycle
- Safety mechanisms (software and hardware)
- Simulator availability and fidelity

### GO1 Unknowns (must resolve before implementation)

- Legacy SDK compatibility with current systems
- UDP protocol details (packet structure, timing)
- Telemetry format and update rate
- Command acknowledgement mechanism
- Safety mechanisms
- Whether the legacy SDK is still maintained

## Physical Verification Requirements

Before any platform can claim `verified_existing` for hardware-dependent
capabilities, the following physical acceptance milestones must be completed:

1. **Bench connection test**: SDK imports, connection established, no errors
2. **Read-only telemetry test**: Telemetry stream verified against known values
3. **Controlled motion test**: Single velocity command in controlled environment
4. **Safety mechanism test**: Emergency stop verified
5. **Full measurement session**: Complete calibration session executed
6. **Profile validation**: Profile built from real data and validated

**No G1 or GO1 claim of `verified_existing` for any hardware capability is
allowed before these milestones are completed.**
