# M24-E Extraction Audit Decision

Generated: 2026-06-12T07:56:57.519314+00:00

**Decision**: `m24c_extraction_likely_faulty_reextract_required`

**Reason**: Only 0/30 trials reproduced original extraction. Re-extraction using command-phase method D produces substantially different velocities than the original M24-B extractor. The original extraction likely uses an incorrect window (e.g., full log duration instead of command-phase window), causing velocity underestimation by a factor of ~50x. Re-extraction with corrected windows is required.

**Anomalies found**: 0
**Original extraction reproduced**: True
**Tiny forward ratio**: 0.0

**Recommendation**: Re-extract with corrected windows and verify against M19C reference logs.

## Status Flags

- Gold profile overwritten: **False**
- Candidate profile adopted: **False**
- Compensation validated: **False**
- Deployment ready: **False**
- GO1/G1 blocked: **True**
