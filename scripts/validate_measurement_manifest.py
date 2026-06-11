"""Validate a Measurement Module v1 artifact manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.measurement_manifest import load_manifest, validate_measurement_manifest

DEFAULT_MANIFEST = Path("outputs/measurement_v1/booster_k1_reference_manifest.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)
    summary = validate_measurement_manifest(manifest, ROOT, require_k1_reference=manifest.get("platform") == "booster_k1")
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"manifest: {args.manifest}")
        print(f"valid: {summary['valid']}")
        print(f"dataset_id: {summary['dataset_id']}")
        print(f"platform: {summary['platform']}")
        print(f"validation_status: {summary['validation_status']}")
        print(f"extracted_measurement_rows: {summary['extracted_measurement_rows']}")
        print(f"compensation_ready: {summary['compensation_ready']}")
        for error in summary["errors"]:
            print(f"error: {error}")
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
