# M23-C K1 Physical Validation Interpretation

## Result

M23-C analyzed the completed Booster K1 physical before/after compensation session:

- Session: `m23b_k1_s2_executable_20260612_121605`
- Surface: `S2_marble_floor`
- Trials: 24
- Complete direct/compensated pairs: 12
- Desired velocities: 0.40, 0.45, 0.50, 0.55 m/s
- Robot-side extraction: 24/24 trials, 0 errors
- Robot-side QC: 16/16 checks passed

The physical result is negative for the current M22-C compensation policy on this surface. Direct commands had lower mean absolute velocity tracking error than compensated commands.

## Evidence Summary

- Mean direct absolute error: 0.00791675 m/s
- Mean compensated absolute error: 0.044004 m/s
- Mean improvement: -0.03608725 m/s
- Mean absolute error reduction: -455.834 percent
- Improved pairs: 0
- Worsened pairs: 12
- Mean yaw drift direct: 0.0 deg
- Mean yaw drift compensated: 0.0 deg

Claim level:

```text
negative_result_requires_compensator_revision
```

## Interpretation

This result weakens the current paper idea if the claim is that the present M22-C inverse lookup already improves physical K1 velocity tracking on S2 marble. The experiment instead shows that the direct command baseline was already very accurate for the executable target range, and the compensated commands under-commanded the robot enough to increase tracking error.

The result is still valuable evidence. It validates the physical measurement, execution, extraction, and paired-analysis pipeline, and it identifies a concrete compensator failure mode: the offline inverse lookup can be harmful when the direct baseline already tracks the desired velocities closely.

## What Can Be Claimed

- One physical Booster K1 before/after experiment on `S2_marble_floor` was executed and analyzed.
- The analyzed M22-C compensated commands worsened velocity tracking error relative to direct commands for the tested S2 target velocities.
- The paired M23-B/M23-C pipeline can detect both improvement and degradation without fabricating measurements.
- The current compensator needs revision before broader validation.

## What Cannot Be Claimed

- Deployment readiness.
- Navigation improvement.
- GO1 or G1 validation.
- Cross-platform physical validation.
- Universal K1 compensation behavior.
- Physical superiority over scalar gain, nearest lookup, or ordinary interpolation baselines; those were not executed in this session.

## Before GO1/G1 Extension

Before extending to GO1 or G1, the project needs:

1. Revise the compensator policy to account for direct-baseline accuracy and avoid unnecessary command changes.
2. Re-run K1 physical validation after the compensator revision.
3. Add real GO1/G1 state-source discovery and measurement extraction.
4. Build GO1/G1 response profiles from real or explicitly simulated evidence, with clear labeling.
5. Run platform-specific before/after experiments before making any cross-platform claim.
