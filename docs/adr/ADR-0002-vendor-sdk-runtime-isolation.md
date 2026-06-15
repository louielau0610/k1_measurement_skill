# ADR-0002: Vendor SDK Runtime Isolation

**Status**: Accepted
**Date**: 2026-06-15
**Milestone**: M26-A

## Context

The calibration skill must support three platforms with three distinct vendor
SDKs:

1. **Booster K1**: Booster Robotics SDK (Python, in-process)
2. **Unitree G1**: Unitree SDK2 / `unitree_sdk2_python` (Python, in-process)
3. **Unitree GO1**: legacy `unitree_legged_sdk` (C++ with Python bindings, UDP)

These SDKs have different dependencies, middleware requirements (Fast-DDS,
CycloneDDS, raw UDP), and may conflict when installed in the same Python
environment. The core calibration logic must remain importable and testable
without any vendor SDK installed.

The current K1 adapter imports Booster SDK at function scope, which works for a
single platform but does not address potential conflicts with other SDKs.

## Decision

We will adopt **lazy function-scoped vendor SDK imports within adapter
boundaries**, with the option to escalate to **subprocess isolation** for
platforms where in-process co-existence is problematic.

The default strategy is:

1. **Adapter modules import vendor SDKs at function scope** (not module level)
2. **Import errors are caught and reported as "platform unavailable"**
3. **No vendor SDK is imported by domain, application, schemas, skill, or CLI modules**

If runtime conflicts arise between SDKs (e.g., DDS middleware conflicts), we
will escalate to subprocess isolation for the conflicting adapter.

## Alternatives Considered

### A. Direct in-process imports (current K1 approach)
- **Accepted as default**: Works for single-platform use. Simple, debuggable.
  Function-scoped imports prevent import-time failures when SDK is missing.
- **Limitation**: May cause conflicts if two SDKs compete for DDS middleware or
  network resources.

### B. Python subprocess workers
- **Accepted as escalation path**: Each adapter runs in its own Python process.
  Communication via pipes, shared memory, or local sockets.
- **When to use**: If SDKs cannot co-exist in the same process (DDS conflicts,
  DLL conflicts, Python version requirements).
- **Cost**: Increased complexity, serialization overhead, process management.
- **Not selected as default**: Unnecessary complexity for the common
  single-platform case.

### C. Native sidecar executables
- **Rejected for now**: Each platform would require a compiled sidecar (C++,
  Rust, Go). Too heavy for three platforms. Revisit if latency or reliability
  requirements demand it.

### D. ROS2 bridges
- **Rejected for now**: Adds ROS2 as a dependency for all platforms. K1 already
  uses ROS2 for telemetry, but G1 uses CycloneDDS natively and GO1 uses raw UDP.
  A ROS2 bridge would add unnecessary middleware complexity.

### E. Network services (REST/gRPC)
- **Rejected for now**: Adds network stack dependency. Latency and reliability
  concerns for real-time command execution. Overhead for local development.

## Consequences

### Positive
- Core package remains lightweight with no vendor dependencies
- Each adapter can be developed and tested in isolation
- SDK conflicts are contained to adapter boundaries
- Graceful degradation when a platform's SDK is not installed

### Negative
- Subprocess isolation (if needed) adds IPC complexity
- Debugging across process boundaries is harder
- Serialization of complex telemetry objects across processes has overhead

## Migration Impact

- Refactor existing K1 adapter to use function-scoped imports consistently
- Add adapter availability check that does not import SDKs
- Define clear IPC protocol for subprocess isolation (if needed later)
- Test that core imports succeed with no vendor SDKs installed

## Validation Requirements

- `import calibration_core` must succeed with no vendor SDKs installed
- `import calibration_core` must succeed with only one vendor SDK installed
- Adapter creation must fail gracefully when SDK is missing
- If subprocess isolation is implemented: round-trip latency < 10ms for commands
