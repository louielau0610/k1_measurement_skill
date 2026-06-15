"""Build a dry-run M25 candidate full-range velocity profile from collected rows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import M25ValidationError, build_candidate_profile, load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an M25 candidate full-range velocity profile.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs/full_range_velocity_profile/m25_candidate_profile.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        profile = build_candidate_profile(args.session, config)
        if not args.dry_run:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    except (OSError, M25ValidationError, ValueError) as exc:
        print(json.dumps({"status": "failed", "errors": [{"code": "candidate_profile_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps({"status": profile["profile_status"], "dry_run": args.dry_run, "output": None if args.dry_run else str(args.output), "profile": profile}, indent=2))
    return 0 if profile["profile_status"] in {"candidate", "planned"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
