"""Run M23-B K1 physical compensation trials.

Robot-side runner for the M23-A trial plan. Requires --execute for hardware
movement. Preserves split-process architecture: ROS2 logger in separate
terminal from SDK command process.

Default: dry-run only. No hardware movement.

Usage (dry-run):
  python scripts/run_m23b_k1_compensation_trials.py --surface S2_marble_floor

Usage (execute):
  python scripts/run_m23b_k1_compensation_trials.py \\
    --surface S2_marble_floor --session-id m23b_s2_run1 --execute
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TRIAL_PLAN_CSV = Path("outputs/compensation_experiments/m23a_trial_plan.csv")
DEFAULT_SESSION_BASE = Path("data/compensation_experiments/m23b_k1")

TRIAL_RECORD_FIELDS = [
    "trial_id", "pair_id", "session_id", "surface",
    "desired_velocity_mps", "condition", "command_velocity_mps",
    "risk_policy", "state_log_path", "valid", "invalid_reason",
    "timestamp", "physical_run_status", "notes",
]

IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run M23-B K1 physical compensation trials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--surface", default="S2_marble_floor", help="Surface identifier")
    parser.add_argument("--session-id", default=None, help="Session ID (auto-generated if not provided)")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute hardware movement (default: dry-run)")
    parser.add_argument("--no-permit", action="store_true", default=False, help="Disable per-trial permit (default: enabled)")
    parser.add_argument("--interface", default="ros2_odometer", help="State interface")
    parser.add_argument("--start-from-trial-id", default=None, help="Resume from a specific trial ID")
    parser.add_argument("--skip-existing", action="store_true", default=False, help="Skip trials with existing state logs")
    parser.add_argument("--trial-plan", type=Path, default=TRIAL_PLAN_CSV, help="Path to trial plan CSV")
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_SESSION_BASE, help="Base output directory")
    args = parser.parse_args(argv)

    # Load trial plan
    if not args.trial_plan.exists():
        print(f"Error: trial plan not found: {args.trial_plan}", file=sys.stderr)
        return 1

    with args.trial_plan.open(newline="", encoding="utf-8-sig") as f:
        all_trials = list(csv.DictReader(f))

    # Filter by surface
    trials = [t for t in all_trials if t["surface"] == args.surface]
    if not trials:
        print(f"No trials found for surface: {args.surface}", file=sys.stderr)
        return 1

    # Resume support
    if args.start_from_trial_id:
        start_idx = next((i for i, t in enumerate(trials) if t["trial_id"] == args.start_from_trial_id), 0)
        trials = trials[start_idx:]

    # Session setup
    session_id = args.session_id or f"m23b_{args.surface}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    session_dir = args.base_dir / session_id
    state_log_dir = session_dir / "state_logs"

    if not args.execute:
        return _dry_run(trials, session_id, args)

    # --- EXECUTE MODE ---
    session_dir.mkdir(parents=True, exist_ok=True)
    state_log_dir.mkdir(parents=True, exist_ok=True)
    trial_records_path = session_dir / "trial_records.csv"

    # Write session metadata
    metadata = {
        "session_id": session_id,
        "experiment_id": "m23b_k1_compensation",
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "surface": args.surface,
        "trial_plan_source": str(args.trial_plan),
        "interface": args.interface,
        "split_process_required": True,
        "permit_enabled": not args.no_permit,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "physical_validation_status": "execution_in_progress",
        "deployment_ready": False,
        "timing": {"idle_sec": IDLE_SEC, "command_sec": COMMAND_SEC, "stop_sec": STOP_SEC},
    }
    (session_dir / "session_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    permit = not args.no_permit
    executed = 0
    skipped = 0
    invalid = 0
    print(f"\n{'='*60}")
    print(f"  M23-B K1 Compensation Trials — EXECUTE")
    print(f"  Session:  {session_id}")
    print(f"  Surface:  {args.surface}")
    print(f"  Trials:   {len(trials)}")
    print(f"  Permit:   {'enabled' if permit else 'DISABLED'}")
    print(f"  Output:   {session_dir}")
    print(f"  SPLIT-PROCESS: ROS2 logger in separate terminal")
    print(f"{'='*60}\n")

    for i, trial in enumerate(trials, 1):
        tid = trial["trial_id"]
        pid = trial["pair_id"]
        cond = trial["condition"]
        v_desired = float(trial["desired_velocity_mps"])
        cmd_str = trial["command_velocity_mps"]
        v_cmd = float(cmd_str) if cmd_str else None

        state_log_path = state_log_dir / f"{tid}.csv"

        print(f"\n--- Trial {i}/{len(trials)}: {tid} ---")
        print(f"    Pair: {pid} | Condition: {cond} | v_desired: {v_desired:.2f} m/s")
        if v_cmd is not None:
            print(f"    u_cmd: {v_cmd:.3f} m/s")

        # Skip if compensator declared infeasible
        comp_status = trial.get("compensator_status", "")
        if cond == "compensated" and comp_status not in ("ok", "feasible_but_risky"):
            print(f"    → SKIPPED: compensator returned {comp_status}")
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "false", f"infeasible_compensation:{comp_status}", "skipped")
            skipped += 1
            continue

        # Skip if state log exists
        if args.skip_existing and state_log_path.exists():
            print(f"    → SKIPPED: state log already exists")
            continue

        # Per-trial permit
        if permit:
            resp = input("    Execute this trial? [y/N]: ").strip().lower()
            if resp != "y":
                _append_record(trial_records_path, tid, pid, session_id, args.surface,
                              v_desired, cond, v_cmd, str(state_log_path),
                              "false", "operator_skipped", "skipped")
                skipped += 1
                print("    → SKIPPED by operator.")
                continue

        # SPLIT-PROCESS: prompt operator to start ROS2 logger
        print(f"    [SPLIT-PROCESS] Start ROS2 logger in SEPARATE terminal:")
        print(f"      source /opt/booster/BoosterRos2Interface/install/setup.bash")
        print(f"      python scripts/log_m23b_k1_compensation_trial.py \\")
        print(f"        --trial-id {tid} --pair-id {pid} --condition {cond} \\")
        print(f"        --desired-velocity {v_desired} --command-velocity {v_cmd or 0} \\")
        print(f"        --output-dir {state_log_dir}")

        if permit:
            input("    Press Enter after starting the ROS2 logger...")

        # SPLIT-PROCESS: prompt operator to send SDK command
        print(f"    [SPLIT-PROCESS] Send velocity command via Booster SDK (separate terminal):")
        if v_cmd is not None and v_cmd > 0:
            print(f"      kPrepare → kWalking → Move({v_cmd:.3f}, 0, 0)")
            print(f"      Duration: {IDLE_SEC}s idle + {COMMAND_SEC}s command + {STOP_SEC}s stop")
        else:
            print(f"      WARNING: command velocity is {v_cmd}. Operator must handle manually.")

        if permit:
            input("    Press Enter after trial duration completes...")

        # Record successful execution
        _append_record(trial_records_path, tid, pid, session_id, args.surface,
                      v_desired, cond, v_cmd, str(state_log_path),
                      "true", "", "executed")
        executed += 1
        print(f"    → EXECUTED.")

    summary = {
        "total": len(trials), "executed": executed,
        "skipped": skipped, "invalid": invalid,
    }
    print(f"\n{'='*60}")
    print(f"  Session complete. Executed: {executed}, Skipped: {skipped}")
    print(f"  Records: {trial_records_path}")
    print(f"  Run extraction: python scripts/extract_m23b_k1_compensation_trials.py --session-dir {session_dir}")
    print(f"{'='*60}\n")
    return 0


def _dry_run(trials: list[dict], session_id: str, args: argparse.Namespace) -> int:
    print(f"\n{'='*60}")
    print(f"  M23-B K1 Compensation Trials — DRY RUN")
    print(f"  Session:  {session_id}")
    print(f"  Surface:  {args.surface}")
    print(f"  Trials:   {len(trials)}")
    print(f"  Motor movement: DISABLED (dry-run)")
    print(f"  Split-process:  REQUIRED")
    print(f"{'='*60}\n")
    for i, t in enumerate(trials, 1):
        print(f"  [{i:03d}/{len(trials):03d}] {t['trial_id']:45s} "
              f"pair={t['pair_id']} cond={t['condition']:12s} "
              f"v_desired={t['desired_velocity_mps']} m/s")
    print(f"\n{'='*60}")
    print(f"  Dry-run complete. No hardware was moved.")
    print(f"  To execute, re-run with --execute.")
    print(f"{'='*60}\n")
    return 0


def _append_record(
    path: Path, trial_id: str, pair_id: str, session_id: str,
    surface: str, v_desired: float, condition: str,
    v_cmd: float | None, state_log_path: str,
    valid: str, reason: str, run_status: str,
) -> None:
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TRIAL_RECORD_FIELDS)
        if write_header:
            w.writeheader()
        w.writerow({
            "trial_id": trial_id, "pair_id": pair_id, "session_id": session_id,
            "surface": surface, "desired_velocity_mps": v_desired,
            "condition": condition, "command_velocity_mps": v_cmd if v_cmd is not None else "",
            "risk_policy": "na", "state_log_path": state_log_path,
            "valid": valid, "invalid_reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "physical_run_status": run_status, "notes": "",
        })


if __name__ == "__main__":
    raise SystemExit(main())
