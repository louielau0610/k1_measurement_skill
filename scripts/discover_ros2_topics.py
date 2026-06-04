"""Read-only ROS2 topic discovery helper.

This script never publishes, subscribes, or sends robot commands.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import shutil
import subprocess

import yaml


CATEGORIES = [
    "odom",
    "imu",
    "low_state",
    "robot_state",
    "battery",
    "command",
    "velocity",
    "loco",
    "unknown",
]


def classify_topic(topic_name: str) -> str:
    """Classify one topic name by keyword. This is not manual verification."""

    name = topic_name.lower()
    if "odom" in name or "odometry" in name:
        return "odom"
    if "imu" in name:
        return "imu"
    if "low_state" in name or "lowstate" in name:
        return "low_state"
    if "battery" in name or "power" in name:
        return "battery"
    if "robot_state" in name or "robotstate" in name or "state" in name:
        return "robot_state"
    if "velocity_cmd" in name or "vel_cmd" in name or "cmd" in name or "command" in name:
        return "command"
    if "velocity" in name or "twist" in name or "cmd_vel" in name:
        return "velocity"
    if "loco" in name or "locomotion" in name or "walk" in name or "gait" in name:
        return "loco"
    return "unknown"


def classify_topics(topic_names: list[str]) -> dict[str, list[str]]:
    """Group topic names by candidate category."""

    grouped: dict[str, list[str]] = {category: [] for category in CATEGORIES}
    for topic_name in topic_names:
        grouped[classify_topic(topic_name)].append(topic_name)
    return grouped


def discover_topics() -> list[str]:
    """Run read-only `ros2 topic list` and return topic names."""

    result = subprocess.run(
        ["ros2", "topic", "list"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def print_summary(grouped_topics: dict[str, list[str]]) -> None:
    """Print a readable candidate topic summary."""

    print("Candidate topic summary. Keyword matches are not verification.")
    for category in CATEGORIES:
        topics = grouped_topics.get(category, [])
        print(f"{category}:")
        if topics:
            for topic_name in topics:
                print(f"  - {topic_name}")
        else:
            print("  - <none>")


def save_grouped_topics(grouped_topics: dict[str, list[str]], output_path: str | Path) -> None:
    """Save grouped candidates to YAML."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "ros2_topic_list_keyword_classification",
        "verification_status": "unverified_candidates_only",
        "warning": "Do not treat keyword-classified topic names as final.",
        "topics": grouped_topics,
    }
    output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only ROS2 topic discovery.")
    parser.add_argument("--save", help="Optional YAML output path for candidate topics.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if shutil.which("ros2") is None:
        print("ROS2 command not detected.")
        print("This is non-fatal for development environments without ROS2 installed.")
        print("No topic discovery was run, and no robot command was sent.")
        return 0

    try:
        topic_names = discover_topics()
    except subprocess.CalledProcessError as exc:
        print(f"Failed to run read-only ROS2 topic list: {exc}")
        return 1

    grouped = classify_topics(topic_names)
    print_summary(grouped)
    if args.save:
        save_grouped_topics(grouped, args.save)
        print(f"Saved unverified candidate topic summary to: {args.save}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
