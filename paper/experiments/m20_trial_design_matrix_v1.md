# M20 Trial Design Matrix v1

Design matrix for future K1 velocity response and navigation outcome experiments. All counts and values are proposed — not executed. Mark `TO_BE_FILLED` where site-specific decisions are required.

## Command grid plan

| command_type | range | step | points | notes |
| --- | --- | --- | --- | --- |
| vx (forward) | 0.05–0.60 m/s | 0.05 or 0.10 | 8-12 | Include 0.10 deadzone zone; keep overlap with v1 grid |
| vy (lateral) | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED | Optional Tier 1 extension |
| omega_z (angular) | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED | Optional Tier 1 extension |

## Repeated trial counts

| tier | trials_per_command | total_commands | total_trials | notes |
| --- | --- | --- | --- | --- |
| Tier 1 minimum | 3 | 8 | 24 | Sufficient for variance estimate |
| Tier 1 recommended | 5 | 12 | 60 | Better statistical power |
| Tier 2 held-out | 5 | 12 (split fit/val/hold) | 60 | Requires fit/val/hold split |
| Tier 3 navigation | 5 per task | 3-5 tasks | 15-25 | Per condition |

## Held-out split plan

| set | fraction | purpose |
| --- | --- | --- |
| fit | 60% | Model fitting |
| validation | 20% | Model selection/hyperparameters (if any) |
| held-out | 20% | Final predictive evaluation |

## Surface/session plan

| surface | sessions | notes |
| --- | --- | --- |
| indoor hard floor | 2-3 | Replicates v1 surface |
| indoor carpet | 2-3 | New surface |
| outdoor pavement | TO_BE_FILLED | SITE_SPECIFIC |
| outdoor grass | TO_BE_FILLED | SITE_SPECIFIC |

## Navigation task plan

| task_id | task_type | description | metrics_collected |
| --- | --- | --- | --- |
| NAV-01 | corridor traversal | Straight corridor, fixed distance | success, completion time, path deviation |
| NAV-02 | obstacle avoidance | Fixed obstacles on path | collision, near-miss, min_distance |
| NAV-03 | precision approach | Approach target point within tolerance | success, path deviation |
| NAV-04 | TO_BE_FILLED | AUTHOR_DECISION_REQUIRED | — |
| NAV-05 | TO_BE_FILLED | AUTHOR_DECISION_REQUIRED | — |

## Baseline/advisory comparison plan

| condition | description | allowed | disallowed |
| --- | --- | --- | --- |
| baseline | No advisory risk labels available | Standard navigation commands | — |
| advisory | Advisory risk labels available to analysis/operator | Display warnings; manual decision support; pre-trip analysis | Automatic compensation; real-time command modification; safe adapter execution |

## Minimum viable protocol (MVP)

- 1 robot, 1 surface, 2 sessions.
- 8 vx command points, 3 trials each (24 total).
- Held-out split: 5 fit / 1 val / 2 held.
- 2 navigation tasks, 5 trials each in one condition.
- Deliverables: expanded dataset v2, held-out MAE/RMSE, advisory risk/outcome association.

## Stronger full protocol

- 1 robot, 3 surfaces, 2+ sessions each.
- 12 vx command points, 5 trials each (60 total per surface).
- Held-out split with full evaluation.
- 3-5 navigation tasks, 5+ trials each in both baseline and advisory conditions.
- Deliverables: multi-surface dataset, held-out evaluation, before/after advisory comparison, navigation outcome analysis.
