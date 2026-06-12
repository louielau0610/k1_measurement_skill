# M23-E Revised Offline Compensator Sweep

Status: offline sweep only. No hardware execution and no physical validation claim.

- Surface: `S2_marble_floor`
- Decisions: 4
- Identity fallback count: 4
- Profile mismatch suspected count: 4
- Harmful M23-C compensated commands selected: 0
- Deployment ready: False

## Decisions

| Desired | Candidate | Final | Status | Direct error | Comp error | Benefit |
|---:|---:|---:|---|---:|---:|---:|
| 0.4 | 0.381884 | 0.4 | identity_preferred | 0.006667 | 0.024483 | -0.017816 |
| 0.45 | 0.416561 | 0.45 | identity_preferred | 0.0075 | 0.040383 | -0.032883 |
| 0.5 | 0.451825 | 0.5 | identity_preferred | 0.008333 | 0.0557 | -0.047367 |
| 0.55 | 0.502935 | 0.55 | identity_preferred | 0.009167 | 0.05545 | -0.046283 |

The revised logic avoids the M23-C failure mode by selecting identity where the physical direct baseline is already accurate.
