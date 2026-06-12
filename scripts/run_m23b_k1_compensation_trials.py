"""Run M23-B K1 physical compensation trials.

Robot-side runner for the M23-A trial plan. Requires --execute for hardware
movement. Preserves split-process architecture by launching separate
subprocesses for:
  1. ROS2 state logger (log_m23b_k1_compensation_trial.py)
  2. Booster SDK command (send_m23b_k1_velocity_command.py)

The runner itself does NOT import rclpy or Booster SDK — it only orchestrates
subprocesses. This ensures rclpy and Booster SDK never share a runtime.

Default: dry-run only. No hardware movement.

Usage (dry-run):
  python scripts/run_m23b_k1_compensation_trials.py --surface S2_marble_floor

Usage (execute):
  python scripts/run_m23b_k1_compensation_trials.py \\
    --surface S2_marble_floor --session-id m23b_s2_run1 --execute

NOTE: Sessions run before the M23-B hotfix (auto SDK subprocess) that relied
on manual operator SDK commands should NOT be treated as valid physical
compensation data. The runner now requires the SDK subprocess to succeed
before marking a trial as executed.
"""
from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
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

# Subprocess script paths (relative to ROOT)
LOGGER_SCRIPT = "scripts/log_m23b_k1_compensation_trial.py"
SDK_SCRIPT = "scripts/send_m23b_k1_velocity_command.py"


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
    parser.add_argument("--logger-startup-sec", type=float, default=0.5, help="Delay after logger launch before SDK launch")
    parser.add_argument("--sdk-python", default=None, help="Python executable for SDK subprocess")
    parser.add_argument("--sdk-env-setup", default=None, help="Optional shell setup command before SDK subprocess")
    parser.add_argument("--command-timeout-sec", type=float, default=20.0, help="SDK command subprocess timeout")
    parser.add_argument("--logger-timeout-sec", type=float, default=20.0, help="Logger subprocess timeout")
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
        "hotfix2_sync_logger_sdk_subprocess": True,
        "logger_startup_sec": args.logger_startup_sec,
        "sdk_python": args.sdk_python or sys.executable,
        "sdk_env_setup_provided": bool(args.sdk_env_setup),
        "invalid_debug_sessions": [
            "m23b_k1_s2_20260612_095811",
            "failed_auto_subprocess_tests_before_hotfix2",
        ],
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
    print(f"  SPLIT-PROCESS: Auto-launching ROS2 logger + SDK command subprocesses")
    print(f"  HOTFIX2: logger first, SDK after {args.logger_startup_sec:.2f}s while logger is running")
    print(f"  SDK interface: {args.interface}")
    print(f"{'='*60}\n")

    logger_py = str(ROOT / LOGGER_SCRIPT)
    sdk_py = str(ROOT / SDK_SCRIPT)

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
            print(f"    -> SKIPPED: compensator returned {comp_status}")
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "false", f"infeasible_compensation:{comp_status}", "skipped")
            skipped += 1
            continue

        # Skip if state log exists
        if args.skip_existing and state_log_path.exists():
            print(f"    -> SKIPPED: state log already exists")
            skipped += 1
            continue

        # Per-trial permit
        if permit:
            resp = input("    Execute this trial? [y/N]: ").strip().lower()
            if resp != "y":
                _append_record(trial_records_path, tid, pid, session_id, args.surface,
                              v_desired, cond, v_cmd, str(state_log_path),
                              "false", "operator_skipped", "skipped")
                skipped += 1
                print("    -> SKIPPED by operator.")
                continue

        # --- Launch split-process subprocesses ---
        if v_cmd is None or v_cmd <= 0:
            print(f"    -> SKIPPED: invalid command velocity {v_cmd}")
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "false", f"invalid_command_velocity:{v_cmd}", "skipped")
            skipped += 1
            continue

        # 1. Launch ROS2 logger subprocess first and keep it alive in realtime.
        logger_cmd = _build_logger_command(
            logger_py, tid, pid, cond, v_desired, v_cmd, state_log_dir, sys.executable
        )
        print(f"    [LOGGER] Launching: {_command_for_display(logger_cmd)}")
        logger_proc = subprocess.Popen(logger_cmd)
        time.sleep(args.logger_startup_sec)

        # 2. Launch SDK command subprocess while logger is still running.
        sdk_cmd = _build_sdk_command(
            sdk_py,
            tid,
            v_cmd,
            args.interface,
            state_log_dir,
            sdk_python=args.sdk_python or sys.executable,
            sdk_env_setup=args.sdk_env_setup,
        )
        print(f"    [SDK]    Launching: {_command_for_display(sdk_cmd)}")
        sdk_proc = subprocess.Popen(sdk_cmd)

        # 3. Wait for SDK command to finish (it controls timing)
        print(f"    Waiting for SDK command subprocess...")
        try:
            sdk_rc = sdk_proc.wait(timeout=args.command_timeout_sec)
        except subprocess.TimeoutExpired:
            sdk_proc.kill()
            sdk_rc = -1
            print(f"    [SDK]    Timed out, killed.")
        print(f"    [SDK]    Exit code: {sdk_rc}")

        if sdk_rc != 0 and logger_proc.poll() is None:
            logger_proc.terminate()

        # 4. Wait for logger to finish (should complete shortly after SDK)
        try:
            logger_rc = logger_proc.wait(timeout=args.logger_timeout_sec)
        except subprocess.TimeoutExpired:
            logger_proc.kill()
            logger_rc = -1
            print(f"    [LOGGER] Timed out, killed.")
        print(f"    [LOGGER] Exit code: {logger_rc}")

        # 5. Record trial outcome based on subprocess results
        if sdk_rc != 0:
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "false", f"sdk_subprocess_failed_rc={sdk_rc}", "sdk_failed",
                          notes=f"hotfix2 logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            invalid += 1
            print(f"    -> INVALID: SDK subprocess failed (rc={sdk_rc})")
        elif logger_rc != 0:
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "false", f"logger_subprocess_failed_rc={logger_rc}", "logger_failed",
                          notes=f"hotfix2 logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            invalid += 1
            print(f"    -> INVALID: Logger subprocess failed (rc={logger_rc})")
        else:
            _append_record(trial_records_path, tid, pid, session_id, args.surface,
                          v_desired, cond, v_cmd, str(state_log_path),
                          "true", "", "executed",
                          notes=f"hotfix2 logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            executed += 1
            print(f"    -> EXECUTED (logger={logger_rc}, sdk={sdk_rc})")

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
    notes: str = "",
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
            "physical_run_status": run_status, "notes": notes,
        })


