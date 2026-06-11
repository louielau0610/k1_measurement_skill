# M22-D Offline Compensator Verification Report

Generated: 2026-06-11T09:18:56.983909+00:00
Platform: booster_k1

**Disclaimer**: offline verification only — not physical validation — not deployment-ready — no hardware execution

## Leave-One-Repeat-Out
- Total checks: 72
- Feasible: 60
- Mean abs cmd error: 1.0084241502936786

## Edge-Case Audit
- Total: 9, Passed: 5, Failed: 4

## Risk Policy Audit
- conservative: feasible=0, risky=0, rejected=78
- balanced: feasible=0, risky=0, rejected=78
- permissive: feasible=0, risky=0, rejected=78

## Baseline Comparison
- Total comparisons: 56
- Methods: direct_command, scalar_gain, nearest_lookup, ordinary_interpolation

## Status
- Physical validation: **not_started**
- Deployment ready: **False**
- Offline only: **True**

## Next
M23-A: K1 physical compensation experiment design.
