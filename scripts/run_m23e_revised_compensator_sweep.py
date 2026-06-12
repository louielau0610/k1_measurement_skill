"""Run the M23-E revised offline compensator sweep.

No hardware is executed. This sweep replays the M23-C target velocities with
M23-C physical context so the revised logic can avoid the known failure mode.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import SUPPORTED_EMPIRICAL_PLATFORM  # noqa: E402
from calibration_core.revised_velocity_compensation import (  # noqa: E402
    DEFAULT_M23C_PAIR_CSV,
    RevisedCompensationRequest,
    revised_compensate_velocity,
)

DEFAULT_OUTPUT_DIR = Path("outputs/compensation_experiments")
DEFAULT_VELOCITIES = [0.40, 0.45, 0.50, 0.55]

SWEEP_FIELDS = [
    "desired_actual_velocity_mps",
    "identity_command_velocity_mps",
    "candidate_compensated_command_velocity_mps",
    "final_command_velocity_mps",
    "expected_direct_error_mps",
    "expected_compensated_error_mps",
    "expected_benefit_mps",
    "benefit_gate_passed",
    "correction_magnitude_mps",
    "correction_limited",
    "profile_mismatch_suspected",
    "feasibility_status",
    "reason",
    "deployment_ready",
    "physical_validation_status",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run M23-E revised offline compensator sweep.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--surface", default="S2_marble_floor")
    parser.add_argument("--velocities", nargs="*", type=float, default=DEFAULT_VELOCITIES)
    parser.add_argument("--physical-context-csv", type=Path, default=DEFAULT_M23C_PAIR_CSV)
    args = parser.parse_args(argv)

    summary = run_sweep(args.output_dir, args.surface, args.velocities, args.physical_context_csv)
    print("M23-E revised offline compensator sweep complete")
    print(f"  Identity fallback count: {summary['identity_fallback_count']}")
    print(f"  Harmful M23-C commands selected: {summary['harmful_m23c_commands_selected']}")
    print(f"  Deployment ready: {summary['deployment_ready']}")
    return 0


def run_sweep(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    surface: str = "S2_marble_floor",
    velocities: list[float] | None = None,
    physical_context_csv: Path = DEFAULT_M23C_PAIR_CSV,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    velocities = velocities or DEFAULT_VELOCITIES
    decisions = []
    for velocity in velocities:
        request = RevisedCompensationRequest(
            platform=SUPPORTED_EMPIRICAL_PLATFORM,
            surface_type=surface,
            desired_actual_velocity_mps=velocity,
            physical_context_csv_path=physical_context_csv,
        )
        decisions.append(revised_compensate_velocity(request))

    rows = [decision.to_dict() for decision in decisions]
    csv_rows = [{field: row.get(field, "") for field in SWEEP_FIELDS} for row in rows]
    csv_path = output_dir / "m23e_revised_compensator_sweep.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SWEEP_FIELDS)
        writer.writeheader()
        writer.writerows(csv_rows)

    sweep_json = output_dir / "m23e_revised_compensator_sweep.json"
    sweep_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    identity_count = sum(1 for row in rows if row["feasibility_status"] == "identity_preferred")
    harmful_selected = sum(
        1
        for row in rows
        if row["final_command_velocity_mps"] == row["candidate_compensated_command_velocity_mps"]
        and row["feasibility_status"] == "ok"
    )
    mismatch_count = sum(1 for row in rows if row["profile_mismatch_suspected"])
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "surface": surface,
        "desired_velocities_mps": velocities,
        "decision_count": len(rows),
        "identity_fallback_count": identity_count,
        "benefit_gate_rejection_count": sum(1 for row in rows if row["feasibility_status"] == "compensation_not_beneficial"),
        "overcorrection_rejection_count": sum(1 for row in rows if row["feasibility_status"] == "overcorrection_risk"),
        "profile_mismatch_suspected_count": mismatch_count,
        "harmful_m23c_commands_selected": harmful_selected,
        "all_final_commands_identity": all(row["final_command_velocity_mps"] == row["identity_command_velocity_mps"] for row in rows),
        "physical_validation_status": "not_started",
        "deployment_ready": False,
        "hardware_execution": False,
        "claim_boundary": "offline revised compensator sweep only; no physical validation or tracking-improvement claim",
    }
    (output_dir / "m23e_revised_compensator_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m23e_revised_compensator_report.md").write_text(build_report(summary, rows), encoding="utf-8")
    return summary


def build_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# M23-E Revised Offline Compensator Sweep",
        "",
        "Status: offline sweep only. No hardware execution and no physical validation claim.",
        "",
        f"- Surface: `{summary['surface']}`",
        f"- Decisions: {summary['decision_count']}",
        f"- Identity fallback count: {summary['identity_fallback_count']}",
        f"- Profile mismatch suspected count: {summary['profile_mismatch_suspected_count']}",
        f"- Harmful M23-C compensated commands selected: {summary['harmful_m23c_commands_selected']}",
        f"- Deployment ready: {summary['deployment_ready']}",
        "",
        "## Decisions",
        "",
        "| Desired | Candidate | Final | Status | Direct error | Comp error | Benefit |",
        "|---:|---:|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {_fmt(row['desired_actual_velocity_mps'])} | "
            f"{_fmt(row['candidate_compensated_command_velocity_mps'])} | "
            f"{_fmt(row['final_command_velocity_mps'])} | "
            f"{row['feasibility_status']} | "
            f"{_fmt(row['expected_direct_error_mps'])} | "
            f"{_fmt(row['expected_compensated_error_mps'])} | "
            f"{_fmt(row['expected_benefit_mps'])} |"
        )
    lines += [
        "",
        "The revised logic avoids the M23-C failure mode by selecting identity where the physical direct baseline is already accurate.",
    ]
    return "\n".join(lines) + "\n"


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
