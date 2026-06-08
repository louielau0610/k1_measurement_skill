"""Structured read-only ROS2 topic validation for K1 measurement prep.

This module never publishes, subscribes by default, or sends movement commands.
All discovered topics remain unconfirmed candidates until manually reviewed on
the real K1 ROS2 shell.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence


Runner = Callable[..., subprocess.CompletedProcess[str]]

REPORT_JSON_NAME = "ros2_topic_discovery_report.json"
REPORT_MD_NAME = "ros2_topic_discovery_report.md"

CLASSIFICATION_KEYS = [
    "odom_candidates",
    "imu_candidates",
    "battery_candidates",
    "robot_state_candidates",
    "command_candidates",
    "unknown_topics",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _preview(text: str | None, limit: int = 1000) -> str:
    return (text or "")[:limit]


def _run_command(
    command: Sequence[str],
    timeout_sec: float,
    runner: Runner = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    return runner(
        list(command),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )


def check_ros2_availability(
    timeout_sec: float = 5.0,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run `ros2 --help` and return a JSON-compatible status object."""

    command = ["ros2", "--help"]
    result: dict[str, Any] = {
        "ros2_available": False,
        "ros2_cli_command": "ros2 --help",
        "return_code": None,
        "stdout_preview": "",
        "stderr_preview": "",
        "error_message": "",
        "checked_at": _utc_now(),
        "timeout_sec": timeout_sec,
    }
    try:
        completed = _run_command(command, timeout_sec, runner)
    except FileNotFoundError as exc:
        result["error_message"] = str(exc)
        return result
    except subprocess.TimeoutExpired as exc:
        result["error_message"] = f"timeout after {timeout_sec} seconds"
        result["stdout_preview"] = _preview(exc.stdout if isinstance(exc.stdout, str) else "")
        result["stderr_preview"] = _preview(exc.stderr if isinstance(exc.stderr, str) else "")
        return result

    result.update(
        {
            "ros2_available": completed.returncode == 0,
            "return_code": completed.returncode,
            "stdout_preview": _preview(completed.stdout),
            "stderr_preview": _preview(completed.stderr),
        }
    )
    if completed.returncode != 0:
        result["error_message"] = "ros2 --help returned a non-zero status"
    return result


def parse_topic_list(output: str) -> list[dict[str, str | None]]:
    """Parse `ros2 topic list` output without message types."""

    topics: list[dict[str, str | None]] = []
    for line in output.splitlines():
        topic = line.strip()
        if topic:
            topics.append({"name": topic, "message_type": None, "raw": line})
    return topics


def parse_topic_list_with_types(output: str) -> list[dict[str, str | None]]:
    """Parse `ros2 topic list -t` output.

    Typical lines look like `/odom [nav_msgs/msg/Odometry]`. If a line does not
    match that shape, the raw topic name is still preserved.
    """

    topics: list[dict[str, str | None]] = []
    for line in output.splitlines():
        raw = line.rstrip()
        stripped = raw.strip()
        if not stripped:
            continue
        message_type: str | None = None
        name = stripped
        if stripped.endswith("]") and " [" in stripped:
            name, type_part = stripped.rsplit(" [", 1)
            message_type = type_part[:-1].strip() or None
        topics.append({"name": name.strip(), "message_type": message_type, "raw": raw})
    return topics


def _result_payload(command: Sequence[str], completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "command": " ".join(command),
        "return_code": completed.returncode,
        "stdout": completed.stdout or "",
        "stderr": completed.stderr or "",
    }


