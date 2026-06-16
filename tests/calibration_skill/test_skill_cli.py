import json
import subprocess
import sys
from pathlib import Path

import pytest

from calibration_skill.cli import main

ROOT = Path(__file__).resolve().parents[2]
CLI = [sys.executable, "-m", "calibration_skill.cli"]


def run_cli(*args, input_text=None):
    return subprocess.run(
        [*CLI, *args],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=30,
    )


def test_manifest_command_returns_json():
    result = run_cli("manifest")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["skill_name"] == "calibration_skill"


def test_operations_command_returns_json():
    result = run_cli("operations")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["operations"]) == 5


def test_validate_valid_request_success():
    result = run_cli("validate", "--input", "examples/calibration_skill/preflight_request.mock.json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "success"


def test_validate_invalid_request_rejected():
    result = run_cli("validate", "--input", "examples/calibration_skill/invalid_real_platform_request.json")
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["status"] == "rejected"


def test_invoke_valid_preflight_and_end_to_end():
    preflight = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json")
    assert preflight.returncode == 0
    assert json.loads(preflight.stdout)["result"]["preflight_report"]["is_ready"] is True
    e2e = run_cli("invoke", "--input", "examples/calibration_skill/dry_run_end_to_end.mock.json")
    assert e2e.returncode == 0
    assert json.loads(e2e.stdout)["audit_reference"] == "audit-example-dry_run_end_to_end"


def test_stdin_stdout_mode():
    text = (ROOT / "examples/calibration_skill/preflight_request.mock.json").read_text(encoding="utf-8")
    result = run_cli("invoke", "--input", "-", "--output", "-", input_text=text)
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "success"


def test_file_input_and_output(tmp_path):
    output = tmp_path / "response.json"
    result = run_cli(
        "invoke",
        "--input",
        "examples/calibration_skill/preflight_request.mock.json",
        "--output",
        str(output),
        "--pretty",
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "success"


def test_pretty_and_compact_output_deterministic():
    pretty1 = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json", "--pretty").stdout
    pretty2 = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json", "--pretty").stdout
    compact1 = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json", "--compact").stdout
    compact2 = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json", "--compact").stdout
    assert pretty1 == pretty2
    assert compact1 == compact2
    assert "\n  " in pretty1
    assert "\n  " not in compact1


def test_malformed_json_missing_input_and_output_parent_missing(tmp_path):
    malformed = run_cli("validate", "--input", "-", input_text="{")
    assert malformed.returncode == 3
    assert json.loads(malformed.stdout)["error"]["code"] == "serialization_failed"
    missing = run_cli("validate", "--input", "does-not-exist.json")
    assert missing.returncode == 2
    parent_missing = tmp_path / "missing" / "response.json"
    result = run_cli("invoke", "--input", "examples/calibration_skill/preflight_request.mock.json", "--output", str(parent_missing))
    assert result.returncode == 4
    assert not parent_missing.exists()


def test_unknown_operation_dry_run_false_and_real_platform_rejected():
    unknown = {
        "schema_version": "1.0.0",
        "request_id": "bad-op",
        "operation": "physical_move",
        "platform": "mock",
        "dry_run": True,
        "payload": {},
    }
    assert run_cli("validate", "--input", "-", input_text=json.dumps(unknown)).returncode == 1
    assert run_cli("validate", "--input", "examples/calibration_skill/invalid_dry_run_false_request.json").returncode == 1
    assert run_cli("invoke", "--input", "examples/calibration_skill/invalid_real_platform_request.json").returncode == 1


def test_unknown_cli_command_returns_usage_error():
    result = run_cli("nope")
    assert result.returncode == 2


def test_no_traceback_by_default_for_malformed_json():
    result = run_cli("validate", "--input", "-", input_text="{")
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout


def test_show_traceback_for_developer_debug(monkeypatch, capsys):
    import calibration_skill.cli as cli

    def boom(_args):
        raise RuntimeError("developer boom")

    monkeypatch.setattr(cli, "_invoke", boom)
    code = main(["invoke", "--input", "-", "--show-traceback"])
    captured = capsys.readouterr()
    assert code == 5
    assert "Traceback" in captured.err
