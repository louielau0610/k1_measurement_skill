"""Run offline compensator verification and generate audit outputs.

Generates verification outputs under:
  outputs/compensation_research/m22d_offline_verification/

All outputs are offline-only — not physical validation — not deployment-ready.

Usage:
  python scripts/verify_offline_compensator.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import SUPPORTED_EMPIRICAL_PLATFORM
from calibration_core.compensation_verification import (
    OFFLINE_ONLY_DISCLAIMER,
    run_baseline_comparison,
    run_edge_case_audit,
    run_leave_one_repeat_out,
    run_risk_policy_audit,
    summarize_leave_one_repeat_out,
)

OUTPUT_DIR = Path("outputs/compensation_research/m22d_offline_verification")
DEFAULT_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")
DEFAULT_CONTRACT = Path("outputs/measurement_v1/booster_k1_measurements_contract_v1.csv")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run offline compensator verification.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--platform", default=SUPPORTED_EMPIRICAL_PLATFORM)
    args = parser.parse_args(argv)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    all_disclaimers_applied = True

    print("=" * 60)
    print("  Offline Compensator Verification — M22-D")
    print(f"  Platform: {args.platform}")
    print(f"  Profile:  {args.profile}")
    print(f"  Contract: {args.contract}")
    print(f"  Output:   {output_dir}")
    print(f"  {OFFLINE_ONLY_DISCLAIMER}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Edge-case audit
    # ------------------------------------------------------------------
    print("\n[1/4] Edge-case audit...")
    edge_result = run_edge_case_audit(args.profile, args.contract, args.platform)
    print(f"  Cases: {edge_result.total} total, {edge_result.passed} passed, {edge_result.failed} failed")

    edge_json = output_dir / "edge_case_audit.json"
    edge_json.write_text(json.dumps(edge_result.to_dict(), indent=2), encoding="utf-8")

    edge_md = output_dir / "edge_case_audit.md"
    edge_md.write_text(_build_edge_case_md(edge_result, timestamp), encoding="utf-8")
    print(f"  -> {edge_json.name}, {edge_md.name}")

    # ------------------------------------------------------------------
    # 2. Leave-one-repeat-out validation
    # ------------------------------------------------------------------
    print("\n[2/4] Leave-one-repeat-out validation...")
    loro_results = run_leave_one_repeat_out(args.contract, args.profile, args.platform)
    loro_summary = summarize_leave_one_repeat_out(loro_results)
    print(f"  Checks: {loro_summary['total_checks']}")
    print(f"  Feasible: {loro_summary['feasible_checks']}, Infeasible: {loro_summary['infeasible_checks']}")
    if loro_summary["mean_abs_command_error_mps"] is not None:
        print(f"  Mean abs cmd error: {loro_summary['mean_abs_command_error_mps']:.4f} m/s")

    loro_csv = output_dir / "leave_one_repeat_out_results.csv"
    _write_loro_csv(loro_csv, loro_results)
    print(f"  -> {loro_csv.name}")

    # ------------------------------------------------------------------
    # 3. Baseline comparison
    # ------------------------------------------------------------------
    print("\n[3/4] Baseline comparison...")
    baseline_results = run_baseline_comparison(args.profile, args.contract, args.platform)
    print(f"  Comparisons: {len(baseline_results)}")

    baseline_csv = output_dir / "baseline_comparison.csv"
    _write_baseline_csv(baseline_csv, baseline_results)
    baseline_summary = {
        "total_comparisons": len(baseline_results),
        "method": "ours_conservative_monotonic",
        "baselines": ["direct_command", "scalar_gain", "nearest_lookup", "ordinary_interpolation"],
        "generated_at": timestamp,
        "disclaimer": OFFLINE_ONLY_DISCLAIMER,
    }
    baseline_json = output_dir / "baseline_comparison_summary.json"
    baseline_json.write_text(json.dumps(baseline_summary, indent=2), encoding="utf-8")
    print(f"  -> {baseline_csv.name}, {baseline_json.name}")

    # ------------------------------------------------------------------
    # 4. Risk policy audit
    # ------------------------------------------------------------------
    print("\n[4/4] Risk policy audit...")
    policy_audit = run_risk_policy_audit(args.profile, args.contract, args.platform)
    stats = policy_audit["policy_stats"]
    for pol in ["conservative", "balanced", "permissive"]:
        s = stats[pol]
        print(f"  {pol}: feasible={s['feasible']}, risky={s['risky']}, rejected={s['rejected']}")
    order = policy_audit["ordering_checks"]
    print(f"  Ordering: conservative_most_restrictive={order['conservative_most_restrictive']}")

    policy_csv = output_dir / "risk_policy_audit.csv"
    _write_policy_csv(policy_csv, policy_audit["decisions"])
    policy_json = output_dir / "risk_policy_audit_summary.json"
    policy_json.write_text(json.dumps(policy_audit, indent=2), encoding="utf-8")
    print(f"  -> {policy_csv.name}, {policy_json.name}")

    # ------------------------------------------------------------------
    # Verification summary
    # ------------------------------------------------------------------
    summary = {
        "generated_at": timestamp,
        "platform": args.platform,
        "offline_only": True,
        "physical_validation": "not_started",
        "deployment_ready": False,
        "leave_one_repeat_out": loro_summary,
        "edge_case_audit": {"total": edge_result.total, "passed": edge_result.passed, "failed": edge_result.failed},
        "baseline_comparison": baseline_summary,
        "risk_policy_audit": {
            "policy_stats": policy_audit["policy_stats"],
            "ordering_checks": policy_audit["ordering_checks"],
        },
        "disclaimers_applied": all_disclaimers_applied,
        "disclaimer": OFFLINE_ONLY_DISCLAIMER,
    }

    summary_json = output_dir / "offline_compensator_verification_summary.json"
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    summary_md = output_dir / "offline_compensator_verification_report.md"
    summary_md.write_text(_build_report_md(summary, loro_summary, edge_result, policy_audit, timestamp), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"  Verification complete.")
    print(f"  Summary: {summary_json}")
    print(f"  Report:  {summary_md}")
    print(f"  {OFFLINE_ONLY_DISCLAIMER}")
    print(f"{'=' * 60}")

    return 0


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _write_loro_csv(path: Path, results: list) -> None:
    fields = ["trial_id", "platform", "surface_type", "command_velocity_mps",
              "measured_actual_velocity_mps", "predicted_command_mps",
              "absolute_command_error_mps", "expected_actual_mps",
              "actual_error_mps", "feasibility_status", "reason"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r.to_dict())


def _write_baseline_csv(path: Path, comparisons: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["platform", "surface_type", "desired_velocity_mps", "method",
                     "recommended_cmd_mps", "expected_actual_mps", "status", "reason"])
        for comp in comparisons:
            for b in [comp.compensator_decision] + comp.baselines:
                w.writerow([comp.platform, comp.surface_type, comp.desired_velocity_mps,
                           b.method, b.recommended_command_velocity_mps,
                           b.expected_actual_velocity_mps, b.status, b.reason])


def _write_policy_csv(path: Path, decisions: list[dict]) -> None:
    if not decisions:
        return
    fields = list(decisions[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for d in decisions:
            w.writerow(d)


def _build_edge_case_md(edge_result, timestamp: str) -> str:
    lines = [
        "# M22-D Edge-Case Audit",
        "",
        f"Generated: {timestamp}",
        f"Total cases: {edge_result.total}, Passed: {edge_result.passed}, Failed: {edge_result.failed}",
        "",
        f"**Disclaimer**: {OFFLINE_ONLY_DISCLAIMER}",
        "",
        "| # | Surface | Desired | Policy | Expected | Actual | Pass |",
        "|---|---------|---------|--------|----------|--------|------|",
    ]
    for i, c in enumerate(edge_result.cases, 1):
        icon = "✅" if c.passed else "❌"
        lines.append(f"| {i} | {c.surface_type} | {c.desired_velocity_mps} | {c.policy} | {c.expected_status} | {c.actual_status} | {icon} |")
    return "\n".join(lines) + "\n"


def _build_report_md(summary: dict, loro: dict, edge, policy: dict, timestamp: str) -> str:
    lines = [
        "# M22-D Offline Compensator Verification Report",
        "",
        f"Generated: {timestamp}",
        f"Platform: {summary['platform']}",
        "",
        f"**Disclaimer**: {OFFLINE_ONLY_DISCLAIMER}",
        "",
        "## Leave-One-Repeat-Out",
        f"- Total checks: {loro.get('total_checks', 0)}",
        f"- Feasible: {loro.get('feasible_checks', 0)}",
        f"- Mean abs cmd error: {loro.get('mean_abs_command_error_mps', 'N/A')}",
        "",
        "## Edge-Case Audit",
        f"- Total: {edge.total}, Passed: {edge.passed}, Failed: {edge.failed}",
        "",
        "## Risk Policy Audit",
    ]
    if "policy_stats" in policy:
        for pol_name, stats in policy["policy_stats"].items():
            lines.append(f"- {pol_name}: feasible={stats['feasible']}, risky={stats['risky']}, rejected={stats['rejected']}")

    lines += [
        "",
        "## Baseline Comparison",
        f"- Total comparisons: {summary['baseline_comparison'].get('total_comparisons', 0)}",
        f"- Methods: {', '.join(summary['baseline_comparison'].get('baselines', []))}",
        "",
        "## Status",
        f"- Physical validation: **{summary['physical_validation']}**",
        f"- Deployment ready: **{summary['deployment_ready']}**",
        f"- Offline only: **{summary['offline_only']}**",
        "",
        "## Next",
        "M23-A: K1 physical compensation experiment design.",
    ]
    return "\n".join(lines) + "\n"
