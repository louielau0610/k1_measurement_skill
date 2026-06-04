"""Dry-run entry point for the v0 forward baseline plan."""

from __future__ import annotations

from k1_measurement.command_runner import CommandRunner, VelocityCommand


def main() -> int:
    runner = CommandRunner(dry_run=True)
    for vx in [0.1, 0.2, 0.3, 0.4]:
        result = runner.run(VelocityCommand(vx_mps=vx))
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
