# M26-B Serialization Policy

**Status**: Implemented
**Milestone**: M26-B / M26-BR
**Version**: 1.0.0

## Encoding

- **Character encoding**: UTF-8. All JSON text is UTF-8 encoded.
- **No BOM**: Byte order marks are not emitted.

## Canonical JSON Rules

Canonical JSON is used for content digest generation. The rules are:

1. **Key ordering**: Object keys are sorted lexicographically by Unicode code
   point (Python's `sort_keys=True`).
2. **Whitespace**: No whitespace outside string literals. `separators=(",", ":")`
   — no spaces after commas or colons.
3. **Number format**: Python's default `json.dumps` float representation.
   Numbers that are exactly integers are represented without a decimal point
   (e.g., `1` not `1.0`).
4. **String escaping**: Non-ASCII characters are emitted literally
   (`ensure_ascii=False`). Control characters use standard JSON escapes.
5. **Trailing data**: No trailing content after the root JSON value.

## Number Handling

- **NaN**: Rejected. `math.isnan()` check before serialization.
- **Infinity**: Rejected. `math.isinf()` check before serialization.
- **Negative zero**: Python's `json.dumps` represents `-0.0` as `-0.0`. This is
  preserved.
- **Integer monotonic time**: All monotonic timestamps are `int` (not `float`).
  They serialize as JSON integers without decimal points.

## Null vs Omitted Fields

- **Omitted**: Field is not present in the JSON object. Means "not provided" or
  "not applicable".
- **Null** (`json null`): Field is present with value `null`. Means "explicitly
  absent" or "known to be unavailable".
- Codecs use omission (not null) for optional unset fields.
- Consumers must distinguish between missing keys and null values.

## Enum Serialization

- All enums serialize as their `.value` — stable lowercase strings.
- Example: `CoordinateFrame.BODY` → `"body"`.
- Enum values are NOT ordinal integers.
- Unknown enum values during deserialization raise `ValueError` from the enum
  constructor.

## Digest Generation

- **Algorithm**: SHA-256.
- **Input**: UTF-8 encoded canonical JSON bytes of the object's `to_dict()`
  output.
- **Output**: Lowercase hex string (64 characters).
- **Scope**: The digest covers the object's own fields, not referenced objects.
- **Identical objects produce identical digests**: Two `CalibrationProfile`
  instances with the same field values produce the same digest.
- **Different key order produces same digest**: Because canonical JSON sorts
  keys, `{"b":2,"a":1}` and `{"a":1,"b":2}` produce the same canonical bytes
  and the same digest.
- **Different list order DOES produce different digests**: List ordering is
  semantically significant unless a field is explicitly documented as
  order-insensitive. `{"items":[1,2]}` and `{"items":[2,1]}` produce different
  digests.

## Canonical Digest Test Vectors

### Example 1: Key order invariance

Input A (insertion order: b, a):
```json
{"b": 2, "a": 1}
```

Input B (insertion order: a, b):
```json
{"a": 1, "b": 2}
```

Both produce the same canonical bytes:
```
{"a":1,"b":2}
```

Both produce the same SHA-256 digest:
```
ea9c4a7b7c1e5a1f2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5
```

### Example 2: List order sensitivity

Input A:
```json
{"items": [1, 2]}
```

Input B:
```json
{"items": [2, 1]}
```

These produce different canonical bytes and different digests. List order is
preserved as-is during canonical serialization.

Only fields explicitly defined as order-insensitive (e.g., via sorted-tuple
internal representation) produce consistent digests regardless of insertion
order.

## Nested Mapping Ordering

- Nested objects are recursively sorted by key.
- The rule applies at every level of nesting, not just the top level.

## List Ordering

- Lists preserve their element order.
- If a field's semantics are order-insensitive, the codec implementation sorts
  the list before serialization. This must be documented per-field.

## Metadata Policy

- The `metadata` field on `RobotIdentity` is serialized as a JSON object with
  keys sorted for canonical output.
- Extra fields in `ConnectionConfig.extra` are serialized as-is without
  reordering (platform-specific semantics).

## Schema Version Inclusion

- Schema versions are included in the `schema_version` field of envelope
  objects (`skill_request`, `skill_response`).
- Domain value objects do not include `schema_version` in their `to_dict()`
  output; versioning is handled at the envelope level.

## Object Type Inclusion

- Domain objects do not include a `type` discriminator field in their
  `to_dict()` output.
- Envelope objects (`skill_request`, `skill_response`) include `operation`
  and `status` fields for routing.

## Deterministic Round-Trip Expectations

For codec pairs (encode + decode):
- `decode(encode(obj))` produces an object semantically equivalent to `obj`.
- Field values are preserved exactly (no precision loss for floats within
  IEEE 754 double representation).
- Enum round-trips: `RobotPlatform("booster_k1")` → `"booster_k1"` →
  `RobotPlatform.BOOSTER_K1`.

## Cross-Process Monotonic Clock Limitation

Monotonic timestamps (`*_monotonic_ns` fields) use `time.monotonic_ns()`.

**These timestamps CANNOT be compared across processes** unless the runtime
establishes an explicit clock relationship between the processes.

Do not:
- Compare `issued_monotonic_ns` from process A with `received_monotonic_ns`
  from process B and draw ordering conclusions.
- Store monotonic timestamps and compare them across process restarts.

Within a single process, monotonic timestamps are strictly increasing and
suitable for timeout, expiry, and freshness calculations.

## Implementation Reference

- `calibration_skill/schemas/codec.py` — `canonical_json_dumps()`
- `calibration_skill/domain/calibration.py` — `_canonical_json()`, `_content_digest()`
