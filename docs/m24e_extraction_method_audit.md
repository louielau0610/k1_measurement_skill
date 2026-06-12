# M24-E Extraction Method Audit

**Status**: Audit complete. Extraction fault identified.
**Decision**: `m24c_extraction_likely_faulty_reextract_required`

## Why M24-E Was Needed

M24-C analysis showed that the M24-B refresh session produced strongly discrepant velocity measurements compared to both M19C and M23-C. Before adopting or rejecting the M24-C candidate profile, the project needed to determine whether the discrepancy was:

1. **Physical/environmental** — the robot actually moved differently on S2 during M24-B.
2. **Extraction-related** — the extraction method produced incorrect velocity values from valid raw logs.

M24-E audits the raw state logs to answer this question.

## Extraction Windows Tested

| Method | Description |
|--------|-------------|
| A | Full log window excluding first/last 1.0s |
| B | Command phase based on known idle_sec + command_sec |
| C | Middle command window excluding first/last 1.0s of command phase |
| D | Original M24-B extraction method (reproduced — command phase samples) |
| E | Raw displacement over full log duration |

## Forward Projection Method

All methods compute forward distance as Euclidean displacement:

$$d_{forward} = \sqrt{(x_{end} - x_{start})^2 + (y_{end} - y_{start})^2}$$

Velocity is computed as:

$$v_{actual} = d_{forward} / \Delta t$$

where $\Delta t$ is the duration of the selected window, computed from `timestamp_monotonic` differences.

## Key Findings

### Cross-Check: Original Extraction NOT Reproduced

**0 of 30 trials** reproduced the original M24-B extracted velocity when using method D (command-phase window with timestamp_monotonic duration).

| v_cmd | Original M24-B mean v_actual | Method D re-extracted mean v_actual | Factor |
|-------|------------------------------|--------------------------------------|--------|
| 0.35 | ~0.0007 m/s | ~0.043 m/s | ~58× |
| 0.40 | ~0.0007 m/s | ~0.058 m/s | ~86× |
| 0.45 | ~0.0018 m/s | ~0.094 m/s | ~51× |
| 0.50 | ~0.0008 m/s | ~0.092 m/s | ~112× |

The original M24-B extraction underestimates velocity by a factor of ~50-110× compared to command-phase re-extraction. This strongly indicates the original extraction used an incorrect time window — likely the full ~9-10s log duration (1000 Hz, ~9000 samples) instead of the ~6s command-phase window.

### Raw Log Quality

- **30 raw state logs** audited.
- **0 anomalies** found in raw log schema, timestamp monotonicity, or column structure.
- `timestamp_monotonic` is present and strictly increasing in all logs.
- Phase segmentation (idle/command/stop) is present in all logs.
- Sample rate: ~1000 Hz (consistent with Booster K1 odometer publishing).

## Anomaly Labels Assigned

- `extraction_issue_likely` — supported by the 0/30 reproduction rate and ~50-110× velocity underestimation.
- No `timestamp_nonmonotonic`, `duration_mismatch`, `sample_rate_unexpected`, `state_log_schema_unexpected` labels triggered — raw logs are structurally valid.

## Decision

**`m24c_extraction_likely_faulty_reextract_required`**

The original M24-B extraction is not reproducible from raw logs using any reasonable extraction window. The most likely cause is that the extractor used the full log duration (including idle and stop phases) rather than the command-phase window, causing velocity underestimation by a factor of ~50-110×.

**Recommendation**: Re-extract all M24-B trials using the corrected command-phase window (method B or D), then re-evaluate the M24-C candidate profile consistency.

## Why Profile Adoption and Compensation Validation Remain Blocked

- The M24-C candidate profile was computed from faulty extraction data.
- Until corrected re-extraction is performed and validated, no profile adoption decision can be made.
- Compensation validation requires trustworthy velocity measurements.
- Gold profile (M19C-E) remains unchanged and is the reference for all comparisons.
