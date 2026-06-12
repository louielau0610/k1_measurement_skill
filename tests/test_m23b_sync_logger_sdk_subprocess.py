from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts/run_m23b_k1_compensation_trials.py"
SDK_PATH = ROOT / "scripts/send_m23b_k1_velocity_command.py"
LOGGER_PATH = ROOT / "scripts/log_m23b_k1_compensation_trial.py"
PROTOCOL_DOC = ROOT / "docs/m23b_k1_physical_compensation_execution_protocol.md"
TRANSFER_DOC = ROOT / "docs/m23b_robot_transfer_and_run_commands.md"
MANIFEST_JSON = ROOT / "outputs/compensation_experiments/m23b_execution_pack_manifest.json"

spec = importlib.util.spec_from_file_location("run_m23b", RUNNER_PATH)
run_m23b = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_m23b)


def test_build_sdk_command_supports_sdk_python() -> None:
    cmd = run_m23b._build_sdk_command(
        "scripts/send.py",
        "T1",
        0.4,
        "eth0",
        Path("logs"),
        sdk_python="/opt/sdk/python3",
        sdk_env_setup=None,
    )
    assert cmd[0] == "/opt/sdk/python3"
    assert "scripts/send.py" in cmd


def test_build_sdk_command_supports_sdk_env_setup() -> None:
    cmd = run_m23b._build_sdk_command(
        "scripts/send.py",
        "T1",
        0.4,
        "eth0",
        Path("logs"),
        sdk_python="/opt/sdk/python3",
        sdk_env_setup="source /some/setup.bash",
    )
    assert cmd[:2] == ["bash", "-lc"]
    assert "source /some/setup.bash &&" in cmd[2]
    assert "/opt/sdk/python3" in cmd[2]


