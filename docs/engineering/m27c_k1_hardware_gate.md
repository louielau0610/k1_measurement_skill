# M27-C K1 Hardware Gate

`BoosterK1HardwareGate` is a future real-runtime precondition model. It is not
an enable switch by itself. M27-C still rejects real runtime creation even when a
gate looks complete.

Required explicit fields:

- `allow_hardware`
- `operator_confirmed_hardware`
- `hardware_session_id`
- `safety_policy_id`
- `safety_policy_hash`
- `expected_robot_id`
- `expected_adapter_mode`
- `require_physical_estop_confirmation`
- `require_clear_test_area_confirmation`
- `require_battery_state_confirmation`
- `require_network_isolation_confirmation`
- `require_manual_operator_present`
- `evidence_reference`
- `expires_monotonic_ns`

Validation requires an explicit `now_ns`. The gate is invalid when expired,
missing evidence, missing any confirmation, or mismatched against the requested
robot ID, safety policy, or vendor adapter mode.

M27-C uses the gate only to prove future hardware gating can be represented and
tested. It does not allow real K1 startup.
