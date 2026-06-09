"""Build the M11 real K1 velocity profile contract artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.velocity_profile import (
    DEFAULT_ANALYSIS_SUMMARY_JSON,
    DEFAULT_FIELD_TEST_YAML,
    build_velocity_profile,
    load_json,
    load_yaml,
    write_json,
)


DEFAULT_OUTPUT_PROFILE = "outputs/real_k1_field_tests/real_k1_velocity_profile_v0.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build real K1 velocity profile v0.")
    parser.add_argument("--field-test-yaml", default=DEFAULT_FIELD_TEST_YAML)
    parser.add_argument("--analysis-summary-json", default=DEFAULT_ANALYSIS_SUMMARY_JSON)
    parser.add_argument("--output-profile", default=DEFAULT_OUTPUT_PROFILE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    field_test_yaml = Path(args.field_test_yaml)
    analysis_summary_json = Path(args.analysis_summary_json)
    if not field_test_yaml.exists():
        raise FileNotFoundError(f"missing field test YAML: {field_test_yaml}")
    if not analysis_summary_json.exists():
        raise FileNotFoundError(f"missing analysis summary JSON: {analysis_summary_json}")

    profile = build_velocity_profile(
        load_yaml(field_test_yaml),
        load_json(analysis_summary_json),
        field_test_yaml_path=args.field_test_yaml,
        analysis_summary_json_path=args.analysis_summary_json,
    )
    write_json(args.output_profile, profile)
    print(f"Output profile: {args.output_profile}")
    print(
        "First effective observed command speed: "
        f"{profile['profile_thresholds']['first_effective_observed_vx_cmd_mps']} m/s"
    )
    print(
        "Stable tracking observed speed: "
        f"{profile['profile_thresholds']['stable_tracking_observed_vx_cmd_mps']} m/s"
    )
    print(f"Compensation ready: {profile['downstream_usage']['compensation_ready']}")
    print(f"Navigation warning ready: {profile['downstream_usage']['navigation_warning_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
