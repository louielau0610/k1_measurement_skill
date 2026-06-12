"""Run M24-B Booster K1 S2 direct-refresh profile trials.

Default mode is dry-run. Hardware movement requires --execute. The runner
orchestrates split subprocesses and imports neither rclpy nor Booster SDK.
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
TRIAL_PLAN_CSV = Path("outputs/compensation_experiments/m24a_s2_profile_refresh_plan.csv")
DEFAULT_SESSION_BASE = Path("data/compensation_experiments/m24b_s2_profile_refresh")
EXPECTED_SURFACE = "S2_marble_floor"
EXPECTED_CONDITION = "direct_refresh"
LOGGER_SCRIPT = "scripts/log_m24b_s2_profile_refresh_trial.py"
SDK_SCRIPT = "scripts/send_m23b_k1_velocity_command.py"

IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0

TRIAL_RECORD_FIELDS = [
    "trial_id",
    "refresh_group_id",
    "session_id",
    "surface",
    "desired_velocity_mps",
    "condition",
    "command_velocity_mps",
    "state_log_path",
    "valid",
    "invalid_reason",
    "timestamp",
    "physical_run_status",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run M24-B S2 direct-refresh profile trials.")
    parser.add_argument("--trial-plan", type=Path, default=TRIAL_PLAN_CSV)
    parser.add_argument("--surface", default=EXPECTED_SURFACE)
    parser.add_argument("--interface", default="ros2_odometer")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--sdk-python", default=None)
    parser.add_argument("--sdk-env-setup", default=None)
    parser.add_argument("--logger-startup-sec", type=float, default=0.5)
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_SESSION_BASE)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-permit", action="store_true")
    parser.add_argument("--command-timeout-sec", type=float, default=20.0)
    parser.add_argument("--logger-timeout-sec", type=float, default=20.0)
    args = parser.parse_args(argv)

    try:
        trials = load_and_validate_plan(args.trial_plan, args.surface)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    session_id = args.session_id or f"m24b_s2_profile_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir = args.base_dir / session_id
    state_log_dir = session_dir / "state_logs"

    if not args.execute:
        return dry_run(trials, session_id, args)

    session_dir.mkdir(parents=True, exist_ok=True)
    state_log_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "session_id": session_id,
        "milestone": "M24-B",
        "platform": "booster_k1",
        "robot_model": "Booster K1",
        "surface": args.surface,
        "condition": EXPECTED_CONDITION,
        "trial_plan_source": str(args.trial_plan),
        "expected_trial_count": len(trials),
        "interface": args.interface,
        "split_process_required": True,
        "runner_imports_rclpy": False,
        "runner_imports_booster_sdk": False,
        "permit_enabled": not args.no_permit,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "physical_profile_refresh_status": "execution_in_progress",
        "profile_update_status": "not_updated",
        "deployment_ready": False,
        "go1_g1_blocked": True,
        "timing": {"idle_sec": IDLE_SEC, "command_sec": COMMAND_SEC, "stop_sec": STOP_SEC},
        "logger_startup_sec": args.logger_startup_sec,
        "sdk_python": args.sdk_python or sys.executable,
        "sdk_env_setup_provided": bool(args.sdk_env_setup),
        "claim_boundary": "direct refresh execution only; no profile update or compensation improvement claim",
    }
    (session_dir / "session_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    trial_records_path = session_dir / "trial_records.csv"
    logger_py = str(ROOT / LOGGER_SCRIPT)
    sdk_py = str(ROOT / SDK_SCRIPT)
    executed = skipped = invalid = 0

    print(f"M24-B S2 direct-refresh EXECUTE session: {session_id}")
    print(f"Trials: {len(trials)} | Surface: {args.surface} | Permit: {not args.no_permit}")

    for index, trial in enumerate(trials, 1):
        trial_id = trial["trial_id"]
        group_id = trial["refresh_group_id"]
        desired = float(trial["desired_velocity_mps"])
        command = float(trial["command_velocity_mps"])
        state_log_path = state_log_dir / f"{trial_id}.csv"
        print(f"[{index:02d}/{len(trials):02d}] {trial_id} u_cmd={command:.2f}")

        if not args.no_permit:
            response = input("Execute this direct-refresh trial? [y/N]: ").strip().lower()
            if response != "y":
                append_record(trial_records_path, trial, session_id, state_log_path, "false", "operator_skipped", "skipped")
                skipped += 1
                continue

        logger_cmd = build_logger_command(logger_py, trial_id, group_id, desired, command, state_log_dir, sys.executable)
        sdk_cmd = build_sdk_command(
            sdk_py,
            trial_id,
            command,
            args.interface,
            state_log_dir,
            sdk_python=args.sdk_python or sys.executable,
            sdk_env_setup=args.sdk_env_setup,
        )

        print(f"  [LOGGER] {_display(logger_cmd)}")
        logger_proc = subprocess.Popen(logger_cmd)
        time.sleep(args.logger_startup_sec)
        print(f"  [SDK] {_display(sdk_cmd)}")
        sdk_proc = subprocess.Popen(sdk_cmd)

        try:
            sdk_rc = sdk_proc.wait(timeout=args.command_timeout_sec)
        except subprocess.TimeoutExpired:
            sdk_proc.kill()
            sdk_rc = -1

        if sdk_rc != 0 and logger_proc.poll() is None:
            logger_proc.terminate()

        try:
            logger_rc = logger_proc.wait(timeout=args.logger_timeout_sec)
        except subprocess.TimeoutExpired:
            logger_proc.kill()
            logger_rc = -1

        if sdk_rc == 0 and logger_rc == 0:
            append_record(trial_records_path, trial, session_id, state_log_path, "true", "", "executed", f"logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            executed += 1
        elif sdk_rc != 0:
            append_record(trial_records_path, trial, session_id, state_log_path, "false", f"sdk_subprocess_failed_rc={sdk_rc}", "sdk_failed", f"logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            invalid += 1
        else:
            append_record(trial_records_path, trial, session_id, state_log_path, "false", f"logger_subprocess_failed_rc={logger_rc}", "logger_failed", f"logger_rc={logger_rc}; sdk_rc={sdk_rc}")
            invalid += 1

    summary = {"executed": executed, "skipped": skipped, "invalid": invalid, "total": len(trials)}
    (session_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"M24-B session complete: {summary}")
    return 0


def load_and_validate_plan(path: Path, surface: str) -> list[dict[str, str]]:
    if not path.exists():
        raise ValueError(f"trial plan not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("trial plan is empty")
    bad_condition = [r.get("trial_id", "?") for r in rows if r.get("condition") != EXPECTED_CONDITION]
    if bad_condition:
        raise ValueError(f"non-direct_refresh conditions present: {bad_condition[:5]}")
    bad_surface = [r.get("trial_id", "?") for r in rows if r.get("surface") != EXPECTED_SURFACE]
    if bad_surface:
        raise ValueError(f"non-S2 surfaces present: {bad_surface[:5]}")
    if surface != EXPECTED_SURFACE:
        raise ValueError(f"M24-B supports only {EXPECTED_SURFACE}, got {surface}")
    return rows


def dry_run(trials: list[dict[str, str]], session_id: str, args: argparse.Namespace) -> int:
    print("M24-B S2 profile refresh DRY RUN")
    print(f"Session: {session_id}")
    print(f"Surface: {args.surface}")
    print(f"Trials: {len(trials)}")
    print("Motor movement: DISABLED")
    for index, trial in enumerate(trials, 1):
        print(
            f"[{index:02d}/{len(trials):02d}] {trial['trial_id']} "
            f"group={trial['refresh_group_id']} condition={trial['condition']} "
            f"u_cmd={trial['command_velocity_mps']}"
        )
    print("Dry-run complete. No hardware was moved. Re-run with --execute to move hardware.")
    return 0


def append_record(
    path: Path,
    trial: dict[str, str],
    session_id: str,
    state_log_path: Path,
    valid: str,
    reason: str,
    run_status: str,
    notes: str = "",
) -> None:
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRIAL_RECORD_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "trial_id": trial["trial_id"],
            "refresh_group_id": trial["refresh_group_id"],
            "session_id": session_id,
            "surface": trial["surface"],
            "desired_velocity_mps": trial["desired_velocity_mps"],
            "condition": trial["condition"],
            "command_velocity_mps": trial["command_velocity_mps"],
            "state_log_path": str(state_log_path),
            "valid": valid,
            "invalid_reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "physical_run_status": run_status,
            "notes": notes,
        })


def build_logger_command(
    logger_py: str,
    trial_id: str,
    refresh_group_id: str,
    desired_velocity: float,
    command_velocity: float,
    state_log_dir: Path,
    python_executable: str,
) -> list[str]:
    return [
        python_executable,
        logger_py,
        "--trial-id",
        trial_id,
        "--refresh-group-id",
        refresh_group_id,
        "--condition",
        EXPECTED_CONDITION,
        "--desired-velocity",
        str(desired_velocity),
        "--command-velocity",
        str(command_velocity),
        "--output-dir",
        str(state_log_dir),
        "--idle-sec",
        str(IDLE_SEC),
        "--command-sec",
        str(COMMAND_SEC),
        "--stop-sec",
        str(STOP_SEC),
        "--realtime",
    ]


def build_sdk_command(
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
        sdk_python,
        sdk_py,
        "--trial-id",
        trial_id,
        "--command-velocity",
        str(command_velocity),
        "--interface",
        interface,
        "--idle-sec",
        str(IDLE_SEC),
        "--command-sec",
        str(COMMAND_SEC),
        "--stop-sec",
        str(STOP_SEC),
        "--log-dir",
        str(state_log_dir),
    ]
    if not sdk_env_setup:
        return direct_cmd
    return ["bash", "-lc", f"{sdk_env_setup} && " + " ".join(shlex.quote(part) for part in direct_cmd)]


def _display(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


if __name__ == "__main__":
    raise SystemExit(main())
