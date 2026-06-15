"""Generate M25-R exploration/formal real-data collection packages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.m25_real_collection_preflight import write_collection_package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate M25-R collection package artifacts.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_real_collection_preflight_template.yaml"))
    parser.add_argument("--phase", choices=["exploration", "formal"], required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/full_range_velocity_profile"))
    args = parser.parse_args(argv)
    try:
        package, json_path, md_path = write_collection_package(args.config, args.phase, args.output_dir)
    except Exception as exc:
        print(json.dumps({"ready": False, "errors": [{"code": "package_generation_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps({"ready": package["ready"], "json": str(json_path), "markdown": str(md_path)}, indent=2))
    return 0 if package["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
