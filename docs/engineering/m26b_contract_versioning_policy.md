# M26-B Contract Versioning Policy

**Status**: Implemented
**Milestone**: M26-B / M26-BR
**Version**: 1.0.0

## Initial Version

All external contracts begin at version `1.0.0`. The schema version is embedded
in every JSON Schema document via the `$id` URN and in the `schema_version`
property of request/response envelopes.

## Schema Version vs Package Version

- **Schema version** (`1.0.0`): Tracks the external contract. Embedded in schema
  `$id` (e.g., `urn:calibration-skill:schema:velocity_command:v1`) and in
  envelope `schema_version` fields.
- **Package version** (`0.1.0`): Tracks the Python package release. Independent
  of schema versions. Multiple schema versions may coexist within one package
  release.

Schema versions use SemVer: `MAJOR.MINOR.PATCH`.

## Compatible Additive Changes (PATCH or MINOR bump)

The following changes are considered backward-compatible and may be introduced
with a MINOR or PATCH version bump:

1. **Adding a new optional field** to an existing object. Existing consumers
   ignore unknown fields (see unknown-field policy). New consumers may use the
   field if present.

2. **Adding a new value to an existing enum** — **WITH CAUTION**. While the
   JSON structure is unchanged, consumers that perform exhaustive matching on
   enum values may break. Such additions require a MINOR version bump and must
   be documented in release notes. Consumers SHOULD handle unknown enum values
   gracefully (see unknown-enum policy).

3. **Relaxing a constraint** (e.g., increasing a maximum, decreasing a minimum,
   making a required field optional). Existing valid payloads remain valid.

4. **Adding a new schema** to the registry. New schemas do not affect existing
   consumers.

## Required Field Addition Rules

Adding a new **required** field is a **breaking change** and requires a MAJOR
version bump. Existing payloads without the field will fail validation.

## Enum Extension Rules

Adding a new enum value:

- Is **not automatically backward-compatible**.
- Requires a MINOR version bump at minimum.
- Must be documented with the note: "Consumers performing exhaustive enum
  matching may need updating."
- Consumers SHOULD handle unknown enum values by treating them as equivalent to
  a documented fallback (e.g., `unknown`), not by crashing.

## Unknown-Field Policy

By default, all v1 schemas use `"additionalProperties": false`. This means:

- **Unknown fields are rejected** during validation.
- Adding a new field to a schema is a breaking change for that schema's
  consumers unless the schema is updated first.

If a future schema version chooses `"additionalProperties": true` or uses
`unevaluatedProperties`, the policy for that schema must be documented
individually.

## Unknown-Enum Policy

When a consumer encounters an enum value not in its known set:

- The consumer SHOULD NOT crash.
- The consumer SHOULD treat the value as semantically equivalent to a defined
  fallback value (typically the `unknown` variant, if one exists).
- The consumer MAY log a warning.
- The consumer MUST NOT silently misinterpret the value as a different known
  enum member.

## Deprecation Process

1. A field, enum value, or schema is marked as deprecated in documentation.
2. Deprecated items remain valid for at least one MINOR version cycle.
3. Deprecated items are removed only in a MAJOR version bump.
4. Deprecation notices include the planned removal version.

## Breaking-Change Criteria

The following are **breaking changes** requiring a MAJOR version bump:

1. Removing a field (required or optional).
2. Making an optional field required.
3. Narrowing a constraint (reducing a maximum, increasing a minimum).
4. Removing an enum value.
5. Changing the type of a field.
6. Changing the semantics of a field without changing its name.
7. Changing the `$id` of a schema.
8. Changing `additionalProperties` from `true` to `false`.
9. Removing a schema from the registry.

## Major-Version Migration

When a MAJOR version is introduced (e.g., `v2`):

1. The new schema lives under a new directory (`schemas/v2/`).
2. The old schema remains available under `schemas/v1/`.
3. Both versions coexist in the schema registry.
4. Consumers declare which version they accept via `schema_version` in requests.
5. Producers include `schema_version` in responses so consumers can identify the version.

## Reader/Writer Compatibility

- **Writers** produce payloads conforming to a specific schema version.
- **Readers** accept payloads conforming to a declared schema version or a
  compatible newer version.
- A reader that only understands v1 MUST reject a v2 payload with
  `schema_version_unsupported`, not attempt to parse it.

## Profile and Audit-Record Retention

- Calibration profiles are immutable once published (status `gold`).
- Profiles retain the schema version under which they were created.
- Audit records retain the schema version of the session that produced them.
- Old profiles and audit records are not retroactively validated against new
  schema versions.

## Minimum Support Window

- Each MAJOR schema version is supported for at least **two subsequent MAJOR
  versions** after its successor is introduced.
- Example: when v3 is introduced, v1 may be removed; v2 remains supported.

## Schema Registry Behavior

- `SCHEMA_REGISTRY` in `schemas/registry.py` is the authoritative source of
  registered schemas.
- Unknown schema IDs produce `schema_version_unsupported` errors.
- Schema lookup is by `schema_id` string, not by URN.

## Unsupported-Version Error Behavior

When a consumer requests or receives an unsupported schema version:

1. The error code `schema_version_unsupported` is returned.
2. The error details include the requested version and the supported versions.
3. The operation is aborted — no partial processing occurs.
