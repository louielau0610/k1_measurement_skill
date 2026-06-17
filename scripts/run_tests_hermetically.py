#!/usr/bin/env python
"""Run tests while proving the Git worktree stays unchanged."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_COMMAND = ["py", "-3.12", "-m", "pytest", "tests/", "--tb=no", "-q"]

EXIT_OK = 0
EXIT_CHILD_FAILED = 1
EXIT_INITIAL_DIRTY = 2
EXIT_MUTATED = 3
EXIT_USAGE = 4


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def git_status(cwd: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git status failed")
    return result.stdout


def run_child(command: list[str], cwd: Path) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    return CommandResult(result.returncode, result.stdout, result.stderr)


def build_summary(
    *,
    command: list[str],
    initial_status: str,
    final_status: str,
    child: CommandResult | None,
    exit_code: int,
) -> dict[str, Any]:
    return {
        "runner": "run_tests_hermetically",
        "command": command,
        "initial_status": initial_status,
        "final_status": final_status,
        "child_returncode": None if child is None else child.returncode,
        "child_stdout": "" if child is None else child.stdout,
        "child_stderr": "" if child is None else child.stderr,
        "repository_mutated": final_status != initial_status,
        "exit_code": exit_code,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print only machine-readable JSON summary")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after --; defaults to pytest")
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    cwd = Path.cwd()
    command = args.command or DEFAULT_COMMAND

    try:
        initial = git_status(cwd)
    except Exception as exc:
        summary = build_summary(
            command=command,
            initial_status="",
            final_status="",
            child=None,
            exit_code=EXIT_USAGE,
        )
        summary["error"] = str(exc)
        print(json.dumps(summary, sort_keys=True))
        return EXIT_USAGE

    if initial:
        summary = build_summary(
            command=command,
            initial_status=initial,
            final_status=initial,
            child=None,
            exit_code=EXIT_INITIAL_DIRTY,
        )
        print(json.dumps(summary, sort_keys=True) if args.json else _human_summary(summary))
        return EXIT_INITIAL_DIRTY

    child = run_child(command, cwd)
    final = git_status(cwd)
    if final != initial:
        exit_code = EXIT_MUTATED
    elif child.returncode != 0:
        exit_code = EXIT_CHILD_FAILED
    else:
        exit_code = EXIT_OK

    summary = build_summary(
        command=command,
        initial_status=initial,
        final_status=final,
        child=child,
        exit_code=exit_code,
    )
    print(json.dumps(summary, sort_keys=True) if args.json else _human_summary(summary))
    return exit_code


def _human_summary(summary: dict[str, Any]) -> str:
    lines = [
        json.dumps(
            {
                "runner": summary["runner"],
                "command": summary["command"],
                "child_returncode": summary["child_returncode"],
                "repository_mutated": summary["repository_mutated"],
                "exit_code": summary["exit_code"],
            },
            sort_keys=True,
        )
    ]
    if summary["child_stdout"]:
        lines.append(summary["child_stdout"].rstrip())
    if summary["child_stderr"]:
        lines.append(summary["child_stderr"].rstrip())
    if summary["final_status"]:
        lines.append("final_status:")
        lines.append(summary["final_status"].rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
