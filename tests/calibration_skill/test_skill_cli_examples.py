import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = [sys.executable, "-m", "calibration_skill.cli"]
EXAMPLE_DIR = ROOT / "examples/calibration_skill"
VALID = [
    "preflight_request.mock.json",
    "dry_run_velocity_command.mock.json",
    "dry_run_collect_telemetry.mock.json",
    "dry_run_stop.mock.json",
    "dry_run_end_to_end.mock.json",
]
INVALID = [
    "invalid_real_platform_request.json",
    "invalid_dry_run_false_request.json",
    "invalid_missing_safety_request.json",
]


def run_cli(*args):
    return subprocess.run([*CLI, *args], cwd=ROOT, capture_output=True, text=True, timeout=30)


def test_all_valid_examples_validate_and_invoke():
    for name in VALID:
        rel = f"examples/calibration_skill/{name}"
        assert run_cli("validate", "--input", rel).returncode == 0
        assert run_cli("invoke", "--input", rel).returncode == 0


def test_invalid_examples_reject_deterministically():
    for name in INVALID:
        rel = f"examples/calibration_skill/{name}"
        first = run_cli("validate", "--input", rel)
        second = run_cli("validate", "--input", rel)
        assert first.returncode == 1
        assert first.stdout == second.stdout
        assert json.loads(first.stdout)["status"] == "rejected"


def test_examples_contain_no_machine_local_paths():
    for path in EXAMPLE_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert "C:\\" not in text
        assert "Users/" not in text
        assert "\\Users\\" not in text


def test_example_outputs_are_deterministic():
    rel = "examples/calibration_skill/dry_run_end_to_end.mock.json"
    first = run_cli("invoke", "--input", rel, "--compact")
    second = run_cli("invoke", "--input", rel, "--compact")
    assert first.returncode == 0
    assert first.stdout == second.stdout
