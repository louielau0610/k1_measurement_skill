# M23-A K1 Compensation Experiment Plan

Generated: 2026-06-12T03:12:27.942272+00:00
Surface: S2_marble_floor
Platform: booster_k1
Risk policy: permissive
Minimum confidence: 0.0

**Status**: EXPERIMENT DESIGN ONLY - no hardware execution - no physical validation claim

## Trial Plan Summary
- Total traceability trials: 36
- Traceability pairs: 18
- Executable trials: 24
- Executable pairs: 12
- Direct trials: 18
- Compensated trials: 18
- Infeasible compensated targets: 6
- Executable plan: `outputs\compensation_experiments\m23a_executable_trial_plan.csv`
- Random seed: 42

## Desired Velocities
- 0.3 m/s
- 0.35 m/s
- 0.4 m/s
- 0.45 m/s
- 0.5 m/s
- 0.55 m/s

## Infeasible Pair Handling
- `M23A_S2_marble_floor_V030_P1` excluded from executable plan: compensator_status=infeasible_deadzone
- `M23A_S2_marble_floor_V030_P2` excluded from executable plan: compensator_status=infeasible_deadzone
- `M23A_S2_marble_floor_V030_P3` excluded from executable plan: compensator_status=infeasible_deadzone
- `M23A_S2_marble_floor_V035_P1` excluded from executable plan: compensator_status=infeasible_deadzone
- `M23A_S2_marble_floor_V035_P2` excluded from executable plan: compensator_status=infeasible_deadzone
- `M23A_S2_marble_floor_V035_P3` excluded from executable plan: compensator_status=infeasible_deadzone

## Trial Plan

