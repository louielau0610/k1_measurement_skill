# M26-D CLI JSON I/O Contract

## Commands

```powershell
py -3.12 -m calibration_skill.cli manifest
py -3.12 -m calibration_skill.cli operations
py -3.12 -m calibration_skill.cli validate --input request.json
py -3.12 -m calibration_skill.cli invoke --input request.json
py -3.12 -m calibration_skill.cli invoke --input - --output -
py -3.12 -m calibration_skill.cli examples --operation dry_run_end_to_end
```

`--input -` reads stdin. `--output -` writes stdout. File output is atomic and
requires the parent directory to exist unless `--create-dirs` is supplied. The
CLI writes machine-readable JSON to stdout for stdout mode and human diagnostics
to stderr.

## Determinism

Compact mode uses canonical key ordering and no extra whitespace. Pretty mode
also sorts keys. Identical request inputs produce identical CLI responses for
the mock dry-run runtime.

## Exit Codes

- `0`: success
- `1`: request rejected by skill contract
- `2`: CLI usage error
- `3`: malformed input JSON
- `4`: output write failure
- `5`: internal error
- `6`: hermeticity or forbidden runtime violation if detected

## Validation Boundary

`validate` checks the existing skill request schema plus M26-D gates: supported
operation, `dry_run=true`, `platform=mock`, and command safety payload
requirements. It does not create an adapter for schema-version failures.

`invoke` uses the M26-C `SkillService`; every response remains compatible with
the existing `skill_response.schema.json`.
