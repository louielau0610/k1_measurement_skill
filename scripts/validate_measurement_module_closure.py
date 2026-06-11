"""Validate Measurement Module v1 closure.

Checks that all closure artifacts exist, are internally consistent,
and that phase gates are correctly maintained.

Usage:
  python scripts/validate_measurement_module_closure.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REQUIRED_ARTIFACTS = {
    "closure_summary": "outputs/measurement_v1/measurement_module_v1_closure_summary.json",
    "closure_report": "outputs/measurement_v1/measurement_module_v1_closure_report.md",
    "closure_documentation": "docs/measurement_module_v1_closure.md",
    "measurement_module_status": "outputs/measurement_v1/measurement_module_status.json",
    "k1_reference_manifest": "outputs/measurement_v1/booster_k1_reference_manifest.json",
    "k1_gold_profile": "outputs/real_k1_validation_m19/k1_gold_profile_v1.json",
    "k1_contract_csv": "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv",
    "k1_contract_validation": "outputs/measurement_v1/booster_k1_measurements_contract_validation.json",
    "contract_definition": "outputs/measurement_v1/measurement_contract_v1.json",
    "step2_plan": "docs/step2_velocity_compensation_research_plan.md",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Measurement Module v1 closure.")
    parser.add_argument("--json", action="store_true", default=False, help="Output as JSON")
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, dict[str, object]] = {}

    # ------------------------------------------------------------------
    # 1. Check all required artifacts exist
    # ------------------------------------------------------------------
    missing_artifacts = []
    for name, rel_path in REQUIRED_ARTIFACTS.items():
        path = ROOT / rel_path
        if path.exists():
            checks[name] = {"pass": True, "path": rel_path}
        else:
            checks[name] = {"pass": False, "path": rel_path}
            errors.append(f"missing_artifact:{rel_path}")
            missing_artifacts.append(name)

    # ------------------------------------------------------------------
    # 2. Check measurement module status
    # ------------------------------------------------------------------
    status_path = ROOT / "outputs/measurement_v1/measurement_module_status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        flag_checks = [
            ("measurement_module_v1_status", "complete"),
            ("measurement_module_v1_complete", True),
            ("booster_k1_reference_ready", True),
            ("measurement_contract_v1_ready", True),
            ("velocity_compensation_ready", False),
            ("unitree_go1_measurement_ready", False),
            ("unitree_g1_measurement_ready", False),
            ("cross_platform_empirical_validation_ready", False),
        ]
        for flag, expected in flag_checks:
            actual = status.get(flag)
            ok = actual == expected
            checks[f"status_flag:{flag}"] = {"pass": ok, "expected": expected, "actual": actual}
            if not ok:
                errors.append(f"status_flag:{flag}:expected={expected}_actual={actual}")

        # Check next_phase
        next_phase = status.get("next_phase", "")
        checks["status:next_phase"] = {
            "pass": "velocity_compensation" in str(next_phase).lower(),
            "actual": next_phase,
        }
        if "velocity_compensation" not in str(next_phase).lower():
            errors.append(f"next_phase:unexpected:{next_phase}")

    # ------------------------------------------------------------------
    # 3. Check closure summary
    # ------------------------------------------------------------------
    closure_path = ROOT / "outputs/measurement_v1/measurement_module_v1_closure_summary.json"
    if closure_path.exists():
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        checks["closure:version"] = {"pass": "closure_version" in closure, "value": closure.get("closure_version")}
        if closure.get("closure_status") != "complete":
            errors.append(f"closure_status:not_complete:{closure.get('closure_status')}")
            checks["closure:status"] = {"pass": False, "actual": closure.get("closure_status")}
        else:
            checks["closure:status"] = {"pass": True}

        # Check status flags in closure
        flags = closure.get("status_flags", {})
        for flag, expected in [("measurement_module_v1_complete", True),
                                ("velocity_compensation_ready", False),
                                ("unitree_go1_measurement_ready", False),
                                ("unitree_g1_measurement_ready", False)]:
            actual = flags.get(flag)
            ok = actual == expected
            checks[f"closure_flag:{flag}"] = {"pass": ok, "expected": expected, "actual": actual}
            if not ok:
                errors.append(f"closure_flag:{flag}:expected={expected}_actual={actual}")

        # Check milestone lineage
        lineage = closure.get("milestone_lineage", [])
        expected_milestones = {"M19C-E", "M20", "M21-A", "M21-B", "M21-C", "M21-D"}
        found = {m["milestone"] for m in lineage if isinstance(m, dict)}
        missing_ms = expected_milestones - found
        checks["closure:milestone_lineage"] = {"pass": len(missing_ms) == 0, "missing": list(missing_ms)}
        if missing_ms:
            errors.append(f"closure:missing_milestones:{missing_ms}")

        # Check next_step
        next_step = closure.get("next_step", "")
        checks["closure:next_step"] = {
            "pass": "velocity_compensation" in str(next_step).lower(),
            "actual": next_step,
        }

    # ------------------------------------------------------------------
    # 4. Check K1 contract CSV has 72 rows
    # ------------------------------------------------------------------
    contract_csv_path = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv"
    if contract_csv_path.exists():
        with contract_csv_path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        row_count = len(rows)
        checks["k1_contract:row_count"] = {"pass": row_count == 72, "actual": row_count}
        if row_count != 72:
            errors.append(f"k1_contract_csv:row_count:{row_count}_expected_72")

    # ------------------------------------------------------------------
    # 5. Check K1 contract validation
    # ------------------------------------------------------------------
    val_path = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_validation.json"
    if val_path.exists():
        val = json.loads(val_path.read_text(encoding="utf-8"))
        v = val.get("validation", {})
        is_valid = v.get("valid", False) if isinstance(v, dict) else False
        valid_rows = v.get("valid_rows", 0) if isinstance(v, dict) else 0
        checks["k1_contract_validation:pass"] = {"pass": is_valid, "valid_rows": valid_rows}
        if not is_valid:
            errors.append("k1_contract_validation:failed")
        if valid_rows != 72:
            errors.append(f"k1_contract_validation:valid_rows:{valid_rows}_expected_72")

    # ------------------------------------------------------------------
    # 6. Check no compensator module introduced
    # ------------------------------------------------------------------
    forbidden_modules = [
        "calibration_core/compensator.py",
        "calibration_core/inverse_response_model.py",
    ]
    for mod in forbidden_modules:
        path = ROOT / mod
        exists = path.exists()
        checks[f"forbidden:{mod}"] = {"pass": not exists}
        if exists:
            errors.append(f"forbidden_module_present:{mod}")

    # ------------------------------------------------------------------
    # 7. Summary
    # ------------------------------------------------------------------
    all_checks = sum(1 for c in checks.values() if c.get("pass", False))
    total_checks = len(checks)
    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_passed": all_checks,
        "checks_total": total_checks,
        "checks": {k: v for k, v in checks.items()},
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status_str = "PASSED" if result["valid"] else "FAILED"
        print(f"\nMeasurement Module v1 Closure Validation: {status_str}")
        print(f"  Checks: {all_checks}/{total_checks} passed")
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for e in errors:
                print(f"  - {e}")
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        if not errors and not warnings:
            print("  All closure checks passed.")
        print()

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
