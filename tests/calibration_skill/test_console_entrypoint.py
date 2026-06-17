"""M26-E console entry point smoke tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from calibration_skill.cli import main

ROOT = Path(__file__).resolve().parents[2]


def run_module_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "calibration_skill.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )


def test_module_cli_manifest_smoke():
    result = run_module_cli("manifest")
    assert result.returncode == 0
    assert json.loads(result.stdout)["skill_name"] == "calibration_skill"


def test_entrypoint_function_callable_for_manifest(capsys):
    assert main(["manifest"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["dry_run_only"] is True


def test_examples_validate_and_invoke_end_to_end():
    example = run_module_cli("examples", "--operation", "dry_run_end_to_end")
    assert example.returncode == 0
    payload = json.loads(example.stdout)
    validate = subprocess.run(
        [sys.executable, "-m", "calibration_skill.cli", "validate", "--input", "-"],
        cwd=ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=30,
    )
    invoke = subprocess.run(
        [sys.executable, "-m", "calibration_skill.cli", "invoke", "--input", "-"],
        cwd=ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert validate.returncode == 0, validate.stderr
    assert invoke.returncode == 0, invoke.stderr
    assert json.loads(invoke.stdout)["status"] == "success"


def test_real_platform_example_rejected_without_traceback():
    result = run_module_cli("invoke", "--input", "examples/calibration_skill/invalid_real_platform_request.json")
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout
    assert json.loads(result.stdout)["status"] == "rejected"


def test_pretty_and_compact_json_parse():
    pretty = run_module_cli("manifest", "--pretty")
    compact = run_module_cli("manifest", "--compact")
    assert pretty.returncode == 0
    assert compact.returncode == 0
    assert "\n  " in pretty.stdout
    assert "\n  " not in compact.stdout
    assert json.loads(pretty.stdout)["skill_name"] == json.loads(compact.stdout)["skill_name"]


def test_manifest_exposes_no_hardware_operation():
    result = run_module_cli("operations")
    operations = json.loads(result.stdout)["operations"]
    assert result.returncode == 0
    assert all(op["hardware_motion_possible"] is False for op in operations)
    assert all(op["adapter_requirement"] == "mock" for op in operations)
