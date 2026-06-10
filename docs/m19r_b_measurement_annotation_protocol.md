# M19R-B Measurement Annotation Protocol

M19R-B completes the evidence path for M19 without fabricating empirical measurements. Existing command velocity, subjective notes, and trial duration are not measurements of actual robot velocity or yaw drift.

## Acceptable Measurement Sources

Priority 1: normalized robot logs containing position, velocity, and yaw fields.

Priority 2: raw logs that can be parsed into position, velocity, and yaw fields.

Priority 3: video-assisted distance-time measurement with visible distance markers and documented frame/time references.

Priority 4: manual marked-distance and stopwatch measurement, only if the distance, timing method, and yaw readings are documented.

## Required Formulas

Actual velocity:

```text
y = distance_m / time_sec
```

Yaw drift:

```text
psi = abs(end_yaw_deg - start_yaw_deg)
```

Yaw drift should be recorded in degrees. If the source records radians, convert to degrees and note the conversion in `annotation_notes`.

## Annotation Rules

- `command_velocity` must never be copied into `measured_actual_velocity`.
- Subjective notes such as "no visible motion" cannot be converted into numeric velocity.
- Yaw estimates from video must use `measurement_confidence=low` unless calibrated yaw markers make the estimate defensible.
- Log-derived measurements with clear fields and timestamps may use `measurement_confidence=high`.
- Video or manual measurements with documented but approximate evidence should use `measurement_confidence=medium` or `low`.
- Unmeasurable trials remain `pending_measurement_extraction`.
- Replacement trial rows are placeholders until the physical replacement trial is executed and measured.

## Annotation Columns

Fill `measured_actual_velocity` and `yaw_drift_statistic` only when real evidence is available. When either measurement is present, also fill `measurement_source`, `measurement_method`, and `measurement_confidence`.
