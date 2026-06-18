# M27-D: K1 Hardware Evidence Contract

## Purpose

Defines the structured evidence artifacts produced by M27-D bench sessions
and the contract they must fulfill for downstream consumption.

## Required Artifacts

| Artifact | Format | Purpose |
|----------|--------|---------|
| `m27d_manifest.json` | JSON object | Session identification and metadata |
| `m27d_gate_evidence.json` | JSON object | Hardware gate configuration and validation evidence |
| `m27d_sdk_detection.json` | JSON object | SDK detection without import evidence |
| `m27d_runtime_trace.jsonl` | JSONL (one object per line) | Sequenced trace of all runtime events |
| `m27d_telemetry_snapshot.json` | JSON object | Snapshot of robot telemetry at bench time |
| `m27d_result_summary.json` | JSON object | Final bench result with status and errors |

## Trace Event Schema

Each line in `m27d_runtime_trace.jsonl`:

```json
{
  "event_sequence": 1,
  "event_type": "connect",
  "monotonic_ns": 1234567890,
  "success": true,
  "structured_error": null,
  "evidence_reference": "m27d-bench-2026-06-18"
}
```

## Result Summary Schema

```json
{
  "status": "bench_passed",
  "evidence_reference": "m27d-bench-2026-06-18",
  "started_at": "2026-06-18T12:00:00Z",
  "finished_at": "2026-06-18T12:00:05Z",
  "errors": []
}
```

## Prohibited Content

Artifacts must NOT contain:
- Secrets, passwords, tokens, or credentials
- Network credentials or connection strings
- Raw SDK object representations (e.g., `<B1LocoClient object at 0x...>`)
- Memory addresses
- Uncontrolled Python tracebacks
- Personal data

## Determinism

Artifact generation must be deterministic when using:
- Injected clock functions (fixed monotonic timestamps)
- Fake vendor bindings (no hardware variance)

## Immutability

Once written, artifacts must not be modified by subsequent bench runs.
Each bench session writes to a unique output directory.
