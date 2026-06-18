# M27-D: K1 Zero-Motion Bench Procedure

## Purpose

Manual bench procedure for validating the isolated Booster K1 SDK binding
with zero-motion commands only. No nonzero velocity may be commanded.

## Prerequisites

1. Booster K1 robot physically present
2. Physical E-stop confirmed functional
3. Test area cleared of personnel and obstacles
4. Battery state adequate for bench session
5. Network isolated (no external connectivity)
6. Manual operator present throughout

## CLI Arguments

```bash
py -3.12 scripts/run_m27d_k1_zero_motion_bench.py \
  --robot-id K1_001 \
  --hardware-session-id m27d-bench-001 \
  --safety-policy-id m27d-zero-motion-policy \
  --safety-policy-hash <POLICY_HASH> \
  --evidence-reference m27d-bench-YYYY-MM-DD \
  --gate-expiry-monotonic-ns <EXPIRY_NS> \
  --output-dir outputs/engineering/m27d_bench_results \
  --operator-confirmed-hardware \
  --physical-estop-confirmed \
  --clear-test-area-confirmed \
  --battery-state-confirmed \
  --network-isolation-confirmed \
  --manual-operator-present \
  --enable-vendor-runtime \
  --execute-hardware
```

All `--*-confirmed` flags default to `False`. No confirmation may default to `True`.

## Sequence

1. Validate arguments and construct hardware gate
2. Validate gate (expiry, robot ID, policy match, confirmations)
3. Detect SDK without importing (via `importlib.util.find_spec`)
4. Check `--execute-hardware` flag
5. Import verified SDK (`booster_robotics_sdk_python`)
6. Construct vendor binding (`BoosterK1VendorBinding.create_with_sdk_import()`)
7. Construct vendor runtime
8. Connect to robot (`ChannelFactory.Init`, `B1LocoClient.Init`)
9. Read identity metadata
10. Read initial motion state
11. Read robot state
12. Read odometry (if available)
13. Read battery state (if available)
14. Run health check
15. Issue explicit stop/zero command (`Move(0.0, 0.0, 0.0)`)
16. Verify non-moving/safe state
17. Restore safe state
18. Disconnect
19. Write immutable result artifacts

Steps 17-18 are in a `try/finally` block to ensure cleanup.

## Artifacts

Output directory receives:
- `m27d_manifest.json` — Session metadata
- `m27d_gate_evidence.json` — Gate configuration evidence
- `m27d_sdk_detection.json` — SDK detection results
- `m27d_runtime_trace.jsonl` — Sequenced trace events
- `m27d_telemetry_snapshot.json` — Telemetry snapshot
- `m27d_result_summary.json` — Final result summary

## Result Statuses

| Status | Meaning |
|--------|---------|
| `not_executed` | Bench not attempted |
| `blocked_by_gate` | Hardware gate validation failed |
| `sdk_unavailable` | SDK not discoverable |
| `sdk_import_failed` | SDK import error |
| `binding_construction_failed` | Binding/runtime construction error |
| `connection_failed` | Robot connection error |
| `read_only_checks_failed` | Telemetry/state read errors |
| `stop_unacknowledged` | Stop command not acknowledged |
| `safe_state_unverified` | Robot not in safe state after stop |
| `bench_passed` | All checks passed |

## Safety Notes

- M27-D forbids all nonzero velocity commands
- `Move(0.35, 0.0, 0.0)` through `Move(0.60, 0.0, 0.0)` are blocked
- Physical E-stop must remain accessible throughout
- Operator must be prepared to use physical E-stop
- Do not enter walking mode unless required for stop command issuance