def _build_logger_command(
    logger_py: str,
    trial_id: str,
    pair_id: str,
    condition: str,
    desired_velocity: float,
    command_velocity: float,
    state_log_dir: Path,
    python_executable: str,
) -> list[str]:
    return [
        python_executable, logger_py,
        "--trial-id", trial_id,
        "--pair-id", pair_id,
        "--condition", condition,
        "--desired-velocity", str(desired_velocity),
        "--command-velocity", str(command_velocity),
        "--output-dir", str(state_log_dir),
        "--idle-sec", str(IDLE_SEC),
        "--command-sec", str(COMMAND_SEC),
        "--stop-sec", str(STOP_SEC),
        "--realtime",
    ]


def _build_sdk_command(
    sdk_py: str,
    trial_id: str,
    command_velocity: float,
    interface: str,
    state_log_dir: Path,
    *,
    sdk_python: str,
    sdk_env_setup: str | None,
) -> list[str]:
    direct_cmd = [
        sdk_python, sdk_py,
        "--trial-id", trial_id,
        "--command-velocity", str(command_velocity),
        "--interface", interface,
        "--idle-sec", str(IDLE_SEC),
        "--command-sec", str(COMMAND_SEC),
        "--stop-sec", str(STOP_SEC),
        "--log-dir", str(state_log_dir),
    ]
    if not sdk_env_setup:
        return direct_cmd
    shell_cmd = f"{sdk_env_setup} && " + " ".join(shlex.quote(part) for part in direct_cmd)
    return ["bash", "-lc", shell_cmd]


def _command_for_display(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


if __name__ == "__main__":
    raise SystemExit(main())
