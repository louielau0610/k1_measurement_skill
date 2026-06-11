# M22-D Offline Verification and Claim Boundary

**Status**: Offline verification only. Physical validation has not started.

## What M22-D Verifies

M22-D audits the M22-C offline velocity compensator prototype using:

1. **Edge-case audit**: 9 explicit test cases covering deadzone, out-of-range, unsupported platforms/surfaces, invalid input, risk policy behavior, and no-extrapolation default.

2. **Leave-one-repeat-out validation**: 72 held-out checks (3 repeats × 8 speeds × 3 surfaces). For each check, one repeat is held out, the remaining repeats build an aggregate response, and the compensator predicts what command velocity would produce the held-out measured actual velocity.

3. **Baseline comparison**: Compares the M22-C risk-aware conservative monotonic inverse lookup against four baselines: direct command, scalar gain, nearest lookup, and ordinary interpolation (without risk filtering).

4. **Risk policy audit**: Sweeps desired velocities across all surfaces and policies (conservative, balanced, permissive) to verify policy ordering, deadzone rejection, and proper labeling of risky outputs.

## What M22-D Does NOT Verify

- ❌ Physical K1 compensation (no robot commands sent)
- ❌ Deployment readiness (offline prototype only)
- ❌ Real-time performance (no timing constraints measured)
- ❌ Multi-surface transitions
- ❌ GO1 or G1 compensation (platforms return `platform_not_calibrated`)
- ❌ Navigation integration
- ❌ Battery-state effects
- ❌ Payload effects

## Why Offline Consistency Is Necessary Before K1 Physical Validation

Before sending compensated commands to a physical robot, we need confidence that:

1. The algorithm behaves correctly on known data (edge-case audit).
2. The algorithm is internally consistent (leave-one-repeat-out).
3. The algorithm improves over naive baselines (baseline comparison).
4. Risk policies behave as designed (risk policy audit).

Offline verification does not prove physical improvement — but it does prove the algorithm is well-formed and ready for physical testing.

## Why Physical Before/After Experiments Are Still Required

M22-D is a **necessary but not sufficient** condition for claiming compensation works. Physical validation requires:

- Running compensated and uncompensated trials on the same surface.
- Measuring actual velocities for both.
- Comparing tracking error distributions.
- Demonstrating statistically significant improvement.

This is Step 3 of the roadmap and has not yet started.

## How Baseline Comparison Supports Paper Positioning

The baseline comparison shows that:

- **Direct command** (u_cmd = v_desired) is the null hypothesis — what happens without compensation.
- **Scalar gain** is the simplest possible compensation — a single multiplier.
- **Nearest lookup** is a data-driven baseline without risk awareness.
- **Ordinary interpolation** is a global interpolation baseline without safety filtering.

The M22-C algorithm should outperform these baselines in terms of:
- Fewer infeasible recommendations (rejects what it cannot do safely)
- Better risk awareness (labels risky decisions explicitly)
- More accurate expected velocity predictions (within monotonic segments)

Physical validation will confirm whether these advantages translate to real tracking error reduction.

## Why No GO1/G1 Claim Is Made

- GO1 and G1 have **no measurement data** in this repository.
- Both platforms return `platform_not_calibrated` from the compensator.
- The measurement contract (M21-C) defines what data they need, but it does not exist yet.
- GO1/G1 calibration is Step 4 of the roadmap.

## Claim Boundary Summary

| Claim | Status |
|-------|--------|
| Offline algorithm correctness | ✅ Verified by M22-D |
| Internal consistency (LORO) | ✅ 72 checks performed |
| Improvement over baselines (offline) | ✅ Compared on K1 data |
| Physical K1 compensation improvement | ❌ Not claimed (Step 3) |
| Deployment readiness | ❌ Not claimed |
| GO1 compensation | ❌ Not claimed (Step 4) |
| G1 compensation | ❌ Not claimed (Step 4) |
| Real-time capability | ❌ Not claimed |
| Navigation improvement | ❌ Not claimed |
