"""Send a single M23-B velocity command via Booster SDK.

Robot-side script. Uses Booster SDK only — does NOT import rclpy.
Preserves split-process architecture: this runs in its own subprocess.

Usage (robot-side):
  python scripts/send_m23b_k1_velocity_command.py \\
    --trial-id M23A_S2_marble_floor_V040_dire_R1 \\
    --command-velocity 0.40 \\
    --interface lo

NOTE: This script requires the Booster SDK environment to be available.
On systems without Booster SDK, it exits with a clear error message.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Try importing Booster SDK. If unavailable, provide a clear error.
# This keeps the script importable for testing and compile checks.
# ---------------------------------------------------------------------------
try:
    from B1LocoClient import B1LocoClient  # type: ignore[import-untyped]
    from ChannelFactory import ChannelFactory  # type: ignore[import-untyped]
    from RobotMode import RobotMode  # type: ignore[import-untyped]
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False
    B1LocoClient = None  # type: ignore
    ChannelFactory = None  # type: ignore
    RobotMode = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]

IDLE_SEC = 2.0
COMMAND_SEC = 6.0
STOP_SEC = 2.0
SEND_HZ = 10


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send a single M23-B velocity command via Booster SDK.")
    parser.add_argument("--trial-id", required=True, help="Trial identifier")
    parser.add_argument("--command-velocity", type=float, required=True, help="Command velocity in m/s")
    parser.add_argument("--interface", default="lo", help="Network interface (default: lo)")
    parser.add_argument("--idle-sec", type=float, default=IDLE_SEC, help="Idle phase duration")
    parser.add_argument("--command-sec", type=float, default=COMMAND_SEC, help="Command phase duration")
    parser.add_argument("--stop-sec", type=float, default=STOP_SEC, help="Stop phase duration")
    parser.add_argument("--prepare-sec", type=float, default=3.0, help="Prepare mode duration")
    parser.add_argument("--walking-sec", type=float, default=2.0, help="Walking mode duration")
    parser.add_argument("--log-dir", default=None, help="Optional directory for command log")
    args = parser.parse_args(argv)

    print(f"M23-B SDK Command: trial={args.trial_id}, v_cmd={args.command_velocity:.3f} m/s, interface={args.interface}")

    if not _SDK_AVAILABLE:
        print("ERROR: Booster SDK not available. Cannot send velocity command.", file=sys.stderr)
        print("This script must run on the Booster K1 robot with the SDK environment.", file=sys.stderr)
        print("The SDK import failed — no motor movement will occur.", file=sys.stderr)
        return 1

    client = None
    command_log: dict = {
        "trial_id": args.trial_id,
        "command_velocity_mps": args.command_velocity,
        "interface": args.interface,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "phases": {},
        "exit_code": -1,
        "error": "",
    }

    try:
        # --- Initialize SDK connection ---
        print(f"  [SDK] Initializing ChannelFactory on interface '{args.interface}'...")
        ChannelFactory.Instance().Init(0, args.interface)
        client = B1LocoClient()
        client.Init()
        print(f"  [SDK] Connected.")

        # --- Enter Prepare mode ---
        print(f"  [SDK] Entering kPrepare for {args.prepare_sec:.1f}s...")
        client.RobotMode(RobotMode.kPrepare)
        time.sleep(args.prepare_sec)
        command_log["phases"]["prepare"] = {"duration_sec": args.prepare_sec, "ok": True}

        # --- Enter Walking mode ---
        print(f"  [SDK] Entering kWalking for {args.walking_sec:.1f}s...")
        client.RobotMode(RobotMode.kWalking)
        time.sleep(args.walking_sec)
        command_log["phases"]["walking_setup"] = {"duration_sec": args.walking_sec, "ok": True}

        # --- Idle phase: zero velocity ---
        print(f"  [SDK] Idle phase: Move(0,0,0) for {args.idle_sec:.1f}s")
        _send_phase(client, 0.0, args.idle_sec, "idle", command_log)

        # --- Command phase: requested velocity ---
        print(f"  [SDK] Command phase: Move({args.command_velocity:.3f},0,0) for {args.command_sec:.1f}s")
        _send_phase(client, args.command_velocity, args.command_sec, "command", command_log)

        # --- Stop phase: zero velocity ---
        print(f"  [SDK] Stop phase: Move(0,0,0) for {args.stop_sec:.1f}s")
        _send_phase(client, 0.0, args.stop_sec, "stop", command_log)

        command_log["exit_code"] = 0
        print(f"  [SDK] Trial {args.trial_id} complete.")

    except Exception as exc:
        command_log["error"] = str(exc)
        command_log["exit_code"] = 1
        print(f"  [SDK] ERROR: {exc}", file=sys.stderr)
        return 1

    finally:
        # Always attempt stop
        if client is not None:
            try:
                for _ in range(int(args.stop_sec * SEND_HZ)):
                    client.Move(0.0, 0.0, 0.0)
                    time.sleep(1.0 / SEND_HZ)
            except Exception:
                pass
        command_log["finished_at"] = datetime.now(timezone.utc).isoformat()

    # Write command log if requested
    if args.log_dir:
        log_dir = Path(args.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{args.trial_id}_cmd_log.json"
        log_path.write_text(json.dumps(command_log, indent=2), encoding="utf-8")
        print(f"  [SDK] Command log: {log_path}")

    return 0


def _send_phase(client, velocity: float, duration_sec: float, phase: str, log: dict) -> None:
    """Send repeated Move commands at SEND_HZ for the given duration."""
    n_commands = max(1, int(duration_sec * SEND_HZ))
    for i in range(n_commands):
        client.Move(velocity, 0.0, 0.0)
        time.sleep(1.0 / SEND_HZ)
    log["phases"][phase] = {"velocity_mps": velocity, "duration_sec": duration_sec, "commands_sent": n_commands, "ok": True}


if __name__ == "__main__":
    raise SystemExit(main())
