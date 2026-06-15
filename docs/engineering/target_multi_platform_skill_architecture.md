# Target Multi-Platform Skill Architecture — M26-A

**Date**: 2026-06-15
**Status**: Proposed (not implemented)
**Branch**: `engineering/m26a-program-reset-audit`

## Architecture Principles

The target architecture is based on:

1. **Unified domain contracts** — platform-independent value objects and invariants
2. **Platform-specific adapters** — vendor SDK integration in isolated packages
3. **Isolated vendor SDK runtimes** — vendor imports restricted to adapter boundaries
4. **Deterministic calibration/application services** — pure functions on domain objects
5. **Agent-callable skill interfaces** — structured JSON envelope for agent invocation

## Logical Package Structure

```
calibration_skill/
├── domain/              # Pure platform-independent value objects and invariants
├── application/         # Calibration, collection, validation, model fitting, compensation
├── ports/               # Abstract interfaces (hardware, telemetry, storage, clocks, safety)
├── schemas/             # Versioned external input/output contracts
├── runtime/             # Process lifecycle, adapter workers, health, timeouts, IPC, shutdown
├── skill/               # Agent-callable operations and deterministic JSON envelopes
├── cli/                 # Human-facing commands (call same application layer)
└── adapters/
    ├── mock/            # Mock adapter for testing without hardware
    ├── booster_k1/      # Booster K1 adapter (Booster Robotics SDK, Fast-DDS)
    ├── unitree_g1/      # Unitree G1 adapter (Unitree SDK2, CycloneDDS)
    └── unitree_go1/     # Unitree GO1 adapter (legacy unitree_legged_sdk, UDP)
```

## Layer Responsibilities

### Domain (`domain/`)

**Pure platform-independent value objects and invariants.**

Contains:
- Value objects: `VelocityCommand`, `TelemetrySample`, `RobotIdentity`, `CapabilityDescriptor`
- Invariants: velocity ranges, timestamp monotonicity, sequence ordering
- No vendor SDK imports
- No filesystem or network I/O
- No hardware dependencies

Must NOT contain:
- Platform-specific constants
- Vendor SDK imports
- I/O operations
- Configuration loading

### Application (`application/`)

**Calibration, collection, validation, model fitting, compensation orchestration.**

Contains:
- Calibration session orchestration
- Trial planning and scheduling
- Profile construction and validation
- Model fitting algorithms
- Compensation decision logic
- Audit and verification workflows

Must NOT contain:
- Direct vendor SDK imports
- Direct hardware communication
- Platform-specific command sequences

### Ports (`ports/`)

**Abstract interfaces (Protocols/ABCs) for all external dependencies.**

Contains:
- `RobotAdapter` — abstract robot control interface
- `TelemetryStream` — abstract telemetry acquisition
- `StorageBackend` — abstract data persistence
- `MonotonicClock` — abstract time source
- `OperatorAuthorization` — abstract safety confirmation
- `EmergencyStop` — abstract emergency stop mechanism
- `AdapterFactory` — abstract adapter creation

Must NOT contain:
- Concrete implementations
- Vendor SDK imports
- Platform-specific logic

### Schemas (`schemas/`)

**Versioned external input/output contracts.**

Contains:
- JSON Schema definitions for all external artifacts
- Measurement profile schemas
- Calibration dataset schemas
- Session manifest schemas
- Audit record schemas

Must NOT contain:
- Business logic
- Python code beyond schema definitions
- Vendor-specific fields without abstraction

### Runtime (`runtime/`)

**Process lifecycle, adapter workers, health, timeouts, IPC, shutdown.**

Contains:
- Adapter process management
- Health monitoring
- Timeout enforcement
- Inter-process communication (if needed)
- Graceful shutdown orchestration
- Resource cleanup

Must NOT contain:
- Domain logic
- Calibration algorithms
- Vendor SDK imports (except through adapter boundaries)

### Skill (`skill/`)

**Agent-callable operations and deterministic JSON envelopes.**

Contains:
- Agent-facing operation definitions
- Request/response JSON schemas
- Input validation
- Output formatting
- Error serialization

Must NOT contain:
- Direct hardware access
- Vendor SDK imports
- UI/CLI rendering

### CLI (`cli/`)

**Human-facing commands that call the same application layer.**

Contains:
- Command-line entry points
- Argument parsing
- Human-readable output formatting
- Progress reporting

Must NOT contain:
- Direct vendor SDK imports
- Business logic (delegate to application layer)
- Hardware communication (delegate to ports)

### Adapters (`adapters/`)

**Vendor-specific implementations only.**

Contains:
- `mock/` — Mock adapter for testing without hardware
- `booster_k1/` — Booster Robotics SDK, Fast-DDS, K1 motion lifecycle
- `unitree_g1/` — Unitree SDK2, CycloneDDS, G1 locomotion client
- `unitree_go1/` — legacy unitree_legged_sdk, UDP high-level command/state

