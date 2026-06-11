"""Run an offline compensation sweep for one platform and surface."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import CompensationRequest
from calibration_core.velocity_compensation import DEFAULT_CONTRACT_CSV, DEFAULT_PROFILE, compensate_velocity

DEFAULT_DESIRED = [0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60]
DEFAULT_OUTPUT_PREFIX = Path("outputs/compensation_research/offline_k1_compensation_sweep")


def parse_velocities(text: str | None) -> list[float]:
    if not text:
        return DEFAULT_DESIRED
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def run_sweep(args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for desired in parse_velocities(args.desired_velocities):
        request = CompensationRequest(
            platform=args.platform,
            robot_model=args.robot_model,
            surface_type=args.surface,
            desired_actual_velocity_mps=desired,
            response_profile_path=args.profile,
            contract_csv_path=args.contract_csv,
            risk_policy=args.risk_policy,
            extrapolation_policy=args.extrapolation_policy,
            minimum_confidence=args.minimum_confidence,
            operator_notes="batch offline compensation sweep",
        )
        rows.append(compensate_velocity(request).to_dict())
    return rows


def write_outputs(rows: list[dict[str, object]], prefix: Path) -> dict[str, str]:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = prefix.with_suffix(".csv")
    json_path = prefix.with_suffix(".json")
    md_path = prefix.with_suffix(".md")
    fields = [
        "schema_version",
        "platform",
        "robot_model",
        "surface_type",
        "desired_actual_velocity_mps",
        "recommended_command_velocity_mps",
        "expected_actual_velocity_mps",
        "expected_tracking_error_mps",
        "expected_relative_error",
        "selected_segment",
        "region_label",
        "risk_score",
        "confidence",
        "feasibility_status",
        "reason",
        "offline_only",
        "physical_validation_status",
        "deployment_ready",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({"offline_prototype_only": True, "decisions": rows}, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(rows), encoding="utf-8")
    return {"csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)}


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Offline K1 Compensation Sweep",
        "",
        "Scope: offline prototype only. This is not physical validation and not deployment-ready compensation.",
        "",
        "| desired_actual_velocity_mps | recommended_command_velocity_mps | feasibility_status | reason |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['desired_actual_velocity_mps']} | {row['recommended_command_velocity_mps']} | "
            f"{row['feasibility_status']} | {row['reason']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", default="booster_k1")
    parser.add_argument("--robot-model", default="Booster K1")
    parser.add_argument("--surface", default="S1_lab_hard_floor")
    parser.add_argument("--desired-velocities", default=None)
    parser.add_argument("--risk-policy", choices=["conservative", "balanced", "permissive"], default="conservative")
    parser.add_argument("--extrapolation-policy", choices=["reject", "nearest_bound"], default="reject")
    parser.add_argument("--minimum-confidence", type=float, default=0.5)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--contract-csv", type=Path, default=DEFAULT_CONTRACT_CSV)
    parser.add_argument("--output-prefix", type=Path, default=DEFAULT_OUTPUT_PREFIX)
    args = parser.parse_args(argv)
    rows = run_sweep(args)
    outputs = write_outputs(rows, args.output_prefix)
    print(json.dumps({"offline_prototype_only": True, "not_physical_validation": True, "outputs": outputs}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
