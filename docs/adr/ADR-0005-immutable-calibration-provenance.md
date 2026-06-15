# ADR-0005: Immutable Calibration Provenance

**Status**: Accepted
**Date**: 2026-06-15
**Milestone**: M26-A

## Context

Calibration profiles are the foundation for velocity compensation decisions.
When a profile is used to compensate a velocity command, there must be complete
traceability from the compensated command back through the profile, the model,
the dataset, the raw telemetry, the session configuration, and the operator
authorization.

Without immutable provenance, it is impossible to audit why a particular
compensation decision was made, or to determine whether a profile is still valid
after platform or environmental changes.

The current K1 gold profile (`outputs/real_k1_validation_m19/k1_gold_profile_v1.json`)
is treated as immutable, but this is a convention, not an enforced architectural
invariant. The safe speed configuration includes a hash in the audit trail,
which is a good precedent.

## Decision

We will adopt **immutable calibration provenance** as an architectural invariant:

1. **All calibration artifacts are content-addressed**: Each artifact (raw log,
   normalized telemetry, dataset, model, profile) has a unique ID and a
   cryptographic hash of its content.

2. **Provenance chains are append-only**: Each artifact records the hashes of
   all artifacts it was derived from. The chain can be verified end-to-end.

3. **Gold profiles are immutable**: A profile with status "gold" must never be
   overwritten. Updates create a new profile with a new ID and a reference to
   the superseded profile.

4. **Safety configurations are hashed into all downstream artifacts**: The
   safety envelope hash appears in trial plans, session metadata, and
   compensation decisions. Any safety configuration change is detectable.

5. **Audit records reference immutable artifacts**: Execution audit records
   reference profiles, models, and configurations by hash, not by mutable path.

6. **Operator confirmations are hashed**: OperatorAuthorization records include
   a hash of what was confirmed, enabling verification that the executed plan
   matched the confirmed plan.

## Alternatives Considered

### A. Timestamp-based versioning
- **Rejected**: Timestamps can be manipulated. Hashes provide cryptographic
  integrity guarantees.

### B. Database-backed provenance
- **Rejected**: Adds infrastructure dependency. File-based hashes are sufficient
  for the scale of this project (tens to hundreds of profiles).

### C. Git-based provenance (rely on git history)
- **Partially accepted**: Git history is a secondary provenance mechanism.
  Primary provenance must be content-addressable within the artifacts themselves,
  independent of git.

## Consequences

### Positive
- Complete audit trail from raw data to compensated command
- Tamper-evident: any modification to an artifact is detectable
- Enables deterministic replay of calibration decisions
- Supports regulatory or safety compliance requirements

### Negative
- Hash computation adds overhead to pipeline execution
- Artifact immutability means more storage (old artifacts retained)
- Requires discipline: all consumers must verify hashes

## Migration Impact

- Add hash fields to all domain objects in the provenance chain
- Existing K1 gold profile: compute and record hash, mark as immutable
- Update profile exporter to include provenance chain
- Update compensation logic to verify profile hash before use
- Add provenance verification to audit scripts

## Validation Requirements

- Gold profile hash is stable (re-computing gives same hash)
- Profile modification is detectable (hash mismatch)
- Provenance chain is verifiable end-to-end
- Compensation decisions include valid profile/model hashes
- Audit records include all required provenance references