def test_runner_launches_logger_before_sdk_and_does_not_wait_first(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    events: list[str] = []
    monkeypatch.setattr(run_m23b.time, "sleep", lambda value: events.append(f"sleep:{value}"))
    monkeypatch.setattr(run_m23b.subprocess, "Popen", _fake_popen_factory(events, sdk_rc=0, logger_rc=0))
    plan = _trial_plan(tmp_path)
    rc = run_m23b.main([
        "--surface", "S2_marble_floor",
        "--session-id", "sync_success",
        "--execute", "--no-permit",
        "--trial-plan", str(plan),
        "--base-dir", str(tmp_path),
        "--logger-startup-sec", "0.25",
    ])
    assert rc == 0
    assert events[:3] == ["popen:logger", "sleep:0.25", "popen:sdk"]
    assert events.index("popen:sdk") < events.index("wait:logger")
    rows = _records(tmp_path / "sync_success" / "trial_records.csv")
    assert rows[0]["physical_run_status"] == "executed"
    assert rows[0]["valid"] == "true"
    assert "logger_rc=0; sdk_rc=0" in rows[0]["notes"]


def test_runner_marks_sdk_failure_invalid(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    events: list[str] = []
    monkeypatch.setattr(run_m23b.time, "sleep", lambda value: events.append(f"sleep:{value}"))
    monkeypatch.setattr(run_m23b.subprocess, "Popen", _fake_popen_factory(events, sdk_rc=1, logger_rc=0))
    rc = run_m23b.main([
        "--surface", "S2_marble_floor", "--session-id", "sdk_fail",
        "--execute", "--no-permit", "--trial-plan", str(_trial_plan(tmp_path)),
        "--base-dir", str(tmp_path),
    ])
    assert rc == 0
    row = _records(tmp_path / "sdk_fail" / "trial_records.csv")[0]
    assert row["valid"] == "false"
    assert row["physical_run_status"] == "sdk_failed"
    assert row["invalid_reason"] == "sdk_subprocess_failed_rc=1"


def test_runner_marks_logger_failure_invalid(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    events: list[str] = []
    monkeypatch.setattr(run_m23b.time, "sleep", lambda value: events.append(f"sleep:{value}"))
    monkeypatch.setattr(run_m23b.subprocess, "Popen", _fake_popen_factory(events, sdk_rc=0, logger_rc=2))
    rc = run_m23b.main([
        "--surface", "S2_marble_floor", "--session-id", "logger_fail",
        "--execute", "--no-permit", "--trial-plan", str(_trial_plan(tmp_path)),
        "--base-dir", str(tmp_path),
    ])
    assert rc == 0
    row = _records(tmp_path / "logger_fail" / "trial_records.csv")[0]
    assert row["valid"] == "false"
    assert row["physical_run_status"] == "logger_failed"
    assert row["invalid_reason"] == "logger_subprocess_failed_rc=2"


def test_runner_help_shows_hotfix2_args() -> None:
    result = subprocess.run([sys.executable, str(RUNNER_PATH), "--help"], cwd=ROOT, capture_output=True, text=True)
    assert "--logger-startup-sec" in result.stdout
    assert "--sdk-python" in result.stdout
    assert "--sdk-env-setup" in result.stdout
    assert "--command-timeout-sec" in result.stdout
    assert "--logger-timeout-sec" in result.stdout


def test_sdk_script_prints_sys_executable_and_writes_import_log(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable, str(SDK_PATH),
            "--trial-id", "IMPORT_FAIL",
            "--command-velocity", "0.4",
            "--log-dir", str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "sys.executable" in result.stdout
    assert "use --sdk-python" in (result.stdout + result.stderr)
    log = json.loads((tmp_path / "IMPORT_FAIL_cmd_log.json").read_text(encoding="utf-8"))
    assert "sys_executable" in log
    assert "import_status" in log
    assert log["exit_status"] == "sdk_import_failed"


def test_process_isolation_import_boundaries() -> None:
    runner_lines = RUNNER_PATH.read_text(encoding="utf-8").splitlines()
    sdk_lines = SDK_PATH.read_text(encoding="utf-8").splitlines()
    logger = LOGGER_PATH.read_text(encoding="utf-8")
    assert not _has_import(runner_lines, "rclpy")
    assert not _has_import(runner_lines, "B1LocoClient")
    assert not _has_import(runner_lines, "ChannelFactory")
    assert not _has_import(sdk_lines, "rclpy")
    assert "B1LocoClient" not in logger
    assert "ChannelFactory" not in logger


def test_docs_mention_invalid_debug_failed_sessions_and_no_validation_claim() -> None:
    text = PROTOCOL_DOC.read_text(encoding="utf-8") + TRANSFER_DOC.read_text(encoding="utf-8")
    assert "m23b_k1_s2_20260612_095811" in text
    assert "failed auto-subprocess" in text.lower() or "failed auto subprocess" in text.lower()
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    assert manifest["deployment_ready"] is False
    assert manifest["claim_boundary"]["tracking_improvement_claimed"] is False
    assert manifest["claim_boundary"]["compensation_validated"] is False


class _FakeProc:
    def __init__(self, name: str, rc: int, events: list[str]) -> None:
        self.name = name
        self.rc = rc
        self.events = events
        self._terminated = False

    def wait(self, timeout: float | None = None) -> int:
        self.events.append(f"wait:{self.name}")
        return -15 if self._terminated and self.name == "logger" else self.rc

    def poll(self) -> int | None:
        return None if self.name == "logger" and not self._terminated else self.rc

    def terminate(self) -> None:
        self.events.append(f"terminate:{self.name}")
        self._terminated = True

    def kill(self) -> None:
        self.events.append(f"kill:{self.name}")
        self._terminated = True


def _fake_popen_factory(events: list[str], *, sdk_rc: int, logger_rc: int):
    def fake_popen(cmd):
        name = "logger" if "log_m23b" in " ".join(cmd) else "sdk"
        events.append(f"popen:{name}")
        return _FakeProc(name, logger_rc if name == "logger" else sdk_rc, events)

    return fake_popen


def _trial_plan(tmp_path: Path) -> Path:
    path = tmp_path / "trial_plan.csv"
    fields = [
        "trial_id", "pair_id", "surface", "desired_velocity_mps", "condition",
        "command_velocity_mps", "compensator_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "trial_id": "M23B_TEST_SYNC_001",
            "pair_id": "P001",
            "surface": "S2_marble_floor",
            "desired_velocity_mps": "0.4",
            "condition": "direct",
            "command_velocity_mps": "0.4",
            "compensator_status": "",
        })
    return path


def _records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _has_import(lines: list[str], module_name: str) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"import {module_name}") or stripped.startswith(f"from {module_name}"):
            return True
    return False
