# M27-D: Booster K1 Isolated SDK Binding

## Overview

M27-D implements the isolated Booster K1 SDK binding needed by
`BoosterK1VendorRuntime`, together with an explicitly hardware-gated,
zero-motion bench validation package.

## Verified SDK Imports

The following SDK imports and API calls are verified by existing
repository code that has operated the real K1 robot:

### Source Files
- `scripts/send_m23b_k1_velocity_command.py`
- `scripts/run_m19c_ros2_odometer_trials.py`

### SDK Entry Points
```python
from booster_robotics_sdk_python import B1LocoClient, ChannelFactory, RobotMode
```

### Verified Motion Sequence
```
ChannelFactory.Instance().Init(0, interface)
client = B1LocoClient()
client.Init()
client.RobotMode(RobotMode.kPrepare)
client.RobotMode(RobotMode.kWalking)
client.Move(vx, 0.0, 0.0)  # repeated at 10 Hz
```

### Verified ROS2 Topics
- `/odometer_state` — `booster_interface/msg/Odometer`
- `/robot_states` — `booster_interface/msg/RobotStatesMsg`
- `/low_state` — `booster_interface/msg/LowState`

## Architecture

```
calibration_skill/adapters/booster_k1/
    vendor_runtime.py     # Runtime backed by injected binding
    vendor_binding.py     # Real SDK binding + factory
    vendor_types.py       # Protocols and types
    adapter.py            # Updated for fake/vendor mode support
    config.py             # Hardware gate + config
    registry.py           # Registration helpers
```

### Vendor Binding Protocol

`BoosterK1VendorBindingProtocol` defines a narrow internal protocol
representing only the SDK operations required by `BoosterK1RuntimeProtocol`.
No raw SDK objects escape through this boundary.

### Construction Order

1. hardware gate exists
2. gate is complete and unexpired
3. robot ID matches
4. safety policy ID and hash match
5. adapter mode is the real vendor mode
6. vendor runtime is explicitly enabled
7. SDK is discoverable (via `importlib.util.find_spec`)
8. explicit SDK import succeeds
9. vendor binding construction succeeds
10. runtime object is returned

No SDK import or object construction occurs before steps 1–6 pass.

## Zero-Motion Enforcement

M27-D is a zero-motion milestone. The runtime rejects any command where:
- `vx_mps != 0.0` (within 1e-9 tolerance)
- `vy_mps != 0.0` (within 1e-9 tolerance)
- `wz_radps != 0.0` (within 1e-9 tolerance)

Error code: `k1_m27d_nonzero_motion_forbidden`

Known K1 velocities 0.35–0.60 m/s are explicitly rejected.

## SDK Isolation

- Importing `calibration_skill` does not import the Booster SDK
- Importing `calibration_skill.adapters.booster_k1` does not import the Booster SDK
- SDK import only occurs inside `BoosterK1VendorBinding.create_with_sdk_import()`
- Default registry remains mock-only
- Default CLI remains mock-only

## Limitations (M27-D)

- Zero-motion only (no nonzero velocity verification)
- No G1/GO1 support
- No compensation or yaw-control verification
- No hardware-motion verification
- Odometry and battery reading via direct SDK is unverified (returns None)
- `control_mode` and `gait_mode` not introduced as mandatory runtime requirements
- Real bench run required to upgrade `k1_zero_motion_bench` to `bench_verified`

## M27-D.1 Audit Closure Corrections

The authoritative SDK runtime dependencies are direct entry modules and classes:

```python
from B1LocoClient import B1LocoClient
from ChannelFactory import ChannelFactory
from RobotMode import RobotMode
```

Repository evidence: `scripts/send_m23b_k1_velocity_command.py:29`,
`:30`, and `:31`. The same script probes
`importlib.util.find_spec("booster_robotics_sdk_python")` at line 65, but that
package probe is diagnostic only and does not prove the direct modules/classes
are available.

M27-D.1 construction order is fail-closed:

1. hardware gate exists
2. gate is complete
3. gate is not expired
4. expected robot ID matches
5. safety policy ID matches
6. safety policy hash matches
7. adapter mode is `vendor_runtime`
8. vendor runtime is explicitly enabled
9. hardware execution is explicitly enabled
10. direct entry modules are discoverable
11. direct imports and class resolution are attempted

Generic zero-velocity dispatch preserves `IDLE` or `LOCOMOTION_READY` and never
sets `MOVING`. Explicit `stop()` records a command-derived internal
`SAFE_STOPPED` state only; it is not independent physical evidence.

Health checks are scoped as `binding_readiness` with
`communication_verified=false`. `GetMode()` is optional/unverified best effort
and cannot be required for binding construction or used as physical safe-state
evidence.

M27-D.1 used no hardware, ran no M27-D hardware bench, verified no nonzero
motion, and leaves default registry/CLI mock-only. No G1/GO1 hardware support
exists.
