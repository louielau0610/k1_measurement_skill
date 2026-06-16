# M26-D Example Requests

Example requests live under `examples/calibration_skill/`.

Valid examples:

- `preflight_request.mock.json`
- `dry_run_velocity_command.mock.json`
- `dry_run_collect_telemetry.mock.json`
- `dry_run_stop.mock.json`
- `dry_run_end_to_end.mock.json`

Invalid examples:

- `invalid_real_platform_request.json`
- `invalid_dry_run_false_request.json`
- `invalid_missing_safety_request.json`

Validate all valid examples:

```powershell
py -3.12 -m calibration_skill.cli validate --input examples/calibration_skill/dry_run_end_to_end.mock.json
```

Invoke the full dry-run example:

```powershell
py -3.12 -m calibration_skill.cli invoke --input examples/calibration_skill/dry_run_end_to_end.mock.json --pretty
```

Invalid examples return deterministic rejected response envelopes. No example
contains machine-local paths, raw logs, gold profiles, or hardware connection
settings.
