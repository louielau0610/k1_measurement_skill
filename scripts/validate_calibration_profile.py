"""Validate a calibration profile without creating empirical claims."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.measurement_schema import validate_aggregate_record

REQUIRED_PROFILE_KEYS = {
    "robot_id",
    "dataset_id",
    "surfaces",
    "speeds",
    "per_surface_response_statistics",
    "region_labels",
    "recommended_reliable_ranges",
    "deadzone_ranges",
    "drift_prone_ranges",
    "limitations",
}


def validate_profile(path: Path) -> dict[str, Any]:
    errors = []
    profile = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_PROFILE_KEYS - set(profile))
    if missing:
        errors.append(f"missing profile keys: {', '.join(missing)}")
    rows = profile.get("per_surface_response_statistics", [])
    if not isinstance(rows, list):
        errors.append("per_surface_response_statistics must be a list")
        rows = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"statistic row {index} is not an object")
            continue
        normalized = {
            "robot_model": profile.get("robot_id", ""),
            "surface_type": row.get("surface_type", row.get("surface_id", "")),
            **row,
        }
        for row_error in validate_aggregate_record(normalized):
            errors.append(f"statistic row {index}: {row_error}")
    region_labels = profile.get("region_labels", {})
    if not isinstance(region_labels, dict) or not region_labels:
        errors.append("region_labels must be a non-empty object")
    return {
        "profile": str(path),
        "valid": not errors,
        "errors": errors,
        "aggregate_rows": len(rows),
        "region_label_count": len(region_labels) if isinstance(region_labels, dict) else 0,
        "empirical_analysis_generated": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    summary = validate_profile(args.profile)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"profile: {summary['profile']}")
        print(f"valid: {summary['valid']}")
        print(f"aggregate_rows: {summary['aggregate_rows']}")
        print(f"region_label_count: {summary['region_label_count']}")
        for error in summary["errors"]:
            print(f"error: {error}")
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
