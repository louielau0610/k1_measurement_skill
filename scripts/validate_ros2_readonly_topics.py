"""CLI for M7 read-only ROS2 topic validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.ros2_readonly_validator import build_validation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ROS2 read-only topic visibility for K1 M7.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON and Markdown reports.")
    parser.add_argument("--include-interface-show", action="store_true", help="Inspect discovered message types.")
    parser.add_argument("--timeout-sec", type=float, default=5.0, help="Timeout per ROS2 CLI command.")
    parser.add_argument("--print-only", action="store_true", help="Print planned checks without executing ROS2.")
    parser.add_argument("--topic", action="append", default=[], help="Explicit topic for optional sample-once planning.")
    parser.add_argument("--sample-once", action="store_true", help="Only plan sampling for topics passed by --topic.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_once and not args.topic:
        print("--sample-once requested without --topic; no sampling will be performed.")
    if args.print_only:
        print("Print-only mode. Planned checks:")
        print("- ros2 --help")
        print("- ros2 topic list")
        print("- ros2 topic list -t")
        if args.include_interface_show:
            print("- ros2 interface show <message_type>")
        if args.sample_once:
            print("- sample once for explicit --topic values only")

    report = build_validation_report(
        output_dir=args.output_dir,
        include_interface_show=args.include_interface_show,
        timeout_sec=args.timeout_sec,
        print_only=args.print_only,
        sample_topics=args.topic,
        sample_once=args.sample_once,
    )
    print(f"Wrote ROS2 discovery reports to: {args.output_dir}")
    print(f"ROS2 available: {report['ros2_availability']['ros2_available']}")
    print("Real K1 topic mapping is still TBD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
