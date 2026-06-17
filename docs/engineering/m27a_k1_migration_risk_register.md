# M27-A K1 Migration Risk Register

**Milestone**: M27-A
**Date**: 2026-06-17
**Status**: Planning Only

## Summary

| Severity | Count |
|----------|-------|
| High | 4 |
| Medium | 9 |
| Low | 2 |
| **Total** | **15** |

## Blocking Risks (for M27-C)

### RISK-003: K1 Mode Lifecycle Uncertainty (HIGH)
SDK `RobotMode` enum values and valid transitions not fully documented. `kPrepare`/`kWalking` sequence may have undocumented requirements.
- **Mitigation**: Replicate exact legacy sequence; hardware-gated lifecycle test
- **Blocks**: M27-C hardware integration

### RISK-012: Stop Acknowledgement Uncertainty (HIGH)
Legacy stop sends `Move(0,0,0)` but does not verify robot actually stopped.
- **Mitigation**: Telemetry-based stop verification; check velocity near zero after stop
- **Blocks**: M27-C hardware integration

## High Severity Risks

| ID | Risk | Likelihood |
|----|------|-----------|
| RISK-001 | SDK environment mismatch | Medium |
| RISK-003 | K1 mode lifecycle uncertainty | Medium |
| RISK-012 | Stop acknowledgement uncertainty | Medium |
| RISK-013 | Import-time vendor side effects | Low |
| RISK-014 | Package dependency contamination | Low |

## Medium Severity Risks

| ID | Risk | Mitigation |
|----|------|-----------|
| RISK-002 | FastDDS configuration | Use existing setup.bash sourcing |
| RISK-004 | Command frame ambiguity | Document body frame assumption |
| RISK-005 | Odometry frame ambiguity | Use relative frame from trial start |
| RISK-006 | Yaw drift variability | Capture in telemetry; flag anomalies |
| RISK-008 | Profile/environment mismatch | M24 profile refresh workflow |
| RISK-009 | Battery/state missing data | Operator checklist; telemetry requirements |
| RISK-010 | Operator confirmation bypass | Hash into audit trail |
| RISK-011 | Stale telemetry | Message age check in TelemetryStream |
| RISK-015 | Windows vs Ubuntu divergence | Subprocess sidecar; platform-specific tests |

## Low Severity Risks

| ID | Risk | Mitigation |
|----|------|-----------|
| RISK-007 | Speed deadband (0.20 m/s) | Document deadband; enforce minimum velocity |
| RISK-014 | Package dependency contamination | Optional extra [booster_k1] |
