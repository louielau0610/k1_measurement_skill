"""Generate a Markdown measurement report from a processed profile."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.report_generator import generate_report_from_profile


DEFAULT_PROFILE = Path("data/processed/dummy_processed_environment_profile.json")
DEFAULT_OUTPUT = Path("reports/dummy_measurement_report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a K1 measurement Markdown report.")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Input profile JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output Markdown report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"Profile not found: {profile_path}")
        print("Generate the dummy profile first:")
        print("py scripts/generate_dummy_raw_log.py")
        print("py scripts/process_trial_logs.py")
        return 2

    output_path = generate_report_from_profile(str(profile_path), args.output)
    print(f"Measurement report generated: {output_path}")
    print("If generated from dummy data, this report is not real K1 measurement data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
