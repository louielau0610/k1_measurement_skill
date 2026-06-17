# M27-A K1 Compatibility Test Plan

**Milestone**: M27-A
**Date**: 2026-06-17
**Status**: Planning Only — Tests for M27-B/M27-C

## Non-Hardware Tests (12 tests)

All runnable in CI without K1 hardware, SDK, or ROS2.

| ID | Test | Purpose |
|----|------|---------|
| NH-001 | Import boundary | Core imports succeed without SDK; adapter fails gracefully |
| NH-002 | Adapter factory | Factory creates RobotAdapter; dry_run works without SDK |
| NH-003 | Safety config parsing | YAML → SafetyEnvelope; vx_max=0.6 |
| NH-004 | Command mapping | VelocityCommand ↔ legacy parameters |
| NH-005 | Dry-run adapter | Full lifecycle: connect→preflight→command→stop→disconnect (all dry) |
| NH-006 | Fake Booster SDK | Mock SDK classes; verify correct method call order |
| NH-007 | Telemetry normalization | Recorded CSV → TelemetrySample invariants |
| NH-008 | No-vendor install | pip install without [booster_k1] extra; core imports work |
| NH-009 | K1 not auto-registered | AdapterRegistry does not auto-register K1 |
| NH-010 | Safety no silent default | SafetyEnvelope requires explicit values |
| NH-011 | No auto-connect | ConnectionConfig construction triggers no network/SDK |
| NH-012 | Operator auth expiry | Expired authorization rejects commands |

## Hardware-Gated Tests (8 tests)

**ALL excluded from CI**. Require `requires_hardware: true` marker.

| ID | Test | Requirements |
|----|------|-------------|
| HW-001 | Connection preflight | K1 robot, SDK, network, operator |
| HW-002 | Lifecycle transition | K1 robot, SDK, operator, clear floor |
| HW-003 | Bounded velocity command | K1 robot, SDK, ROS2, operator, clear floor |
| HW-004 | Stop acknowledgement | K1 robot, SDK, operator, clear floor |
| HW-005 | Telemetry capture | K1 robot, ROS2 telemetry active |
| HW-006 | Safety rejection | K1 robot, SDK, operator |
| HW-007 | Emergency stop | K1 robot, SDK, operator, e-stop procedure |
| HW-008 | Audit package | K1 robot, full infrastructure |

## CI Policy

```bash
# CI-safe test command (excludes all hardware tests):
py -3.12 -m pytest tests/ -k 'not hardware_gated' -q

# Full suite (robot only):
py -3.12 -m pytest tests/ --tb=no -q
```

All hardware-gated tests must use:
```python
@pytest.mark.hardware_gated
```
