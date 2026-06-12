# M24-D Profile Adoption Boundary

The M24-C candidate profile is not adopted automatically.

Current adoption decision:

```text
investigate_extraction_before_profile_decision
```

## Why Not Adopt Yet

- M24-C was `inconclusive_environment_dependent`.
- M24-C differs from old M19C S2 profile.
- M24-C also differs from M23-C direct-response evidence.
- M24-C has near-zero measured velocity across the tested direct commands.
- The artifacts do not fully encode reset procedure, starting pose, battery, warm-up, or environment state.

## Allowed Next Steps

- Audit the M24-B/M24-C extraction method and odometer source.
- Collect controlled direct-only S2 replication data.
- Keep the revised compensator offline-only until the current S2 response question is resolved.

## Forbidden Steps

- Do not overwrite `k1_gold_profile_v1`.
- Do not adopt `m24c_s2_current_profile_candidate.json` as a gold profile.
- Do not run a second compensation validation yet.
- Do not claim compensation improvement.
- Do not claim deployment readiness.
- Do not start GO1/G1 work.
