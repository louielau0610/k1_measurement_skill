"""List registered calibration platforms."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.platform_registry import list_platforms


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)
    entries = [entry.summary() for entry in list_platforms()]
    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        for entry in entries:
            validated = "hardware_validated_reference=true" if entry["hardware_validated_reference"] else "hardware_validated_reference=false"
            print(f"{entry['platform_id']}: {entry['robot_model']} [{entry['validation_status']}, {validated}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
