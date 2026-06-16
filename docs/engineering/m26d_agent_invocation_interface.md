# M26-D Agent Invocation Interface

M26-D exposes the mock-only calibration skill through a deterministic JSON CLI.
Agents invoke it with:

```powershell
py -3.12 -m calibration_skill.cli invoke --input request.json --output -
```

Stdin/stdout invocation is supported:

```powershell
Get-Content request.json -Raw | py -3.12 -m calibration_skill.cli invoke --input - --output -
```

The CLI supports exactly these operations:

- `preflight`
- `dry_run_velocity_command`
- `dry_run_collect_telemetry`
- `dry_run_stop`
- `dry_run_end_to_end`

All operations require `dry_run: true` and `platform: "mock"`. Real platforms
are rejected by contract. M26-D does not migrate K1, implement G1/GO1, connect
to hardware, open sockets, start DDS, send UDP, or import vendor SDK runtimes.

Responses are `skill_response.schema.json`-compatible envelopes. Python
tracebacks are not exposed by default; pass `--show-traceback` only for local
developer debugging.
