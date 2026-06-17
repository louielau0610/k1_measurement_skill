# M27-C Future Booster SDK Integration

The ordinary `calibration-skill` package remains no-vendor. M27-C adds a
placeholder optional extra named `booster-k1`, but it intentionally contains no
dependency because there is no stable package dependency selected for this
repository milestone.

Future M27-D bench integration must provide:

- a documented Booster SDK installation environment
- a hardware-gated bench procedure
- operator and physical-estop confirmation evidence
- network isolation confirmation
- adapter-mode separation between fake runtime and vendor runtime
- tests that remain excluded from ordinary no-hardware CI

The future real runtime should live behind the existing fail-closed
`vendor_runtime.py` boundary or a module with the same isolation properties. It
must not be imported by default CLI, default registry composition, or ordinary
contract tests.

Until M27-D, Booster K1 support remains fake-runtime-only in the new
`calibration_skill` runtime.
