# M23-E Revised Offline Compensator

## Status

M23-E implements a revised offline compensator. It does not execute hardware, does not claim physical validation, does not claim tracking improvement, and does not make the system deployment ready.

## Why Revision Was Needed

M23-C showed that the current M22-C inverse lookup worsened physical K1 tracking on `S2_marble_floor`. Direct commands were already accurate, but the compensator lowered commands and increased error in all 12 pairs.

M23-D diagnosed this as:

- `identity_preferred`
- `compensation_not_beneficial`
- `overcorrection_risk`
- `profile_mismatch_suspected`
- `revision_required`

## Revised Logic

The revised compensator still uses M22-C as a candidate generator, but it no longer blindly accepts the candidate command.

### Identity Fallback

If direct command error is below `direct_error_good_enough_mps`, default `0.02`, the final command remains:

```text
final_command_velocity_mps = desired_actual_velocity_mps
```

The decision status is:

```text
identity_preferred
```

### Benefit Gate

The compensator only accepts a candidate when:

```text
expected_benefit_mps >= minimum_expected_benefit_mps
```

Default:

```text
minimum_expected_benefit_mps = 0.02
```

If the benefit is too small or negative, the decision returns identity with:

```text
compensation_not_beneficial
```

### Correction Magnitude Limit

The revised compensator rejects large command changes by default:

```text
abs(candidate_compensated_command_velocity_mps - desired_actual_velocity_mps) <= max_correction_mps
```

Default:

```text
max_correction_mps = 0.05
```

If the candidate exceeds this limit, default behavior is:

```text
overcorrection_risk
```

Optional clamping is available with `allow_clamping=true`, but it remains offline-only and requires later validation.

### Profile Mismatch Detection

The revised compensator compares old profile-predicted direct behavior with M23-C physical direct behavior. If the difference exceeds `profile_mismatch_threshold_mps`, default `0.03`, it marks:

```text
profile_mismatch_suspected = true
```

This catches the M23-C failure mode where the old response profile predicted that direct command would be poor, but physical direct trials were already accurate.

## M23-C Failure Avoidance

For the M23-C velocities 0.40, 0.45, 0.50, and 0.55 m/s, the revised sweep selected identity for all four target velocities and selected zero harmful M23-C compensated commands.

Artifacts:

- `outputs/compensation_experiments/m23e_revised_compensator_sweep.csv`
- `outputs/compensation_experiments/m23e_revised_compensator_sweep.json`
- `outputs/compensation_experiments/m23e_revised_compensator_report.md`
- `outputs/compensation_experiments/m23e_revised_compensator_summary.json`

## Conservative Boundary

M23-E remains offline-only:

- `physical_validation_status = not_started`
- `deployment_ready = false`
- no GO1/G1 validation
- no navigation improvement claim
- no physical tracking improvement claim

## Next Validation

M23-F or M24 must validate the revised logic before any physical claim:

1. Run offline replay over M23-C results.
2. Generate a revised K1 physical plan.
3. Execute a small K1 revalidation run.
4. Analyze whether identity fallback and benefit-gated compensation preserve or improve tracking.
5. Keep GO1/G1 blocked until revised K1 validation succeeds.
