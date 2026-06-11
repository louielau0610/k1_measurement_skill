# M22-D Edge-Case Audit

Generated: 2026-06-11T09:18:56.983909+00:00
Total cases: 9, Passed: 5, Failed: 4

**Disclaimer**: offline verification only — not physical validation — not deployment-ready — no hardware execution

| # | Surface | Desired | Policy | Expected | Actual | Pass |
|---|---------|---------|--------|----------|--------|------|
| 1 | S1_lab_hard_floor | -0.1 | conservative | invalid_input | invalid_input | ✅ |
| 2 | S1_lab_hard_floor | 0.001 | conservative | infeasible_deadzone | infeasible_deadzone | ✅ |
| 3 | S1_lab_hard_floor | 2.0 | conservative | infeasible_out_of_range | insufficient_evidence | ❌ |
| 4 | lab_hard_floor | 0.3 | conservative | platform_not_calibrated | platform_not_calibrated | ✅ |
| 5 | lab_hard_floor | 0.3 | conservative | platform_not_calibrated | platform_not_calibrated | ✅ |
| 6 | nonexistent_surface | 0.3 | conservative | surface_not_calibrated | surface_not_calibrated | ✅ |
| 7 | S1_lab_hard_floor | 0.3 | conservative | insufficient_evidence | infeasible_deadzone | ❌ |
| 8 | S1_lab_hard_floor | 0.3 | permissive | feasible_but_risky | infeasible_deadzone | ❌ |
| 9 | S1_lab_hard_floor | 0.6 | conservative | infeasible_out_of_range | insufficient_evidence | ❌ |