def discover_topics(
    timeout_sec: float = 5.0,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run read-only topic discovery commands and parse topic metadata."""

    commands = {
        "topic_list": ["ros2", "topic", "list"],
        "topic_list_with_types": ["ros2", "topic", "list", "-t"],
    }
    payload: dict[str, Any] = {"commands": {}, "topics": [], "errors": []}

    try:
        list_result = _run_command(commands["topic_list"], timeout_sec, runner)
        payload["commands"]["topic_list"] = _result_payload(commands["topic_list"], list_result)
        if list_result.returncode == 0:
            payload["topics"] = parse_topic_list(list_result.stdout)
        else:
            payload["errors"].append("ros2 topic list returned a non-zero status")
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        payload["commands"]["topic_list"] = {
            "command": " ".join(commands["topic_list"]),
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "error_message": str(exc),
        }
        payload["errors"].append(str(exc))

    try:
        typed_result = _run_command(commands["topic_list_with_types"], timeout_sec, runner)
        payload["commands"]["topic_list_with_types"] = _result_payload(
            commands["topic_list_with_types"],
            typed_result,
        )
        if typed_result.returncode == 0:
            typed_topics = parse_topic_list_with_types(typed_result.stdout)
            if typed_topics:
                payload["topics"] = typed_topics
        else:
            payload["errors"].append("ros2 topic list -t returned a non-zero status")
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        payload["commands"]["topic_list_with_types"] = {
            "command": " ".join(commands["topic_list_with_types"]),
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "error_message": str(exc),
        }
        payload["errors"].append(str(exc))

    return payload


def classify_topic(topic: dict[str, str | None]) -> str:
    """Return a conservative candidate class for one topic."""

    haystack = " ".join(
        str(value).lower()
        for value in [topic.get("name"), topic.get("message_type")]
        if value
    )
    name = str(topic.get("name") or "").lower()

    if "odom" in haystack or "odometry" in haystack:
        return "odom_candidates"
    if "imu" in haystack or "inertial" in haystack:
        return "imu_candidates"
    if "battery" in haystack or "power" in haystack:
        return "battery_candidates"
    if "robot_state" in name or "robotstate" in name or "low_state" in name or "lowstate" in name:
        return "robot_state_candidates"
    if "cmd_vel" in name or "velocity_cmd" in name or "vel_cmd" in name:
        return "command_candidates"
    if "command" in name or name.endswith("/cmd") or "/cmd/" in name:
        return "command_candidates"
    return "unknown_topics"


def classify_topics(topics: list[dict[str, str | None]]) -> dict[str, list[dict[str, str | None]]]:
    """Group topics into unconfirmed candidate lists."""

    grouped: dict[str, list[dict[str, str | None]]] = {key: [] for key in CLASSIFICATION_KEYS}
    for topic in topics:
        grouped[classify_topic(topic)].append(topic)
    return grouped


def inspect_message_interfaces(
    topics: list[dict[str, str | None]],
    timeout_sec: float = 5.0,
    runner: Runner = subprocess.run,
) -> dict[str, dict[str, Any]]:
    """Run `ros2 interface show` for deduplicated message types."""

    message_types = sorted(
        {
            str(topic["message_type"])
            for topic in topics
            if topic.get("message_type")
        }
    )
    results: dict[str, dict[str, Any]] = {}
    for message_type in message_types:
        command = ["ros2", "interface", "show", message_type]
        try:
            completed = _run_command(command, timeout_sec, runner)
            results[message_type] = _result_payload(command, completed)
        except subprocess.TimeoutExpired:
            results[message_type] = {
                "command": " ".join(command),
                "return_code": None,
                "stdout": "",
                "stderr": "",
                "error_message": f"timeout after {timeout_sec} seconds",
            }
        except FileNotFoundError as exc:
            results[message_type] = {
                "command": " ".join(command),
                "return_code": None,
                "stdout": "",
                "stderr": "",
                "error_message": str(exc),
            }
    return results


def planned_print_only_report(timeout_sec: float) -> dict[str, Any]:
    """Create a dry-run report without executing ROS2 commands."""

    return {
        "generated_at": _utc_now(),
        "mode": "print_only",
        "ros2_availability": {
            "ros2_available": False,
            "ros2_cli_command": "ros2 --help",
            "return_code": None,
            "stdout_preview": "",
            "stderr_preview": "",
            "error_message": "print-only mode: ROS2 commands were not executed",
            "checked_at": _utc_now(),
            "timeout_sec": timeout_sec,
        },
        "topic_discovery": {"commands": {}, "topics": [], "errors": []},
        "candidate_classification": {key: [] for key in CLASSIFICATION_KEYS},
        "interface_inspection": {},
        "sample_once": {"enabled": False, "topics": [], "note": "not executed in print-only mode"},
        "manual_confirmation_required": True,
        "topic_mapping_status": "TBD",
        "warnings": [
            "Real K1 topic mapping is still TBD.",
            "Dummy reports are not real K1 findings.",
            "This tool does not publish motion commands.",
        ],
    }


def build_validation_report(
    output_dir: str | Path,
    include_interface_show: bool = False,
    timeout_sec: float = 5.0,
    print_only: bool = False,
    sample_topics: list[str] | None = None,
    sample_once: bool = False,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Build and write the JSON/Markdown ROS2 validation report."""

    if print_only:
        report = planned_print_only_report(timeout_sec)
        report["sample_once"] = {
            "enabled": bool(sample_once),
            "topics": sample_topics or [],
            "note": "planned only; no ROS2 commands were executed",
        }
    else:
        availability = check_ros2_availability(timeout_sec=timeout_sec, runner=runner)
        discovery = {"commands": {}, "topics": [], "errors": []}
        interface_results: dict[str, dict[str, Any]] = {}
        if availability["ros2_available"]:
            discovery = discover_topics(timeout_sec=timeout_sec, runner=runner)
            if include_interface_show:
                interface_results = inspect_message_interfaces(
                    discovery["topics"],
                    timeout_sec=timeout_sec,
                    runner=runner,
                )
        classification = classify_topics(discovery["topics"])
        report = {
            "generated_at": _utc_now(),
            "mode": "live_ros2_cli",
            "ros2_availability": availability,
            "topic_discovery": discovery,
            "candidate_classification": classification,
            "interface_inspection": interface_results,
            "sample_once": {
                "enabled": bool(sample_once),
                "topics": sample_topics or [],
                "note": (
                    "Sampling is only allowed for explicit --topic selections; "
                    "automatic all-topic sampling is not performed."
                ),
            },
            "manual_confirmation_required": True,
            "topic_mapping_status": "TBD",
            "warnings": [
                "Real K1 topic mapping is still TBD.",
                "Dummy reports are not real K1 findings.",
                "This tool does not publish motion commands.",
            ],
        }

    write_reports(report, output_dir)
    return report


def write_reports(report: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    """Write JSON and Markdown discovery reports."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / REPORT_JSON_NAME
    md_path = output / REPORT_MD_NAME
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")
    return json_path, md_path


def render_markdown_report(report: dict[str, Any]) -> str:
    """Render a Chinese-first Markdown summary for field review."""

    availability = report.get("ros2_availability", {})
    topics = report.get("topic_discovery", {}).get("topics", [])
    classification = report.get("candidate_classification", {})
    interface_results = report.get("interface_inspection", {})

    lines = [
        "# M7 Real K1 ROS2 Topic Discovery Report",
        "",
        "## 结论声明",
        "",
        "- Real K1 topic mapping is still TBD.",
        "- Dummy reports are not real K1 findings.",
        "- 本工具只执行 ROS2 CLI 只读检查，不发布运动命令。",
        "",
        "## ROS2 可用性",
        "",
        f"- ros2_available: {availability.get('ros2_available')}",
        f"- command: {availability.get('ros2_cli_command')}",
        f"- return_code: {availability.get('return_code')}",
        f"- checked_at: {availability.get('checked_at')}",
        f"- timeout_sec: {availability.get('timeout_sec')}",
        f"- error_message: {availability.get('error_message', '')}",
        "",
        "## Discovered Topics",
        "",
    ]
    if topics:
        lines.extend(
            f"- {topic.get('name')} [{topic.get('message_type') or 'type not shown'}]"
            for topic in topics
        )
    else:
        lines.append("- <none>")

    lines.extend(["", "## Candidate Classification", ""])
    for key in CLASSIFICATION_KEYS:
        lines.append(f"### {key}")
        entries = classification.get(key, [])
        if entries:
            lines.extend(
                f"- {topic.get('name')} [{topic.get('message_type') or 'type not shown'}]"
                for topic in entries
            )
        else:
            lines.append("- <none>")
        lines.append("")

    lines.extend(["## Interface Inspection", ""])
    if interface_results:
        for message_type, result in interface_results.items():
            lines.extend(
                [
                    f"### {message_type}",
                    f"- return_code: {result.get('return_code')}",
                    f"- error_message: {result.get('error_message', '')}",
                    "",
                ]
            )
    else:
        lines.append("- Not requested or no message types were available.")

    lines.extend(
        [
            "",
            "## Next Manual Confirmation Steps",
            "",
            "1. 在真实 K1 ROS2 shell 中复查候选 odom / IMU / battery / robot_state / command topics。",
            "2. 对候选 message type 运行 `ros2 interface show`，确认字段含义和时间戳。",
            "3. 只在人工确认后填写 `configs/real_k1_logger_template.yaml`。",
            "4. 先运行静态 logging test，再运行一次 smoke forward trial。",
            "5. 确认 raw log 完整后再执行完整 forward velocity baseline。",
            "",
        ]
    )
    return "\n".join(lines)
