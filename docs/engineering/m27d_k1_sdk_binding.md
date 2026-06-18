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
