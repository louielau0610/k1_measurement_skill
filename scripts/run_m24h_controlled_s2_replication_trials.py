"""Run M24-H controlled S2 replication trials.

Robot-side runner for the M24-G controlled S2 replication plan.
Enforces strict constraints: S2_marble_floor only, direct_refresh_controlled
only, no compensated commands, velocities 0.40/0.45/0.50/0.55 only.

Split-process architecture: launches logger and SDK command as subprocesses.
Default: dry-run only. Requires --execute for hardware movement.

Usage (dry-run):
  python scripts/run_m24h_controlled_s2_replication_trials.py

Usage (execute):
  python scripts/run_m24h_controlled_s2_replication_trials.py --execute \\
    --session-id m24h_controlled_s2_replication_20260612_150000
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TRIAL_PLAN_CSV = Path("outputs/compensation_experiments/m24g_controlled_s2_replication_plan.csv")
METADATA_TEMPLATE = Path("outputs/compensation_experiments/m24h_controlled_metadata_template.json")
SESSION_BASE = Path("data/compensation_experiments/m24h_controlled_s2_replication")

ALLOWED_SURFACE = "S2_marble_floor"
ALLOWED_CONDITION = "direct_refresh_controlled"
ALLOWED_VELOCITIES = {0.40, 0.45, 0.50, 0.55}

LOGGER_SCRIPT = "scripts/log_m23b_k1_compensation_trial.py"
SDK_SCRIPT = "scripts/send_m23b_k1_velocity_command.py"

TRIAL_RECORD_FIELDS = [
    "trial_id", "replication_group_id", "session_id", "surface",
    "condition", "command_velocity_mps", "desired_velocity_mps",
    "repeat_index", "state_log_path", "valid", "invalid_reason",
    "timestamp", "physical_run_status", "logger_rc", "sdk_rc", "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run M24-H controlled S2 replication trials.")
    parser.add_argument("--trial-plan", type=Path, default=TRIAL_PLAN_CSV)
    parser.add_argument("--surface", default=ALLOWED_SURFACE)
    parser.add_argument("--interface", default="lo", help="SDK network interface")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--sdk-python", default=sys.executable, help="Python for SDK subprocess")
    parser.add_argument("--logger-startup-sec", type=float, default=1.0)
    parser.add_argument("--execute", action="store_true", default=False)
    parser.add_argument("--no-permit", action="store_true", default=False)
    parser.add_argument("--metadata-file", default=None, help="Session metadata JSON to record")
    parser.add_argument("--base-dir", type=Path, default=SESSION_BASE)
    parser.add_argument("--start-from-trial-id", default=None)
    parser.add_argument("--skip-existing", action="store_true", default=False)
    args = parser.parse_args(argv)

    # --- Validate surface ---
    if args.surface != ALLOWED_SURFACE:
        print(f"ERROR: only {ALLOWED_SURFACE} is allowed. Got: {args.surface}", file=sys.stderr)
        return 1

    # --- Load trial plan ---
    if not args.trial_plan.exists():
        print(f"ERROR: trial plan not found: {args.trial_plan}", file=sys.stderr)
        return 1

    with args.trial_plan.open(newline="", encoding="utf-8-sig") as f:
        all_trials = list(csv.DictReader(f))

    # --- Validate trials ---
    trials = []
    rejected = 0
    for t in all_trials:
        cond = t.get("condition", "")
        vel_str = t.get("command_velocity_mps", "0")
        try:
            vel = float(vel_str)
        except (ValueError, TypeError):
            vel = 0.0

        if t.get("surface") != ALLOWED_SURFACE:
            print(f"SKIP {t['trial_id']}: surface={t.get('surface')} (only {ALLOWED_SURFACE} allowed)")
            rejected += 1
            continue
        if cond != ALLOWED_CONDITION:
            print(f"SKIP {t['trial_id']}: condition={cond} (only {ALLOWED_CONDITION} allowed)")
            rejected += 1
            continue
        if t.get("compensated_command", "false").lower() == "true":
            print(f"SKIP {t['trial_id']}: compensated command not allowed")
            rejected += 1
            continue
        if vel not in ALLOWED_VELOCITIES:
            print(f"SKIP {t['trial_id']}: velocity={vel} (only {sorted(ALLOWED_VELOCITIES)} allowed)")
            rejected += 1
            continue
        trials.append(t)

    if not trials:
        print("ERROR: no valid trials after filtering.", file=sys.stderr)
        return 1

    # --- Resume support ---
    if args.start_from_trial_id:
        start_idx = next((i for i, t in enumerate(trials) if t["trial_id"] == args.start_from_trial_id), 0)
        trials = trials[start_idx:]

    print(f"Trial plan: {len(all_trials)} rows, {len(trials)} accepted, {rejected} rejected")
    for t in trials:
        print(f"  {t['trial_id']} | group={t['replication_group_id']} | v={t['command_velocity_mps']} | rep={t['repeat_index']}")

    # --- Dry-run ---
    if not args.execute:
        print(f"\n{'='*60}")
        print(f"  M24-H Controlled S2 Replication — DRY RUN")
        print(f"  Surface: {ALLOWED_SURFACE}")
        print(f"  Trials:  {len(trials)}")
        print(f"  Condition: {ALLOWED_CONDITION}")
        print(f"  No compensated commands. No hardware movement.")
        print(f"{'='*60}\n")
        return 0

    # --- EXECUTE ---
    session_id = args.session_id or f"m24h_controlled_s2_replication_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    session_dir = args.base_dir / session_id
    state_log_dir = session_dir / "state_logs"
    session_dir.mkdir(parents=True, exist_ok=True)
    state_log_dir.mkdir(parents=True, exist_ok=True)

    # Write session metadata
    session_meta = {
        "session_id": session_id, "surface": ALLOWED_SURFACE,
        "condition": ALLOWED_CONDITION, "total_trials": len(trials),
        "planned_velocities": sorted(ALLOWED_VELOCITIES),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "physical_run_status": "in_progress", "deployment_ready": False,
        "go1_g1_blocked": True, "profile_adoption_status": "not_adopted",
        "gold_profile_overwritten": False,
    }
    (session_dir / "session_metadata.json").write_text(json.dumps(session_meta, indent=2))

    # Copy metadata template if provided
    if args.metadata_file and Path(args.metadata_file).exists():
        controlled_meta = json.loads(Path(args.metadata_file).read_text())
    elif METADATA_TEMPLATE.exists():
        controlled_meta = json.loads(METADATA_TEMPLATE.read_text())
    else:
        controlled_meta = {}
    controlled_meta["session_id"] = session_id
    (session_dir / "controlled_metadata.json").write_text(json.dumps(controlled_meta, indent=2))

    trial_records_path = session_dir / "trial_records.csv"
    permit = not args.no_permit
    executed = skipped = invalid = 0

    print(f"\n{'='*60}")
    print(f"  M24-H Controlled S2 Replication — EXECUTE")
    print(f"  Session:  {session_id}")
    print(f"  Surface:  {ALLOWED_SURFACE}")
    print(f"  Trials:   {len(trials)}")
    print(f"  Permit:   {'enabled' if permit else 'DISABLED'}")
    print(f"  Output:   {session_dir}")
    print(f"{'='*60}\n")

    logger_py = str(ROOT / LOGGER_SCRIPT)
    sdk_py = str(ROOT / SDK_SCRIPT)

    for i, trial in enumerate(trials, 1):
        tid = trial["trial_id"]
        gid = trial["replication_group_id"]
        v_cmd = float(trial["command_velocity_mps"])
        v_desired = float(trial["desired_velocity_mps"])
        rep = trial["repeat_index"]
        state_log_path = state_log_dir / f"{tid}.csv"

        print(f"\n--- Trial {i}/{len(trials)}: {tid} ---")
        print(f"    Group: {gid} | v_cmd={v_cmd:.2f} | rep={rep}")

        if args.skip_existing and state_log_path.exists():
            print(f"    -> SKIPPED: state log exists")
            skipped += 1
            continue

        if permit:
            resp = input("    Execute? [y/N]: ").strip().lower()
            if resp != "y":
                _append_record(trial_records_path, tid, gid, session_id, v_cmd, v_desired, rep,
                              str(state_log_path), "false", "operator_skipped", "skipped")
                skipped += 1
                continue

        # Launch logger subprocess
        logger_cmd = [sys.executable, logger_py, "--trial-id", tid, "--pair-id", gid,
                      "--condition", ALLOWED_CONDITION, "--desired-velocity", str(v_desired),
                      "--command-velocity", str(v_cmd), "--output-dir", str(state_log_dir)]
        print(f"    [LOGGER] {' '.join(logger_cmd)}")
        logger_proc = subprocess.Popen(logger_cmd)
        time.sleep(args.logger_startup_sec)

        # Launch SDK subprocess
        sdk_cmd = [args.sdk_python, sdk_py, "--trial-id", tid, "--command-velocity", str(v_cmd),
                   "--interface", args.interface]
        print(f"    [SDK]    {' '.join(sdk_cmd)}")
        sdk_proc = subprocess.Popen(sdk_cmd)

        sdk_rc = sdk_proc.wait(timeout=30)
        try:
            logger_rc = logger_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logger_proc.kill()
            logger_rc = -1

        print(f"    [SDK] rc={sdk_rc}  [LOGGER] rc={logger_rc}")

        if sdk_rc != 0:
            _append_record(trial_records_path, tid, gid, session_id, v_cmd, v_desired, rep,
                          str(state_log_path), "false", f"sdk_failed_rc={sdk_rc}", "sdk_failed",
                          logger_rc=logger_rc, sdk_rc=sdk_rc)
            invalid += 1
        elif logger_rc != 0:
            _append_record(trial_records_path, tid, gid, session_id, v_cmd, v_desired, rep,
                          str(state_log_path), "false", f"logger_failed_rc={logger_rc}", "logger_failed",
                          logger_rc=logger_rc, sdk_rc=sdk_rc)
            invalid += 1
        else:
            _append_record(trial_records_path, tid, gid, session_id, v_cmd, v_desired, rep,
                          str(state_log_path), "true", "", "executed",
                          logger_rc=logger_rc, sdk_rc=sdk_rc)
            executed += 1
            print(f"    -> EXECUTED")

    print(f"\n{'='*60}")
    print(f"  Done. Executed={executed} Skipped={skipped} Invalid={invalid}")
    print(f"  Records: {trial_records_path}")
    print(f"  Extract: python scripts/extract_m24h_controlled_s2_replication_trials.py --session-dir {session_dir}")
    print(f"  QC:      python scripts/qc_m24h_controlled_s2_replication_session.py --session-dir {session_dir}")
    print(f"{'='*60}\n")
    return 0


def _append_record(path: Path, tid: str, gid: str, sid: str,
                   v_cmd: float, v_desired: float, rep: str, log_path: str,
                   valid: str, reason: str, status: str,
                   logger_rc: int = 0, sdk_rc: int = 0) -> None:
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TRIAL_RECORD_FIELDS)
        if write_header:
            w.writeheader()
        w.writerow({
            "trial_id": tid, "replication_group_id": gid, "session_id": sid,
            "surface": ALLOWED_SURFACE, "condition": ALLOWED_CONDITION,
            "command_velocity_mps": v_cmd, "desired_velocity_mps": v_desired,
            "repeat_index": rep, "state_log_path": log_path,
            "valid": valid, "invalid_reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "physical_run_status": status,
            "logger_rc": logger_rc, "sdk_rc": sdk_rc, "notes": "",
        })


if __name__ == "__main__":
    raise SystemExit(main())
