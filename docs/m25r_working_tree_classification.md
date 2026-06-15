# M25-R Working Tree Classification

Baseline commands were run on `feature/m24i-controlled-s2-replication-analysis` at `69aa216`, then the branch `feature/m25r-real-data-readiness` was created from `69aa216`. Existing changes were carried over intact.

## Dirty And Untracked Paths

| Path | Category | Intended action | Rationale |
|------|----------|-----------------|-----------|
| `AGENTS.md` | user-authored change | Preserve, do not stage for M25-R | Adds a documentation-maintenance rule; ownership predates M25-R. |
| `outputs/compensation_experiments/m24e_extraction_anomaly_report.md` | reproducible generated artifact | Preserve unstaged | Diff is timestamp-only; not needed for M25-R and not raw data. |
| `outputs/compensation_experiments/m24e_extraction_anomaly_summary.json` | reproducible generated artifact | Preserve unstaged | Diff is timestamp-only; not needed for M25-R and not raw data. |
| `outputs/compensation_experiments/m24e_extraction_audit_decision.json` | reproducible generated artifact | Preserve unstaged | Diff is timestamp-only; not needed for M25-R and not raw data. |
| `outputs/compensation_experiments/m24e_extraction_audit_decision.md` | reproducible generated artifact | Preserve unstaged | Diff is timestamp-only; not needed for M25-R and not raw data. |
| `outputs/compensation_experiments/m24e_m24c_crosscheck.md` | reproducible generated artifact | Preserve unstaged | Diff is timestamp-only; not needed for M25-R and not raw data. |
| `outputs/real_k1_validation_m19/m19_validation_report.md` | tracked historical evidence | Preserve unstaged | Diff would replace historical M19R content with a pending-data summary; ownership and intent are unclear. |
| `outputs/real_k1_validation_m19/repeated_validation_summary.json` | tracked historical evidence | Preserve unstaged | Large historical summary rewrite; not needed for M25-R and may affect auditability. |
| `data/measurement_sessions/` | raw real-robot data or temporary execution artifact | Preserve; add ignore rule | Local measurement-session tree may contain raw/operator execution evidence. It must not be deleted. Future local sessions should not pollute Git status. |
| `docs/project_overview.md` | user-authored change | Preserve unstaged | Pre-existing documentation artifact; ownership predates M25-R. |
| `docs/modules/calibration_core_implementation.md` | user-authored change | Preserve unstaged | Pre-existing module documentation; not modified by M25-R. |
| `docs/modules/calibration_core_principles.md` | user-authored change | Preserve unstaged | Pre-existing module documentation; not modified by M25-R. |
| `docs/modules/platforms_implementation.md` | user-authored change | Preserve unstaged | Pre-existing module documentation; not modified by M25-R. |
| `docs/modules/platforms_principles.md` | user-authored change | Preserve unstaged | Pre-existing module documentation; not modified by M25-R. |

## Confirmation

No raw data, user-authored change, or unknown-ownership path was deleted, reverted, stashed, or staged for the M25-R commit.
