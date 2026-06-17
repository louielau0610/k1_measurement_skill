# M27-A K1 Vendor Runtime Isolation Design

**Milestone**: M27-A
**Date**: 2026-06-17
**Status**: Design Recommendation Only — No Implementation

## Problem Statement

The Booster K1 SDK (`booster_robotics_sdk_python`) must not be imported into the new `calibration_skill` core runtime. The legacy code already demonstrates split-process isolation, but the new architecture needs a deliberate isolation strategy.

## Options Evaluated

### 1. Direct In-Process Booster SDK Import

**Pros**: Simplest code path; no IPC overhead
**Cons**: 
- Contaminates core runtime with vendor dependency
- Import fails on any machine without SDK → breaks `import calibration_skill`
- Violates M26-C layering (domain/ports free of vendor imports)
- Packaging would require optional dependency management
**Failure Modes**: ImportError on non-robot machines; version conflicts
**Verdict**: ❌ Rejected — violates core architecture principle

### 2. Subprocess Sidecar (Current Legacy Pattern)

**Pros**:
- Proven pattern (M23-B/M24-B/M24-H already use this)
- SDK process isolated from core runtime
- Core runtime importable without SDK
- Separate Python environments possible (`--sdk-python`, `--sdk-env-setup`)
**Cons**:
- Subprocess management overhead
- Needs synchronization between command and telemetry processes
- Error handling across process boundary
- Windows subprocess quirks
**Failure Modes**: Subprocess crash, zombie process, IPC desync
**Verdict**: ✅ **Recommended for M27-B/M27-C** — mature, proven, preserves isolation

### 3. CLI Wrapper

**Pros**: Simple; SDK accessed only via CLI tool; no Python import dependency
**Cons**:
- Limited programmatic control
- No structured return values (rely on stdout/exit codes)
- Hard to integrate with async adapter protocol
**Failure Modes**: CLI not on PATH; argument parsing mismatch
**Verdict**: ⚠️ Acceptable fallback — simpler but less flexible than subprocess

### 4. Local IPC Service (gRPC/Unix Socket/Named Pipe)

**Pros**:
- Clean API boundary
- Language-agnostic
- Can run as persistent service
**Cons**:
- Complex setup (service management, port allocation)
- Additional dependency (gRPC framework)
- Harder to debug than subprocess
- Windows named pipe vs Unix socket divergence
**Failure Modes**: Service not running; port conflicts; serialization errors
**Verdict**: ⚠️ Future consideration — over-engineered for M27-B

### 5. ROS2 Bridge

**Pros**: Leverages existing ROS2 infrastructure on robot
**Cons**:
- ROS2 dependency in adapter (currently forbidden in calibration_skill)
- Message type dependency on `booster_interface`
- Additional ROS2 node management
- Cannot use on Windows (no ROS2)
**Failure Modes**: ROS2 not running; topic not available; message format change
**Verdict**: ❌ Rejected for M27-B — ROS2 dependency conflicts with vendor-free core

## Recommendation

**Subprocess Sidecar** with the following design:

```
calibration_skill/
  adapters/
    booster_k1/           ← M27-B creates this
      __init__.py
      adapter.py          ← RobotAdapter implementation
      sdk_sidecar.py      ← Subprocess manager for send_m23b_k1_velocity_command.py
      sdk_protocol.py     ← JSON protocol for subprocess I/O
```

### Key Design Rules

1. **Core runtime remains vendor-free**: `calibration_skill/domain/`, `ports/`, `schemas/` never import Booster SDK
2. **Adapter isolates SDK**: Only `calibration_skill/adapters/booster_k1/` may reference SDK paths
3. **No auto-import on construction**: `import calibration_skill` must succeed without SDK
4. **Lazy SDK loading**: SDK only imported when `RobotAdapter.connect()` is called with `dry_run=False`
5. **Dry-run default**: All adapter methods support dry-run without SDK
6. **No hardware path without explicit request**: `--execute` or `dry_run=False` required

### Packaging Implications

- `booster_robotics_sdk_python` is NOT a pip dependency of `calibration-skill`
- Listed as optional extra: `[booster_k1]` if user wants SDK support
- Standard `pip install calibration-skill` remains vendor-free
- Robot-side installation can add `[booster_k1]` extra

### Windows/Ubuntu Considerations

- **Windows**: Core development, testing, dry-run — no SDK, no ROS2
- **Ubuntu (robot)**: SDK + ROS2 available; adapter can use subprocess sidecar
- Subprocess approach handles both: on Windows, adapter reports SDK unavailable gracefully

### Why M27-A Does Not Implement This

M27-A is a planning and boundary milestone only. Implementation begins in M27-B. This document defines the design that M27-B will follow.
