# M23-F Second K1 Validation Readiness

## Recommendation

Readiness category:

```text
ready_for_profile_refresh_before_validation
```

The revised offline compensator avoids every observed harmful M23-C command in offline replay, but profile mismatch is flagged for all tested velocities. This means the next step should be profile refresh or profile confirmation before a new compensation experiment.

## Should We Rerun The Same S2 Velocities?

Yes. Rerun 0.40, 0.45, 0.50, and 0.55 m/s if a second K1 validation is approved. These are the exact velocities where the old compensated commands failed.

The goal is not to prove broad compensation improvement. The immediate goal is to verify that revised identity fallback does not repeat the M23-C harm.

## Should We Validate Identity Non-Worsening?

Yes. The revised compensator selects identity for all four audited velocities. A second validation should confirm that this conservative behavior preserves the already-good direct tracking.

## Should We Refresh The S2 Profile?

Yes, before another selected-compensation experiment.

Recommended profile-refresh step:

1. Rerun a small S2 direct-response measurement set.
2. Compare current direct response to the M19C gold profile.
3. If mismatch is confirmed, write a versioned refreshed profile.
4. Do not overwrite `k1_gold_profile_v1.json` in place.

## Should We Choose A Different Surface?

Optionally, after the S2 profile is refreshed or confirmed. A surface where direct tracking is not already near-optimal may be a better test of selected compensation, but K1/S2 identity fallback should be validated first because that is the known failure case.

## Should Deadzone Or Low-Speed Targets Remain Excluded?

Yes. Deadzone and low-speed targets remain excluded unless a separate safety-reviewed protocol is created. They should not be forced into a compensation validation experiment.

## Boundary

This document is a readiness recommendation only. It does not run hardware, claim physical improvement, claim deployment readiness, or validate GO1/G1.
