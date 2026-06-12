# M24-G Claim Boundary

M24-G is a design-only milestone.

It creates a controlled S2 replication design, physical protocol, metadata schema, trial plan, analysis plan, and manifest. It does not execute hardware and does not create new physical measurements.

M24-G does not:

- Run Booster K1 hardware.
- Fabricate physical results.
- Overwrite `k1_gold_profile_v1`.
- Adopt the M24-F corrected candidate profile.
- Validate compensation.
- Claim compensation improvement.
- Claim deployment readiness.
- Start GO1/G1 work.

Current boundary flags:

- `physical_run_status=not_run`
- `new_physical_data=false`
- `profile_adoption_status=not_adopted`
- `gold_profile_overwritten=false`
- `revised_compensator_status=offline_only`
- `compensation_validation_status=blocked_pending_controlled_replication`
- `deployment_ready=false`
- `go1_g1_blocked=true`
