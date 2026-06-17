# M26-E Distribution Readiness

M26-E distribution readiness is limited to local packaging and local release-gate evidence for the dry-run skill.

## Included

- `calibration_skill` Python package
- dry-run CLI and operation catalog
- versioned JSON schemas under `calibration_skill/schemas/v1/`
- manifest schema under `calibration_skill/skill/manifest.schema.json`
- package metadata in `pyproject.toml`
- local release scripts under `scripts/`
- focused M26-E tests under `tests/calibration_skill/`

## Excluded

- raw robot logs and measurement sessions
- historical M19/M24 outputs
- gold profiles and raw measurement data
- `platforms/` runtime adapters
- Booster SDK, Unitree SDK2, `unitree_legged_sdk`, ROS2, DDS, or vendor binaries
- `dist/`, build caches, virtual environments, and machine-local paths

## Build Behavior

When `python -m build` is installed, the local release gate builds wheel and sdist artifacts into a temporary output directory and inspects them for required schema files and excluded high-risk paths. The repository does not commit `dist/` artifacts.

When `python -m build` is unavailable, M26-E records the build check as `skipped_missing_dependency` and marks wheel and sdist verification as not verified due to missing build tooling. The gate still validates packaging metadata, tests, CLI smoke behavior, install smoke where practical, and no-vendor runtime behavior.

## Install Smoke

The release gate creates a temporary virtual environment with system site packages, installs the package in editable mode with `--no-deps`, and runs both the module CLI and console script. This avoids internet dependency resolution while still proving that package metadata exposes the local entry points.

## Readiness Status

M26-E readiness is `pre_release_only`. It supports local engineering validation but is not a final or stable public release.

Future K1, G1, and GO1 adapters should be packaged separately or as optional extras with explicit dependencies and separate hardware gates. They must not become mandatory dependencies of the dry-run package.
