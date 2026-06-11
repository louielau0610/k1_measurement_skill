# M22-C Offline Velocity Compensator Prototype

M22-C implements a pure offline prototype of the M22-B algorithm, `Conservative Monotonic Segment Inverse Lookup`.

## Scope

The prototype reads measured response data from the Booster K1 gold profile and measurement contract CSV, then returns a structured compensation decision. It does not execute robot hardware, send commands to K1, implement real-time command remapping, or claim physical validation.

## Algorithm Implementation

The prototype:

1. Validates the request.
2. Loads response cells for `booster_k1`.
3. Filters by surface.
4. Detects deadzone and minimum effective actual velocity.
5. Applies the selected risk policy.
6. Builds monotonic response segments from command velocity and mean actual velocity.
7. Rejects deadzone and out-of-range targets by default.
8. Performs piecewise linear inverse interpolation when one valid segment brackets the desired velocity.
9. Returns a structured decision with status, reason, warnings, confidence, and limitations.

## Risk Policies

- `conservative`: accepts reliable cells only and rejects high risk, yaw drift, uncertainty, deadzone, and insufficient evidence.
- `balanced`: accepts reliable and low-risk under-track cells with warnings for moderate yaw drift or uncertainty.
- `permissive`: may return `feasible_but_risky`, but still refuses deadzone and insufficient-evidence cells.

## Deadzone Behavior

Targets below the minimum effective measured actual velocity return `infeasible_deadzone` when extrapolation is disabled. The prototype does not silently increase command velocity to escape the deadzone.

## Non-Monotonic Behavior

The prototype splits response data into monotonic segments. If multiple comparable segments bracket the target and no clear best segment exists, it returns `non_monotonic_ambiguous`.

## Novelty Positioning

The implementation does not claim generic feedforward compensation, inverse-model compensation, deadzone compensation, or velocity tracking as new. The project-specific framing is a measurement-contract-driven, surface-aware, risk-aware, black-box SDK-level compensation framework for legged robots.

Current novelty status: `engineering_novelty_plausible_but_requires_K1_physical_validation`.

## CLI Usage

```bash
python scripts/offline_compensate_velocity.py --platform booster_k1 --surface S1_lab_hard_floor --desired-velocity 0.40
```

Optional flags:

- `--risk-policy conservative|balanced|permissive`
- `--profile outputs/real_k1_validation_m19/k1_gold_profile_v1.json`
- `--contract-csv outputs/measurement_v1/booster_k1_measurements_contract_v1.csv`
- `--output path/to/decision.json`

Batch sweep:

```bash
python scripts/batch_offline_compensation_sweep.py --platform booster_k1 --surface S1_lab_hard_floor
```

Default batch outputs:

- `outputs/compensation_research/offline_k1_compensation_sweep.csv`
- `outputs/compensation_research/offline_k1_compensation_sweep.json`
- `outputs/compensation_research/offline_k1_compensation_sweep.md`

## Example Output Fields

The decision includes:

- `recommended_command_velocity_mps`
- `expected_actual_velocity_mps`
- `expected_tracking_error_mps`
- `feasibility_status`
- `reason`
- `warnings`
- `offline_only=true`
- `physical_validation_status=not_started`
- `deployment_ready=false`

## Relation to M22-B

M22-B specified the algorithm and feasibility statuses. M22-C implements the offline decision logic only.

## Why This Is Not K1 Physical Validation

The prototype reads existing measurement artifacts and computes offline decisions. It does not run compensated K1 trials, compare compensated and uncompensated tracking error on hardware, or prove deployment readiness. That belongs to Step 3.
