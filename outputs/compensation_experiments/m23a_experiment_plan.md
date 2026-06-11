# M23-A K1 Compensation Experiment Plan

Generated: 2026-06-11T09:34:31.988953+00:00
Surface: S2_marble_floor
Platform: booster_k1
Risk policy: balanced

**Status**: EXPERIMENT DESIGN ONLY — no hardware execution — no physical validation claim

## Trial Plan Summary
- Total trials: 36
- Pairs: 18
- Direct trials: 18
- Compensated trials: 18
- Infeasible compensated targets: 18
- Random seed: 42

## Desired Velocities
- 0.3 m/s
- 0.35 m/s
- 0.4 m/s
- 0.45 m/s
- 0.5 m/s
- 0.55 m/s

## Trial Plan

| # | Trial ID | Pair | v_desired | Condition | u_cmd | Status |
|---|----------|------|-----------|-----------|-------|--------|
| 1 | M23A_S2_marble_floor_V030_dire_R1 | M23A_S2_marble_floor_V030_P1 | 0.3 | direct | 0.300 | na_direct_baseline |
| 2 | M23A_S2_marble_floor_V030_comp_R1 | M23A_S2_marble_floor_V030_P1 | 0.3 | compensated |  | infeasible_deadzone |
| 3 | M23A_S2_marble_floor_V030_comp_R2 | M23A_S2_marble_floor_V030_P2 | 0.3 | compensated |  | infeasible_deadzone |
| 4 | M23A_S2_marble_floor_V030_dire_R2 | M23A_S2_marble_floor_V030_P2 | 0.3 | direct | 0.300 | na_direct_baseline |
| 5 | M23A_S2_marble_floor_V030_dire_R3 | M23A_S2_marble_floor_V030_P3 | 0.3 | direct | 0.300 | na_direct_baseline |
| 6 | M23A_S2_marble_floor_V030_comp_R3 | M23A_S2_marble_floor_V030_P3 | 0.3 | compensated |  | infeasible_deadzone |
| 7 | M23A_S2_marble_floor_V035_dire_R1 | M23A_S2_marble_floor_V035_P1 | 0.35 | direct | 0.350 | na_direct_baseline |
| 8 | M23A_S2_marble_floor_V035_comp_R1 | M23A_S2_marble_floor_V035_P1 | 0.35 | compensated |  | infeasible_deadzone |
| 9 | M23A_S2_marble_floor_V035_comp_R2 | M23A_S2_marble_floor_V035_P2 | 0.35 | compensated |  | infeasible_deadzone |
| 10 | M23A_S2_marble_floor_V035_dire_R2 | M23A_S2_marble_floor_V035_P2 | 0.35 | direct | 0.350 | na_direct_baseline |
| 11 | M23A_S2_marble_floor_V035_dire_R3 | M23A_S2_marble_floor_V035_P3 | 0.35 | direct | 0.350 | na_direct_baseline |
| 12 | M23A_S2_marble_floor_V035_comp_R3 | M23A_S2_marble_floor_V035_P3 | 0.35 | compensated |  | infeasible_deadzone |
| 13 | M23A_S2_marble_floor_V040_dire_R1 | M23A_S2_marble_floor_V040_P1 | 0.4 | direct | 0.400 | na_direct_baseline |
| 14 | M23A_S2_marble_floor_V040_comp_R1 | M23A_S2_marble_floor_V040_P1 | 0.4 | compensated |  | infeasible_deadzone |
| 15 | M23A_S2_marble_floor_V040_comp_R2 | M23A_S2_marble_floor_V040_P2 | 0.4 | compensated |  | infeasible_deadzone |
| 16 | M23A_S2_marble_floor_V040_dire_R2 | M23A_S2_marble_floor_V040_P2 | 0.4 | direct | 0.400 | na_direct_baseline |
| 17 | M23A_S2_marble_floor_V040_dire_R3 | M23A_S2_marble_floor_V040_P3 | 0.4 | direct | 0.400 | na_direct_baseline |
| 18 | M23A_S2_marble_floor_V040_comp_R3 | M23A_S2_marble_floor_V040_P3 | 0.4 | compensated |  | infeasible_deadzone |
| 19 | M23A_S2_marble_floor_V045_dire_R1 | M23A_S2_marble_floor_V045_P1 | 0.45 | direct | 0.450 | na_direct_baseline |
| 20 | M23A_S2_marble_floor_V045_comp_R1 | M23A_S2_marble_floor_V045_P1 | 0.45 | compensated |  | infeasible_deadzone |
| 21 | M23A_S2_marble_floor_V045_comp_R2 | M23A_S2_marble_floor_V045_P2 | 0.45 | compensated |  | infeasible_deadzone |
| 22 | M23A_S2_marble_floor_V045_dire_R2 | M23A_S2_marble_floor_V045_P2 | 0.45 | direct | 0.450 | na_direct_baseline |
| 23 | M23A_S2_marble_floor_V045_dire_R3 | M23A_S2_marble_floor_V045_P3 | 0.45 | direct | 0.450 | na_direct_baseline |
| 24 | M23A_S2_marble_floor_V045_comp_R3 | M23A_S2_marble_floor_V045_P3 | 0.45 | compensated |  | infeasible_deadzone |
| 25 | M23A_S2_marble_floor_V050_dire_R1 | M23A_S2_marble_floor_V050_P1 | 0.5 | direct | 0.500 | na_direct_baseline |
| 26 | M23A_S2_marble_floor_V050_comp_R1 | M23A_S2_marble_floor_V050_P1 | 0.5 | compensated |  | infeasible_deadzone |
| 27 | M23A_S2_marble_floor_V050_comp_R2 | M23A_S2_marble_floor_V050_P2 | 0.5 | compensated |  | infeasible_deadzone |
| 28 | M23A_S2_marble_floor_V050_dire_R2 | M23A_S2_marble_floor_V050_P2 | 0.5 | direct | 0.500 | na_direct_baseline |
| 29 | M23A_S2_marble_floor_V050_dire_R3 | M23A_S2_marble_floor_V050_P3 | 0.5 | direct | 0.500 | na_direct_baseline |
| 30 | M23A_S2_marble_floor_V050_comp_R3 | M23A_S2_marble_floor_V050_P3 | 0.5 | compensated |  | infeasible_deadzone |
| 31 | M23A_S2_marble_floor_V055_dire_R1 | M23A_S2_marble_floor_V055_P1 | 0.55 | direct | 0.550 | na_direct_baseline |
| 32 | M23A_S2_marble_floor_V055_comp_R1 | M23A_S2_marble_floor_V055_P1 | 0.55 | compensated |  | infeasible_deadzone |
| 33 | M23A_S2_marble_floor_V055_comp_R2 | M23A_S2_marble_floor_V055_P2 | 0.55 | compensated |  | infeasible_deadzone |
| 34 | M23A_S2_marble_floor_V055_dire_R2 | M23A_S2_marble_floor_V055_P2 | 0.55 | direct | 0.550 | na_direct_baseline |
| 35 | M23A_S2_marble_floor_V055_dire_R3 | M23A_S2_marble_floor_V055_P3 | 0.55 | direct | 0.550 | na_direct_baseline |
| 36 | M23A_S2_marble_floor_V055_comp_R3 | M23A_S2_marble_floor_V055_P3 | 0.55 | compensated |  | infeasible_deadzone |

## Next Steps
1. M23-B: Execute this plan on physical Booster K1.
2. Record ROS2 state logs for all trials.
3. M23-C: Analyze before/after results.