| # | Trial ID | Pair | v_desired | Condition | u_cmd | Status | Run status |
|---|----------|------|-----------|-----------|-------|--------|------------|
| 1 | M23A_S2_marble_floor_V030_dire_R1 | M23A_S2_marble_floor_V030_P1 | 0.3 | direct | 0.300 | na_direct_baseline | planned |
| 2 | M23A_S2_marble_floor_V030_comp_R1 | M23A_S2_marble_floor_V030_P1 | 0.3 | compensated |  | infeasible_deadzone | not_executable |
| 3 | M23A_S2_marble_floor_V030_dire_R2 | M23A_S2_marble_floor_V030_P2 | 0.3 | direct | 0.300 | na_direct_baseline | planned |
| 4 | M23A_S2_marble_floor_V030_comp_R2 | M23A_S2_marble_floor_V030_P2 | 0.3 | compensated |  | infeasible_deadzone | not_executable |
| 5 | M23A_S2_marble_floor_V030_dire_R3 | M23A_S2_marble_floor_V030_P3 | 0.3 | direct | 0.300 | na_direct_baseline | planned |
| 6 | M23A_S2_marble_floor_V030_comp_R3 | M23A_S2_marble_floor_V030_P3 | 0.3 | compensated |  | infeasible_deadzone | not_executable |
| 7 | M23A_S2_marble_floor_V035_dire_R1 | M23A_S2_marble_floor_V035_P1 | 0.35 | direct | 0.350 | na_direct_baseline | planned |
| 8 | M23A_S2_marble_floor_V035_comp_R1 | M23A_S2_marble_floor_V035_P1 | 0.35 | compensated |  | infeasible_deadzone | not_executable |
| 9 | M23A_S2_marble_floor_V035_dire_R2 | M23A_S2_marble_floor_V035_P2 | 0.35 | direct | 0.350 | na_direct_baseline | planned |
| 10 | M23A_S2_marble_floor_V035_comp_R2 | M23A_S2_marble_floor_V035_P2 | 0.35 | compensated |  | infeasible_deadzone | not_executable |
| 11 | M23A_S2_marble_floor_V035_dire_R3 | M23A_S2_marble_floor_V035_P3 | 0.35 | direct | 0.350 | na_direct_baseline | planned |
| 12 | M23A_S2_marble_floor_V035_comp_R3 | M23A_S2_marble_floor_V035_P3 | 0.35 | compensated |  | infeasible_deadzone | not_executable |
| 13 | M23A_S2_marble_floor_V040_dire_R1 | M23A_S2_marble_floor_V040_P1 | 0.4 | direct | 0.400 | na_direct_baseline | planned |
| 14 | M23A_S2_marble_floor_V040_comp_R1 | M23A_S2_marble_floor_V040_P1 | 0.4 | compensated | 0.382 | feasible_but_risky | planned |
| 15 | M23A_S2_marble_floor_V040_dire_R2 | M23A_S2_marble_floor_V040_P2 | 0.4 | direct | 0.400 | na_direct_baseline | planned |
| 16 | M23A_S2_marble_floor_V040_comp_R2 | M23A_S2_marble_floor_V040_P2 | 0.4 | compensated | 0.382 | feasible_but_risky | planned |
| 17 | M23A_S2_marble_floor_V040_dire_R3 | M23A_S2_marble_floor_V040_P3 | 0.4 | direct | 0.400 | na_direct_baseline | planned |
| 18 | M23A_S2_marble_floor_V040_comp_R3 | M23A_S2_marble_floor_V040_P3 | 0.4 | compensated | 0.382 | feasible_but_risky | planned |
| 19 | M23A_S2_marble_floor_V045_dire_R1 | M23A_S2_marble_floor_V045_P1 | 0.45 | direct | 0.450 | na_direct_baseline | planned |
| 20 | M23A_S2_marble_floor_V045_comp_R1 | M23A_S2_marble_floor_V045_P1 | 0.45 | compensated | 0.417 | feasible_but_risky | planned |
| 21 | M23A_S2_marble_floor_V045_dire_R2 | M23A_S2_marble_floor_V045_P2 | 0.45 | direct | 0.450 | na_direct_baseline | planned |
| 22 | M23A_S2_marble_floor_V045_comp_R2 | M23A_S2_marble_floor_V045_P2 | 0.45 | compensated | 0.417 | feasible_but_risky | planned |
| 23 | M23A_S2_marble_floor_V045_dire_R3 | M23A_S2_marble_floor_V045_P3 | 0.45 | direct | 0.450 | na_direct_baseline | planned |
| 24 | M23A_S2_marble_floor_V045_comp_R3 | M23A_S2_marble_floor_V045_P3 | 0.45 | compensated | 0.417 | feasible_but_risky | planned |
| 25 | M23A_S2_marble_floor_V050_dire_R1 | M23A_S2_marble_floor_V050_P1 | 0.5 | direct | 0.500 | na_direct_baseline | planned |
| 26 | M23A_S2_marble_floor_V050_comp_R1 | M23A_S2_marble_floor_V050_P1 | 0.5 | compensated | 0.452 | feasible_but_risky | planned |
| 27 | M23A_S2_marble_floor_V050_dire_R2 | M23A_S2_marble_floor_V050_P2 | 0.5 | direct | 0.500 | na_direct_baseline | planned |
| 28 | M23A_S2_marble_floor_V050_comp_R2 | M23A_S2_marble_floor_V050_P2 | 0.5 | compensated | 0.452 | feasible_but_risky | planned |
| 29 | M23A_S2_marble_floor_V050_dire_R3 | M23A_S2_marble_floor_V050_P3 | 0.5 | direct | 0.500 | na_direct_baseline | planned |
| 30 | M23A_S2_marble_floor_V050_comp_R3 | M23A_S2_marble_floor_V050_P3 | 0.5 | compensated | 0.452 | feasible_but_risky | planned |
| 31 | M23A_S2_marble_floor_V055_dire_R1 | M23A_S2_marble_floor_V055_P1 | 0.55 | direct | 0.550 | na_direct_baseline | planned |
| 32 | M23A_S2_marble_floor_V055_comp_R1 | M23A_S2_marble_floor_V055_P1 | 0.55 | compensated | 0.503 | feasible_but_risky | planned |
| 33 | M23A_S2_marble_floor_V055_dire_R2 | M23A_S2_marble_floor_V055_P2 | 0.55 | direct | 0.550 | na_direct_baseline | planned |
| 34 | M23A_S2_marble_floor_V055_comp_R2 | M23A_S2_marble_floor_V055_P2 | 0.55 | compensated | 0.503 | feasible_but_risky | planned |
| 35 | M23A_S2_marble_floor_V055_dire_R3 | M23A_S2_marble_floor_V055_P3 | 0.55 | direct | 0.550 | na_direct_baseline | planned |
| 36 | M23A_S2_marble_floor_V055_comp_R3 | M23A_S2_marble_floor_V055_P3 | 0.55 | compensated | 0.503 | feasible_but_risky | planned |

## Next Steps
1. M23-B formal before/after execution must use the executable trial plan CSV.
2. Record ROS2 state logs for executable pairs only.
3. M23-C analyzes before/after results only after physical data pass QC.
