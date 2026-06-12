"""Run the M23-E revised offline velocity compensator and print JSON."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.revised_velocity_compensation import (  # noqa: E402
    DEFAULT_CONTRACT_CSV,
    DEFAULT_M23C_PAIR_CSV,
    DEFAULT_PROFILE,
    RevisedCompensationRequest,
    decision_to_json,
    revised_compensate_velocity,
)


def build_request(args: argparse.Namespace) -> RevisedCompensationRequest:
    return RevisedCompensationRequest(
        platform=args.platform,
        robot_model=args.robot_model,
        surface_type=args.surface,
        desired_actual_velocity_mps=args.desired_velocity,
        response_profile_path=args.profile,
        contract_csv_path=args.contract_csv,
        physical_context_csv_path=args.physical_context_csv,
        risk_policy=args.risk_policy,
        extrapolation_policy=args.extrapolation_policy,
        minimum_confidence=args.minimum_confidence,
        direct_error_good_enough_mps=args.direct_error_good_enough_mps,
        minimum_expected_benefit_mps=args.minimum_expected_benefit_mps,
        max_correction_mps=args.max_correction_mps,
        profile_mismatch_threshold_mps=args.profile_mismatch_threshold_mps,
        allow_clamping=args.allow_clamping,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--robot-model", default="Booster K1")
    parser.add_argument("--surface", required=True)
    parser.add_argument("--desired-velocity", type=float, required=True)
    parser.add_argument("--risk-policy", choices=["conservative", "balanced", "permissive"], default="permissive")
    parser.add_argument("--extrapolation-policy", choices=["reject", "nearest_bound"], default="reject")
    parser.add_argument("--minimum-confidence", type=float, default=0.0)
    parser.add_argument("--direct-error-good-enough-mps", type=float, default=0.02)
    parser.add_argument("--minimum-expected-benefit-mps", type=float, default=0.02)
    parser.add_argument("--max-correction-mps", type=float, default=0.05)
    parser.add_argument("--profile-mismatch-threshold-mps", type=float, default=0.03)
    parser.add_argument("--allow-clamping", action="store_true")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--contract-csv", type=Path, default=DEFAULT_CONTRACT_CSV)
    parser.add_argument("--physical-context-csv", type=Path, default=DEFAULT_M23C_PAIR_CSV)
    args = parser.parse_args(argv)

    decision = revised_compensate_velocity(build_request(args))
    print(decision_to_json(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
