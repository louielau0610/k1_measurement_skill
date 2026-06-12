# M24-I Controlled S2 Replication Analysis

**Decision**: `response_reproducible_profile_adoption_planning_allowed`

## Why Controlled Replication Was Needed

M24-F corrected S2 extraction remained inconclusive. M24-G designed a controlled replication experiment to isolate the S2 direct response under known conditions (marked start pose, straight path, operator reset confirmation, metadata recording). M24-H created the execution pack, and the clean session `m24h_controlled_s2_replication_clean_20260612_171419` was successfully run on the robot.

M24-I analyzes this controlled replication to determine whether the S2 response is reproducible enough for profile adoption planning.

## How M24-I Differs From M24-F

| Aspect | M24-F | M24-I |
|--------|-------|-------|
| Data source | M24-B refresh (mixed conditions) | M24-H controlled replication (direct only) |
| Condition | Mixed (some stale config) | `direct_refresh_controlled` only |
| Metadata | Minimal | Full controlled metadata (warmup, pose, path, reset) |
| Extraction | Corrected post-hoc | Corrected from start |
| QC | Post-hoc | Built-in QC verified 26/26 checks |

## Whether Controlled Response Is Reproducible

**3 of 4 velocities** match M24-F within the 0.03 m/s reproducibility threshold. The controlled response is consistent with the earlier M24-F corrected extraction, supporting the interpretation that the S2 response is not purely environment-dependent.

However, 0 of 4 velocities match M19C within 0.05 m/s, confirming that the S2 response has drifted from the original gold profile. This is expected given M24-D's diagnosis of `environment_dependent_response`.

## What Can and Cannot Be Claimed

| Claim | Status |
|-------|--------|
| Controlled replication analyzed | ✅ |
| Response reproducible vs M24-F | ✅ 3/4 velocities |
| Profile adoption planning allowed | ✅ Candidate only |
| Profile adopted as gold | ❌ Not adopted |
| Compensation validated | ❌ Not claimed |
| Deployment ready | ❌ Not claimed |
| GO1/G1 | ❌ Blocked |

## Why Compensation Validation Remains Separate

The M24-I candidate profile is a **direct response profile only** — it characterizes `v_cmd → v_actual` for S2_marble_floor under controlled conditions. Compensation validation requires running compensated commands (using M22-C/M23-E offline compensator) and comparing tracking error against direct baselines. This is a separate experiment, not part of M24-I.
