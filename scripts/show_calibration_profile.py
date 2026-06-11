"""Show a calibration profile summary for a registered platform."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.platform_registry import get_platform
from calibration_core.profile_loader import K1_GOLD_PROFILE, load_k1_gold_profile


def profile_for_platform(platform_id: str, profile_path: Path | None = None) -> dict[str, object]:
    entry = get_platform(platform_id)
    if platform_id != "booster_k1":
        return {
            "platform_id": platform_id,
            "robot_model": entry.robot_model,
            "profile_available": False,
            "hardware_validated_reference": entry.hardware_validated_reference,
            "claim_boundary": "scaffold only; no platform profile or empirical validation",
        }
    profile = load_k1_gold_profile(profile_path or K1_GOLD_PROFILE)
    return {
        "platform_id": platform_id,
        "robot_model": entry.robot_model,
        "profile_available": True,
        "hardware_validated_reference": entry.hardware_validated_reference,
        **profile,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", default="booster_k1")
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    summary = profile_for_platform(args.platform, args.profile)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"platform_id: {summary['platform_id']}")
        print(f"robot_model: {summary['robot_model']}")
        print(f"hardware_validated_reference: {summary['hardware_validated_reference']}")
        print(f"profile_available: {summary['profile_available']}")
        if summary["profile_available"]:
            print(f"robot_id: {summary['robot_id']}")
            print(f"tested_surfaces: {', '.join(summary['tested_surfaces'])}")
            print(f"speed_list: {', '.join(str(speed) for speed in summary['speed_list'])}")
            print(f"region_label_count: {len(summary['region_labels'])}")
        else:
            print(f"claim_boundary: {summary['claim_boundary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
