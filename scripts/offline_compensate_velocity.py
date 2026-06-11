"""Run the offline velocity compensator prototype and print a JSON decision."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import CompensationRequest
from calibration_core.velocity_compensation import DEFAULT_CONTRACT_CSV, DEFAULT_PROFILE, compensate_velocity


def build_request(args: argparse.Namespace) -> CompensationRequest:
    return CompensationRequest(
        platform=args.platform,
        robot_model=args.robot_model,
        surface_type=args.surface,
        desired_actual_velocity_mps=args.desired_velocity,
        response_profile_path=args.profile,
        contract_csv_path=args.contract_csv,
        risk_policy=args.risk_policy,
        extrapolation_policy=args.extrapolation_policy,
        minimum_confidence=args.minimum_confidence,
        operator_notes=args.operator_notes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--robot-model", default="Booster K1")
    parser.add_argument("--surface", required=True)
    parser.add_argument("--desired-velocity", type=float, required=True)
    parser.add_argument("--risk-policy", choices=["conservative", "balanced", "permissive"], default="conservative")
    parser.add_argument("--extrapolation-policy", choices=["reject", "nearest_bound"], default="reject")
    parser.add_argument("--minimum-confidence", type=float, default=0.5)
    parser.add_argument("--operator-notes", default="")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--contract-csv", type=Path, default=DEFAULT_CONTRACT_CSV)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    decision = compensate_velocity(build_request(args)).to_dict()
    text = json.dumps(decision, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
