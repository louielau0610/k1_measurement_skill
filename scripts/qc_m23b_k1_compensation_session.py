"""Run QC on a M23-B K1 compensation session.

Checks session integrity, pair completeness, and field presence.

Usage:
  python scripts/qc_m23b_k1_compensation_session.py \\
    --session-dir data/compensation_experiments/m23b_k1/<session_id>/
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QC a M23-B K1 compensation session.")
    parser.add_argument("--session-dir", required=True, help="Path to session directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    session_dir = Path(args.session_dir)
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    # Check session metadata
    meta_path = session_dir / "session_metadata.json"
    if meta_path.exists():
        checks.append({"check": "session_metadata", "pass": True})
    else:
        checks.append({"check": "session_metadata", "pass": False})
        errors.append("session_metadata.json:missing")

    # Check trial records
    records_path = session_dir / "trial_records.csv"
    if not records_path.exists():
        checks.append({"check": "trial_records", "pass": False})
        errors.append("trial_records.csv:missing")
    else:
        checks.append({"check": "trial_records", "pass": True})
        with records_path.open(newline="", encoding="utf-8-sig") as f:
            records = list(csv.DictReader(f))

        # Check required fields in records
        for field in ["trial_id", "pair_id", "condition", "desired_velocity_mps", "command_velocity_mps"]:
            missing = [r["trial_id"] for r in records if not r.get(field)]
            if missing:
                checks.append({"check": f"record_field:{field}", "pass": False})
                errors.append(f"record_field:{field}:missing_in:{missing[:3]}")
            else:
                checks.append({"check": f"record_field:{field}", "pass": True})

        # Check pairs have direct + compensated
        pairs: dict[str, list[str]] = {}
        for r in records:
            pid = r.get("pair_id", "")
            if pid:
                pairs.setdefault(pid, []).append(r.get("condition", ""))
        incomplete = [pid for pid, conds in pairs.items() if set(conds) != {"direct", "compensated"}]
        if incomplete:
            checks.append({"check": "pair_completeness", "pass": False})
            errors.append(f"incomplete_pairs:{incomplete[:5]}")
        else:
            checks.append({"check": "pair_completeness", "pass": True, "pair_count": len(pairs)})

        # Check invalid trials have reason
        invalid_no_reason = [r["trial_id"] for r in records if r.get("valid", "").lower() == "false" and not r.get("invalid_reason", "").strip()]
        if invalid_no_reason:
            checks.append({"check": "invalid_trial_reason", "pass": False})
            errors.append(f"invalid_without_reason:{invalid_no_reason[:5]}")
        else:
            checks.append({"check": "invalid_trial_reason", "pass": True})

    # Check state logs
    state_log_dir = session_dir / "state_logs"
    if state_log_dir.is_dir():
        csv_count = len(list(state_log_dir.glob("*.csv")))
        checks.append({"check": "state_logs", "pass": True, "csv_count": csv_count})
    else:
        checks.append({"check": "state_logs", "pass": False})
        warnings.append("state_logs/:missing")

    # Check extraction outputs
    extracted_path = session_dir / "extracted_results.csv"
    if extracted_path.exists():
        checks.append({"check": "extracted_results", "pass": True})
        with extracted_path.open(newline="", encoding="utf-8-sig") as f:
            ext_rows = list(csv.DictReader(f))

        # Check extraction fields
        for field in ["measured_actual_velocity_mps", "yaw_drift_deg", "absolute_tracking_error_mps"]:
            missing = [r.get("trial_id", "?") for r in ext_rows if not r.get(field)]
            if missing:
                checks.append({"check": f"extraction:{field}", "pass": False})
                errors.append(f"extraction:{field}:missing_in:{missing[:3]}")
            else:
                checks.append({"check": f"extraction:{field}", "pass": True})

        # Check no command copy
        suspect = []
        for r in ext_rows:
            try:
                cmd = float(r.get("command_velocity_mps", 0))
                meas = float(r.get("measured_actual_velocity_mps", 0))
                if cmd > 0 and abs(cmd - meas) < 1e-9:
                    suspect.append(r.get("trial_id", "?"))
            except (ValueError, TypeError):
                pass
        if suspect:
            checks.append({"check": "no_command_velocity_copy", "pass": False})
            errors.append(f"suspected_copy:{suspect[:5]}")
        else:
            checks.append({"check": "no_command_velocity_copy", "pass": True})

    else:
        checks.append({"check": "extracted_results", "pass": False})
        warnings.append("extracted_results.csv:missing")

    # Check no physical validation claim
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        pv = meta.get("physical_validation_status", "")
        if "complete" in str(pv).lower() or "validated" in str(pv).lower():
            errors.append(f"physical_validation_claimed_prematurely:{pv}")
            checks.append({"check": "no_physical_validation_claim", "pass": False})
        else:
            checks.append({"check": "no_physical_validation_claim", "pass": True})

    # Summary
    all_pass = len(errors) == 0
    summary = {
        "qc_time": datetime.now(timezone.utc).isoformat(),
        "session_dir": str(session_dir),
        "overall_pass": all_pass,
        "checks_passed": sum(1 for c in checks if c.get("pass")),
        "checks_total": len(checks),
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "disclaimer": "M23-B execution pack QC — not physical validation — no compensation improvement claim",
    }

    qc_path = session_dir / "qc_summary.json"
    qc_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status = "PASSED" if all_pass else "FAILED"
        print(f"\nM23-B Session QC: {status}")
        print(f"  Checks: {summary['checks_passed']}/{summary['checks_total']}")
        for e in errors:
            print(f"  - {e}")
        for w in warnings:
            print(f"  WARNING: {w}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
