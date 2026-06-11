# Velocity Compensation Risk Filtering Specification

**Spec version**: `compensation_algorithm_spec_v1.0`
**Status**: Specification only.

## Purpose

Defines how the velocity compensator filters measurement cells by risk before selecting a segment for inverse interpolation. Risk filtering prevents the compensator from using unreliable, drift-prone, or under-evidenced data.

## Risk Region Labels

Measurement cells carry a `region_label` from the M16 risk classification pipeline:

| Label | Meaning | Compensator Action (Conservative) |
|-------|---------|-----------------------------------|
| `reliable` | Low tracking error, low yaw drift, low uncertainty | ✅ Accept |
| `under_track` | Actual velocity significantly below command | ❌ Reject (balanced: ⚠️ accept) |
| `unstable` | High variance, inconsistent response | ❌ Reject |
| `drift_prone` | High yaw drift during command | ❌ Reject (balanced: ⚠️ warn) |
| `deadzone` | No measurable motion | ❌ Reject (always) |
| `unclassified` | Not enough data to classify | ❌ Reject |

## Risk Score

Each cell has a `risk_score` (0.0 = no risk, 1.0 = maximum risk). The compensator uses `risk_score` as a tiebreaker when multiple segments are otherwise comparable.

Risk score components:
- Tracking error magnitude (normalized)
- Response uncertainty (normalized)
- Yaw drift magnitude (normalized)
- Sample size penalty (lower n → higher risk)

## Policy Definitions

### Conservative Policy (Default)

**Goal**: Only use cells where compensation is highly likely to be accurate and safe.

**Acceptance criteria**:
- `region_label == "reliable"`
- `risk_score <= 0.3`
- `confidence >= minimum_confidence` (0.5)
- `yaw_drift_deg < yaw_drift_high_threshold_deg` (5.0°)
- `response_uncertainty < uncertainty_high_threshold_mps` (0.08 m/s)
- `no_motion_ratio == 0`
- `n >= minimum_cell_repeats` (3)

**Rejection criteria**:
- Any of the above conditions not met → reject the cell
- Rejected cells are removed from segment construction entirely

**Use case**: Safety-critical applications, first-time deployment, unknown surface characteristics.

### Balanced Policy

**Goal**: Allow some risk in exchange for broader velocity coverage.

**Acceptance criteria**:
- `region_label in ["reliable", "under_track"]`
- `risk_score <= 0.6`
- `confidence >= 0.3`
- `yaw_drift_deg < 2 * yaw_drift_high_threshold_deg` (10.0°)
- `n >= 2`

**Warning conditions** (cell is accepted but generates warnings):
- `region_label == "drift_prone"` and `response_uncertainty < 0.04` → accept with warning
- `yaw_drift_deg > yaw_drift_high_threshold_deg` (5.0°) → warn
- `response_uncertainty > 0.04` → warn
- Only 2 repeats → warn about low sample size

**Rejection criteria**:
- `region_label == "deadzone"` → always reject
- `region_label == "unstable"` → always reject
- `n < 2` → reject

**Use case**: Controlled environments, experienced operators, surfaces with limited data.

### Permissive Policy

**Goal**: Maximize velocity coverage, accepting significant risk with explicit warnings.

**Acceptance criteria**:
- `region_label != "deadzone"` and `region_label != "unclassified"`
- `n >= 1`

**Warning conditions** (nearly everything generates warnings):
- `region_label != "reliable"` → warn with region label
- `yaw_drift_deg > 0` → warn
- `response_uncertainty > 0` → warn
- `no_motion_ratio > 0` → warn
- `n < minimum_cell_repeats` → warn

**Rejection criteria**:
- `region_label == "deadzone"` → always reject (no motion = no compensation)
- `region_label == "unclassified"` → reject (no data to evaluate)

**Feasibility status**: Always returns `feasible_but_risky` (never `ok`) unless the cell is reliable.

**Use case**: Research exploration, data collection planning, understanding compensation boundaries.

## Filtering Pipeline

```
All aggregate cells
    │
    ▼
[1. Evidence filter] ──► reject if n < minimum, evidence_level insufficient
    │
    ▼
[2. Deadzone filter] ──► reject if no_motion_ratio > 0 (all policies)
    │
    ▼
[3. Region label filter] ──► reject per policy rules
    │
    ▼
[4. Numeric threshold filter] ──► reject per yaw, uncertainty, risk_score thresholds
    │
    ▼
[5. Confidence filter] ──► reject if below minimum_confidence
    │
    ▼
Remaining cells → build monotonic segments → select best segment
```

## Filter Interaction with Deadzone

The deadzone filter (step 2) runs before region label filtering because a deadzone cell cannot produce useful compensation regardless of its other properties. Even under permissive policy, deadzone cells are rejected.

## Filter Interaction with Non-Monotonicity

Risk filtering runs before monotonic segment construction. A non-monotonic region may become monotonic after high-risk cells are removed. This is intentional: unstable or drift-prone cells cause apparent non-monotonicity that risk filtering eliminates.

If non-monotonicity persists after filtering, the `non_monotonic_ambiguous` status applies.
