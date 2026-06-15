"""Audit historical measurement rows for M25 full-range compatibility."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.full_range_velocity_profile import M25ValidationError, audit_historical_rows, load_config


DEFAULT_HISTORICAL = [
    Path("outputs/real_k1_validation_m19/repeated_validation_table.csv"),
    Path("data/compensation_experiments/m24b_s2_profile_refresh/m24b_s2_profile_refresh_clean_20260612_145358/corrected_extracted_results.csv"),
    Path("data/compensation_experiments/m24h_controlled_s2_replication/m24h_controlled_s2_replication_clean_20260612_171419/corrected_extracted_results.csv"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit historical rows for M25 compatibility.")
    parser.add_argument("--config", type=Path, default=Path("configs/m25_full_range_velocity_profile_template.yaml"))
    parser.add_argument("--input", type=Path, action="append", dest="inputs")
    parser.add_argument("--output", type=Path, default=Path("outputs/full_range_velocity_profile/m25_historical_compatibility_audit.json"))
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = audit_historical_rows(args.inputs or DEFAULT_HISTORICAL, config.valid_speed_domain)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except (OSError, M25ValidationError, ValueError) as exc:
        print(json.dumps({"status": "failed", "errors": [{"code": "historical_audit_failed", "message": str(exc)}]}), file=sys.stderr)
        return 2
    print(json.dumps({"status": "ok", "output": str(args.output), "valid_speed_rows_retained": result["valid_speed_rows_retained"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
