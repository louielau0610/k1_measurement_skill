"""Build the M14 velocity response dataset v1 from Measurement v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.research_dataset_schema import load_velocity_response_schema
from k1_measurement.velocity_response_dataset_builder import (
    build_future_trial_template,
    build_validation_report,
    build_velocity_response_dataset_v1,
    validate_built_dataset,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build velocity response dataset v1 from Measurement v0 artifacts."
    )
    parser.add_argument("--measurement-root", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Reserved for optional missing artifacts; required root artifacts must still exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        dataset = build_velocity_response_dataset_v1(args.measurement_root, args.schema)
        schema = load_velocity_response_schema(args.schema)
        validation_errors = validate_built_dataset(dataset, schema)
        report = build_validation_report(
            dataset,
            validation_errors,
            args.output,
            args.schema,
            args.measurement_root,
        )
        template = build_future_trial_template(args.schema)

        if validation_errors:
            print(json.dumps(report, indent=2, ensure_ascii=False), file=sys.stderr)
            return 1

        write_json(args.output, dataset)
        write_json(args.report, report)
        write_json(args.template, template)

        summary: dict[str, Any] = {
            "milestone": "M14",
            "dataset_path": args.output,
            "validation_report_path": args.report,
            "future_trial_template_path": args.template,
            "records_count": dataset["records_count"],
            "validation_passed": True,
            "source_artifacts_used": dataset["source_artifacts_used"],
            "source_artifacts_missing": dataset["source_artifacts_missing"],
            "fabricated_values": False,
            "compensation_ready": False,
            "safe_command_adapter_ready": False,
            "navigation_warning_ready": True,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(json.dumps({"validation_passed": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
