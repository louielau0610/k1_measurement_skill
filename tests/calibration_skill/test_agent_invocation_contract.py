import json
import subprocess
import sys
from pathlib import Path

from calibration_skill.schemas.validation import validate_skill_response

ROOT = Path(__file__).resolve().parents[2]
CLI = [sys.executable, "-m", "calibration_skill.cli"]


def run_cli(*args, input_text=None):
    return subprocess.run([*CLI, *args], cwd=ROOT, input=input_text, capture_output=True, text=True, timeout=30)


def test_invoke_response_is_skill_response_schema_compatible():
    result = run_cli("invoke", "--input", "examples/calibration_skill/dry_run_velocity_command.mock.json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert validate_skill_response(payload)["valid"]


def test_validate_response_is_skill_style_envelope():
    result = run_cli("validate", "--input", "examples/calibration_skill/preflight_request.mock.json")
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0.0"
    assert payload["operation"] == "preflight"
    assert payload["status"] == "success"
    assert validate_skill_response(payload)["valid"]


def test_unsupported_schema_version_structured_rejection():
    bad = json.loads((ROOT / "examples/calibration_skill/preflight_request.mock.json").read_text(encoding="utf-8"))
    bad["schema_version"] = "2.0.0"
    result = run_cli("invoke", "--input", "-", input_text=json.dumps(bad))
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "schema_version_unsupported"
    assert validate_skill_response(payload)["valid"]


def test_validate_does_not_create_adapter_for_schema_failure(monkeypatch):
    import calibration_skill.cli as cli
    import io

    def fail():
        raise AssertionError("adapter service should not be built for validation schema failure")

    monkeypatch.setattr(cli, "build_mock_dry_run_service", fail)
    bad = {"schema_version": "2.0.0", "request_id": "bad", "operation": "preflight", "platform": "mock", "dry_run": True}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(bad)))
    code = cli.main(["validate", "--input", "-"])
    assert code == 1
