"""Run or dry-run a Booster K1 measurement session.

Default: dry-run only, prints trial plan, creates no hardware movement.
Execution requires explicit --execute and per-trial permit by default.

Usage:
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute --no-permit
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platforms.booster_k1.measurement_runner import BoosterK1MeasurementRunner
from platforms.booster_k1.session import BoosterK1Session

DEFAULT_SURFACES = ["S1_lab_hard_floor", "S2_marble_floor", "S3_artificial_turf"]
DEFAULT_SPEEDS = [0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
DEFAULT_REPEATS = 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run or dry-run a Booster K1 measurement session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default, safe)
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor

  # Execute with per-trial permit
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --execute

  # Custom speeds and repeats
  python scripts/run_booster_k1_measurement.py --surface S1_lab_hard_floor --speeds 0.2 0.4 0.6 --repeats 2 --execute
        """,
    )
    parser.add_argument(
        "--surface",
        default="S1_lab_hard_floor",
        help="Surface identifier (default: S1_lab_hard_floor)",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Custom session ID (auto-generated if not provided)",
    )
    parser.add_argument(
        "--interface",
        default="ros2_odometer",
        help="Measurement interface (default: ros2_odometer)",
    )
    parser.add_argument(
        "--speeds",
        nargs="*",
        type=float,
        default=None,
        help="Command velocities in m/s (default: 0.1 0.2 0.3 0.35 0.4 0.45 0.5 0.6)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help=f"Number of repeats per surface-speed cell (default: {DEFAULT_REPEATS})",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Execute hardware movement (default: dry-run only)",
    )
    parser.add_argument(
        "--no-permit",
        action="store_true",
        default=False,
        help="Disable per-trial permit prompt (default: permit enabled)",
    )
    parser.add_argument(
        "--base-dir",
        default="data/measurement_sessions/booster_k1",
        help="Base directory for session data",
    )

    args = parser.parse_args(argv)

    # Validate surface
    surface = args.surface
    if surface not in DEFAULT_SURFACES:
        print(f"Warning: surface '{surface}' is not one of the known surfaces: {DEFAULT_SURFACES}")
        print("Continuing with custom surface identifier.")

    speeds = args.speeds if args.speeds else DEFAULT_SPEEDS
    permit = not args.no_permit

    # Build session
    session = BoosterK1Session(
        session_id=args.session_id,
        surface=surface,
        speeds=speeds,
        repeats=args.repeats,
        base_dir=Path(args.base_dir),
    )

    # Write session metadata
    metadata_path = session.write_metadata()
    print(f"Session metadata: {metadata_path}")

    # Build runner
    runner = BoosterK1MeasurementRunner(
        session=session,
        execute=args.execute,
        permit=permit,
        interface=args.interface,
    )

    # Run
    result = runner.run(surfaces=[surface])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
