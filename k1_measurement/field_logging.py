"""Read-only real K1 field logging launcher."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from k1_measurement.topic_mapping import confirmed_topics, load_topic_mapping, validate_topic_mapping


PopenFactory = Callable[..., Any]


def build_rosbag_record_command(session_dir: str | Path, topics: list[str]) -> list[str]:
    output = Path(session_dir) / "raw_ros" / "rosbag"
    return ["ros2", "bag", "record", "-o", str(output), *topics]


def start_field_logger(
    session_dir: str | Path,
    duration_sec: float | None = None,
    popen_factory: PopenFactory = subprocess.Popen,
) -> dict[str, Any]:
    """Start read-only `ros2 bag record` and write a run summary."""

    session = Path(session_dir)
    raw_dir = session / "raw_ros"
    raw_dir.mkdir(parents=True, exist_ok=True)
    mapping = load_topic_mapping(session / "topic_mapping.yaml")
    validation = validate_topic_mapping(mapping)
    if not validation["valid"]:
        summary = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": "topic mapping validation failed",
            "validation": validation,
            "command": None,
        }
        (session / "logger_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        raise ValueError("topic mapping validation failed")

    topics = confirmed_topics(mapping)
    command = build_rosbag_record_command(session, topics)
    started_at = datetime.now(timezone.utc).isoformat()
    process = popen_factory(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timed_out = False
    stdout = ""
    stderr = ""

    try:
        if duration_sec is None:
            stdout, stderr = process.communicate()
        else:
            try:
                stdout, stderr = process.communicate(timeout=duration_sec)
            except TypeError:
                time.sleep(duration_sec)
                process.terminate()
                stdout, stderr = process.communicate()
                timed_out = True
            except subprocess.TimeoutExpired:
                process.terminate()
                stdout, stderr = process.communicate()
                timed_out = True
    finally:
        return_code = process.returncode

    summary = {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "success": return_code == 0 or timed_out,
        "duration_sec": duration_sec,
        "timed_out_and_terminated": timed_out,
        "command": command,
        "topics": topics,
        "return_code": return_code,
        "stdout_preview": (stdout or "")[:1000],
        "stderr_preview": (stderr or "")[:1000],
        "note": "Read-only ros2 bag record. No movement command was published.",
    }
    (session / "logger_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
