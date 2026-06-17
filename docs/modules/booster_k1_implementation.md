# Booster K1 Adapter Implementation

## Responsibility

`calibration_skill/adapters/booster_k1/` contains the M27-B Booster K1
fake-runtime adapter skeleton. It conforms to the existing M26-B/M26-C contracts
without importing the real Booster SDK or registering K1 in the default runtime.

## Public Files And Symbols

- `calibration_skill/adapters/booster_k1/config.py`: `_require_non_empty` line
  14, `_require_finite_non_negative` line 19, `BoosterK1AdapterConfig` line 27,
  `BoosterK1AdapterConfig.__post_init__` line 46,
  `BoosterK1AdapterConfig.to_safety_envelope` line 77.
- `calibration_skill/adapters/booster_k1/capabilities.py`: `_supported` line 38,
  `_unsupported` line 49, `_unknown` line 59, `booster_k1_capabilities` line 69.
- `calibration_skill/adapters/booster_k1/identity.py`: `booster_k1_identity`
  line 14, `_optional_str` line 40.
- `calibration_skill/adapters/booster_k1/runtime.py`:
  `BoosterK1RuntimeHealth` line 15, `BoosterK1RuntimeCommandReceipt` line 22,
  `BoosterK1RuntimeOdometry` line 30, `BoosterK1RuntimeState` line 43,
  `BoosterK1RuntimeProtocol` line 52.
- `calibration_skill/adapters/booster_k1/adapter.py`: `BoosterK1Adapter` line
  44, `__post_init__` line 56, `identity` line 65, `capabilities` line 69,
  `connection_state` line 73, `motion_state` line 77,
  `configure_command_context` line 80, `connect` line 90, `disconnect` line 95,
  `preflight` line 100, `enter_locomotion_ready` line 138,
  `send_velocity_command` line 146, `stop` line 174,
  `restore_safe_state` line 197, `collect_telemetry_sample` line 201,
  `_command_rejection_error` line 243, `_rejected_receipt` line 279,
  `_check` line 290.
- `calibration_skill/adapters/booster_k1/registry.py`:
  `register_booster_k1_fake_adapter` line 16, inner `create` line 24,
  `_config_from_connection` line 37.
- `tests/calibration_skill/fakes/fake_booster_k1_runtime.py`:
  `FakeBoosterK1FailureConfig` line 16, `FakeBoosterK1Runtime` line 25,
  `connect` line 66, `enter_prepare_mode` line 93,
  `enter_walking_mode` line 98, `send_body_velocity` line 103, `stop` line
  112, `restore_safe_state` line 121, `read_odometry` line 126,
  `read_robot_state` line 132, `read_battery_state` line 136,
  `health_check` line 140.

## Data Flow

`BoosterK1AdapterConfig` is converted to a `SafetyEnvelope`. The adapter is
constructed with an injected `BoosterK1RuntimeProtocol`, reads optional identity
metadata, and starts disconnected. `connect` and `disconnect` delegate to the
runtime. `enter_locomotion_ready` calls prepare mode and then walking mode.
`send_velocity_command` validates connection state, lifecycle state, expiry,
forward-only K1 axis support, safety envelope, and operator authorization before
calling `send_body_velocity(vx, 0.0, 0.0)`.

Telemetry normalization reads fake robot state, fake odometry, and optional fake
battery data, then produces a platform-independent `TelemetrySample`.

## Tests

The implementation is covered by `tests/calibration_skill/test_booster_k1_*.py`
and the fake runtime in `tests/calibration_skill/fakes/`.
