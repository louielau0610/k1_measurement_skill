# Revised Velocity Compensator Requirements

## Status

These are M23-D design requirements only. They do not implement a revised compensator and do not authorize hardware execution.

## A. Identity Fallback

If direct command is predicted or observed to be sufficiently accurate, the compensator must return:

```text
recommended_command_velocity = desired_velocity
```

Proposed status label:

```text
identity_preferred
```

The fallback should trigger when expected direct absolute error is below a configured tolerance, or when recent physical evidence shows direct control tracks the target better than compensated control.

## B. Benefit Gate

The compensator should only alter the command when predicted improvement exceeds a minimum threshold.

Example rule:

```text
predicted_direct_error - predicted_compensated_error >= min_expected_improvement_mps
```

If the threshold is not met, return identity and label:

```text
compensation_not_beneficial
```

This prevents blind remapping when the baseline is already good.

## C. Correction Magnitude Limit

Constrain the compensated command:

```text
abs(u_compensated - v_desired) <= max_correction_mps
```

Default suggestion:

```text
max_correction_mps = 0.05
```

The limit should be configurable. If the raw inverse lookup exceeds this bound, clamp it or refuse the compensated command with:

```text
overcorrection_risk
```

## D. Profile Mismatch Detection

If current physical direct results differ substantially from the old response profile, mark:

```text
profile_mismatch_suspected
```

Profile mismatch should block aggressive compensation and require either identity fallback, re-profiling, or a fresh validation run.

## E. Conservative Deployment Status

The revised compensator remains offline until revalidated. It must report:

```text
deployment_ready = false
physical_validation_status = not_started_for_revised_compensator
```

## Proposed Labels

- `identity_preferred`
- `compensation_not_beneficial`
- `overcorrection_risk`
- `profile_mismatch_suspected`
- `revision_required`

These labels are proposed for the next implementation milestone. M23-D documents them but does not implement the revised compensator.