Must:
- Implement ports interfaces
- Contain ALL vendor SDK imports
- Be the ONLY place vendor SDKs are imported
- Support dry-run/mock modes
- Validate safety envelopes before command execution

Must NOT:
- Export vendor types to other layers
- Be imported by domain, application, schemas, skill, or generic CLI modules

## Import Rules

### Allowed

```
domain → (nothing external)
ports → (nothing external)
schemas → (nothing external)
application → domain, ports, schemas
runtime → ports, domain
skill → application, ports, domain
cli → application, ports, domain
adapters/* → ports, domain, vendor SDKs
```

### Prohibited

```
domain → vendor SDK          ❌
application → vendor SDK     ❌
schemas → vendor SDK         ❌
skill → vendor SDK           ❌
cli (generic) → vendor SDK   ❌
application → adapters/*     ❌ (use ports)
domain → adapters/*          ❌
```

## Mapping from Current Structure

| Current Location | Target Location | Notes |
|---|---|---|
| `calibration_core/measurement_schema.py` | `domain/` | Value objects |
| `calibration_core/measurement_contract.py` | `schemas/` | External contracts |
| `calibration_core/command_adapter.py` | `ports/` | Abstract interface |
| `calibration_core/state_logger.py` | `ports/` | Abstract interface |
| `calibration_core/measurement_extractor.py` | `ports/` | Abstract interface |
| `calibration_core/platform_registry.py` | `ports/` or `runtime/` | Adapter registry |
| `calibration_core/trial_scheduler.py` | `application/` | Trial planning |
| `calibration_core/measurement_pipeline.py` | `application/` | Orchestration |
| `calibration_core/response_analyzer.py` | `application/` | Analysis |
| `calibration_core/compensation_models.py` | `application/` or `domain/` | Compensation logic |
| `calibration_core/compensation_policies.py` | `application/` | Policy engine |
| `calibration_core/compensation_verification.py` | `application/` | Verification |
| `calibration_core/velocity_compensation.py` | `application/` | Compensation |
| `calibration_core/revised_velocity_compensation.py` | `application/` | Compensation |
| `calibration_core/profile_exporter.py` | `application/` or `schemas/` | Export |
| `calibration_core/profile_loader.py` | `application/` | Loading (parameterize K1 path) |
| `calibration_core/risk_classifier.py` | `application/` | Risk analysis |
| `calibration_core/measurement_manifest.py` | `schemas/` | Manifest schema |
| `calibration_core/measurement_contract_mapping.py` | `schemas/` | Schema migration |
| `platforms/booster_k1/*` | `adapters/booster_k1/` | K1 adapter |
| `platforms/unitree_g1/*` | `adapters/unitree_g1/` | G1 adapter |
| `platforms/unitree_go1/*` | `adapters/unitree_go1/` | GO1 adapter |
| `k1_measurement/command_runner.py` | `adapters/booster_k1/` or `runtime/` | K1 command |
| `k1_measurement/field_logging.py` | `adapters/booster_k1/` | K1 telemetry |
| `k1_measurement/ros2_readonly_validator.py` | `adapters/booster_k1/` | K1 discovery |
| `k1_measurement/metrics.py` | `domain/` or `application/` | Pure metrics |
| `k1_measurement/visualization.py` | `application/` | Visualization |
| `k1_measurement/full_range_velocity_profile.py` | `application/` | M25 profiling |
| `k1_measurement/m25_real_collection_preflight.py` | `application/` | Preflight |

## Upstream Integration Families

### Booster K1

- **SDK**: Booster Robotics SDK
- **Middleware**: Fast-DDS
- **Communication**: Platform-specific motion mode lifecycle
- **Command path**: `kPrepare → kWalking → Move(vx, 0.0, 0.0)`
- **Telemetry**: `/odometer_state`, `/low_state.imu_state.rpy`
- **Setup**: `source /opt/booster/BoosterRos2Interface/install/setup.bash`

### Unitree G1

- **SDK**: Unitree SDK2 / `unitree_sdk2_python`
- **Middleware**: CycloneDDS
- **Communication**: G1-specific locomotion client, G1/H1-2 IDL family
- **Telemetry**: TBD (to be determined during adapter implementation)
- **Setup**: TBD

### Unitree GO1

- **SDK**: legacy `unitree_legged_sdk`
- **Communication**: UDP high-level command/state loop
- **Command structure**: Platform-specific command and state structures
- **Telemetry**: TBD
- **Setup**: TBD

## Design Decisions

1. **Python Protocols over ABCs** for abstract interfaces (lighter weight, better IDE support)
2. **Function-scoped vendor imports** in adapter modules (import only when needed)
3. **Subprocess isolation** for vendor SDK runtimes where in-process import is problematic
4. **Fail-closed defaults** for all hardware operations
5. **Immutable domain objects** where practical (`@dataclass(frozen=True)`)
