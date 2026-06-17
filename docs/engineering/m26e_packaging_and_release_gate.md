# M26-E Packaging and Release Gate

M26-E turns the hardware-free `calibration_skill` CLI into a local Python package artifact. It does not start K1 migration, does not add G1 or GO1 runtime adapters, and does not connect to hardware.

## Package Metadata

- Package name: `calibration-skill`
- Python package: `calibration_skill`
- Runtime dependency: `jsonschema>=4.18`
- Console script: `calibration-skill = calibration_skill.cli:main`
- Package data: `calibration_skill/schemas/v1/*.schema.json` and `calibration_skill/skill/manifest.schema.json`

Excluded from the package metadata are raw robot logs, historical `outputs/`, `data/`, platform adapter packages, vendor SDK binaries, local virtual environments, build artifacts, and secrets.

## Console Script

The console script exposes only the mock dry-run skill CLI:

```powershell
calibration-skill manifest
calibration-skill operations
calibration-skill examples --operation dry_run_end_to_end
calibration-skill validate --input examples/calibration_skill/dry_run_end_to_end.mock.json
calibration-skill invoke --input examples/calibration_skill/dry_run_end_to_end.mock.json
```

The equivalent module entry point remains:

```powershell
py -3.12 -m calibration_skill.cli manifest
```

No physical robot command is exposed by this entry point.

## Hermetic Runner

`scripts/run_tests_hermetically.py` checks `git status --porcelain=v1`, rejects an initially dirty repository, runs a supplied command after `--` or defaults to `py -3.12 -m pytest tests/ --tb=no -q`, captures stdout/stderr/return code, checks final porcelain status, and fails if the repository changed.

Exit codes:

- `0`: child command passed and the repository stayed clean
- `1`: child command failed
- `2`: repository was dirty before the command
- `3`: repository mutated during the command
- `4`: usage or internal error

The runner never restores files automatically and does not call checkout, restore, reset, or clean commands.

## Local Release Gate

`scripts/run_local_release_gate.py` runs checks in this order:

1. repository initially clean
2. engineering artifact validation
3. compileall
4. targeted calibration skill tests
5. full suite through the hermetic runner
6. CLI manifest smoke test
7. CLI examples smoke test
8. packaging metadata validation
9. wheel and sdist build if `python -m build` is available
10. built artifact inspection when artifacts are built
11. temporary virtual environment install smoke where practical
12. no-vendor SDK import check
13. final repository clean check

Use:

```powershell
py -3.12 scripts/run_local_release_gate.py --summary outputs/engineering/m26e_release_gate_summary.json
```

If the `build` module is absent, the build step is recorded as `skipped_missing_dependency`; wheel and sdist verification are not claimed.

## Boundary

M26-E remains a local pre-release gate only. It does not publish to PyPI or any external registry, and it does not claim stable public release readiness or hardware verification.
