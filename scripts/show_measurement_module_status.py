"""Show Measurement Module v1 status."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_STATUS = Path("outputs/measurement_v1/measurement_module_status.json")


def load_status(path: Path = DEFAULT_STATUS) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    status = load_status(args.status)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"measurement_module_v1_status: {status['measurement_module_v1_status']}")
        print("available_reference_datasets:")
        for dataset in status.get("available_reference_datasets", []):
            print(f"- {dataset['platform']}: {dataset['dataset_id']} ({dataset['manifest_path']})")
        print(f"validated_platforms: {', '.join(status.get('validated_platforms', []))}")
        print(f"scaffold_only_platforms: {', '.join(status.get('scaffold_only_platforms', []))}")
        print(f"velocity_compensation_ready: {status['velocity_compensation_ready']}")
        print(f"next_required_step: {status['next_required_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
