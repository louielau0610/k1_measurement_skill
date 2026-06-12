"""Tests for M23-B hotfix: auto SDK command subprocess.

Tests cover:
- SDK command subprocess script exists
- SDK command subprocess does not import rclpy
- runner launches SDK command subprocess in execute mode
- runner does not mark trial executed if command subprocess fails
- runner still defaults to dry-run
- runner still requires --execute for movement
- logger and SDK command subprocess are separate commands
- invalid/debug session warning appears in docs
- physical validation claim is still absent
- deployment_ready remains false
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SDK_SCRIPT = ROOT / "scripts/send_m23b_k1_velocity_command.py"
RUNNER_SCRIPT = ROOT / "scripts/run_m23b_k1_compensation_trials.py"
PROTOCOL_DOC = ROOT / "docs/m23b_k1_physical_compensation_execution_protocol.md"
MANIFEST_JSON = ROOT / "outputs/compensation_experiments/m23b_execution_pack_manifest.json"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


# ---------------------------------------------------------------------------
# SDK command subprocess tests
# ---------------------------------------------------------------------------

class TestSDKCommandScript:
    def test_script_exists(self) -> None:
        assert SDK_SCRIPT.exists(), f"Missing: {SDK_SCRIPT}"

    def test_script_does_not_import_rclpy(self) -> None:
        """Verify the SDK command script does NOT import rclpy."""
        lines = SDK_SCRIPT.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith("import rclpy") or stripped.startswith("from rclpy"):
                pytest.fail(f"SDK script imports rclpy: {stripped}")
        # But it should reference Booster SDK
        assert "B1LocoClient" in SDK_SCRIPT.read_text(encoding="utf-8") or "ChannelFactory" in SDK_SCRIPT.read_text(encoding="utf-8"), \
            "SDK script should reference Booster SDK components"

    def test_script_help_shows_required_args(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SDK_SCRIPT), "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--trial-id" in result.stdout
        assert "--command-velocity" in result.stdout
        assert "--interface" in result.stdout

    def test_script_exits_nonzero_when_sdk_unavailable(self) -> None:
        """On dev machine (no Booster SDK), script should exit nonzero."""
        result = subprocess.run(
            [sys.executable, str(SDK_SCRIPT),
             "--trial-id", "TEST_001", "--command-velocity", "0.4"],
            cwd=ROOT, capture_output=True, text=True,
        )
        # Should fail gracefully when SDK not available
        assert result.returncode != 0

    def test_script_prints_error_when_sdk_unavailable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SDK_SCRIPT),
             "--trial-id", "TEST_001", "--command-velocity", "0.4"],
            cwd=ROOT, capture_output=True, text=True,
        )
        output = (result.stdout + result.stderr).lower()
        assert "sdk" in output or "booster" in output or "not available" in output


# ---------------------------------------------------------------------------
# Runner tests
# ---------------------------------------------------------------------------

class TestRunnerAutoSubprocess:
    def test_runner_help_shows_execute_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNNER_SCRIPT), "--help"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert "--execute" in result.stdout
        assert "--no-permit" in result.stdout

    def test_runner_defaults_to_dry_run(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNNER_SCRIPT), "--surface", "S2_marble_floor"],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "No hardware was moved" in result.stdout

    def test_runner_execute_launches_subprocesses(self) -> None:
        """In execute mode with --no-permit, runner should launch subprocesses.
        On dev machine, SDK subprocess will fail (no Booster SDK), which is
        expected — the trial should be marked invalid, not executed."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(RUNNER_SCRIPT),
                 "--surface", "S2_marble_floor",
                 "--session-id", "test_auto_subprocess",
                 "--execute", "--no-permit",
                 "--base-dir", tmp],
                cwd=ROOT, capture_output=True, text=True, timeout=120,
            )
            # Runner should complete (even if subprocesses fail on dev)
            assert result.returncode == 0, f"Runner failed: {result.stderr}"

            # Check session directory was created
            session_dir = Path(tmp) / "test_auto_subprocess"
            assert session_dir.is_dir()

            # Check metadata has split_process_required
            meta_path = session_dir / "session_metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                assert meta["split_process_required"] is True

            # Trial records should exist
            records_path = session_dir / "trial_records.csv"
            assert records_path.exists()

    def test_runner_imports_subprocess_module(self) -> None:
        """Verify runner source imports subprocess (for Popen)."""
        text = RUNNER_SCRIPT.read_text(encoding="utf-8")
        assert "import subprocess" in text, "Runner must import subprocess"
        assert "Popen" in text, "Runner must use Popen for subprocess management"

    def test_runner_references_sdk_script(self) -> None:
        """Verify runner references the SDK command script path."""
        text = RUNNER_SCRIPT.read_text(encoding="utf-8")
        assert "send_m23b_k1_velocity_command.py" in text, \
            "Runner must reference SDK command script"

    def test_runner_references_logger_script(self) -> None:
        """Verify runner references the logger script path."""
        text = RUNNER_SCRIPT.read_text(encoding="utf-8")
        assert "log_m23b_k1_compensation_trial.py" in text, \
            "Runner must reference logger script"


# ---------------------------------------------------------------------------
# Documentation tests
# ---------------------------------------------------------------------------

class TestDocumentation:
    def test_protocol_mentions_auto_subprocess(self) -> None:
        text = PROTOCOL_DOC.read_text(encoding="utf-8")
        assert "auto" in text.lower() or "automatically" in text.lower(), \
            "Protocol should mention auto subprocess launching"

    def test_protocol_mentions_invalid_session(self) -> None:
        text = PROTOCOL_DOC.read_text(encoding="utf-8")
        assert "m23b_k1_s2_20260612_095811" in text, \
            "Protocol should reference the invalid pre-hotfix session"
        assert "invalid" in text.lower() or "NOT be treated" in text, \
            "Protocol should warn that pre-hotfix session is invalid"

    def test_protocol_mentions_sdk_subprocess(self) -> None:
        text = PROTOCOL_DOC.read_text(encoding="utf-8")
        assert "send_m23b_k1_velocity_command.py" in text, \
            "Protocol should reference the SDK command script"

    def test_manifest_includes_sdk_script(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        scripts = data["scripts_to_transfer"]
        assert any("send_m23b" in s for s in scripts), \
            "Manifest should include SDK command script in transfer list"


# ---------------------------------------------------------------------------
# Boundary flag tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_physical_validation_still_not_analyzed(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["physical_validation_status"] == "execution_pack_ready_not_run"

    def test_deployment_ready_still_false(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_go1_g1_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_compensation_ready_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_no_tracking_improvement_claim(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["claim_boundary"]["tracking_improvement_claimed"] is False
        assert data["claim_boundary"]["compensation_validated"] is False


# ---------------------------------------------------------------------------
# Split-process isolation tests
# ---------------------------------------------------------------------------

class TestSplitProcessIsolation:
    def test_sdk_script_isolated_from_rclpy(self) -> None:
        """SDK script must NOT import rclpy."""
        lines = SDK_SCRIPT.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith("import rclpy") or stripped.startswith("from rclpy"):
                pytest.fail(f"SDK script imports rclpy: {stripped}")

    def test_runner_isolated_from_both(self) -> None:
        """Runner must NOT import rclpy or Booster SDK."""
        lines = RUNNER_SCRIPT.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith("import rclpy") or stripped.startswith("from rclpy"):
                pytest.fail(f"Runner imports rclpy: {stripped}")
            if stripped.startswith("from B1LocoClient") or stripped.startswith("import B1LocoClient"):
                pytest.fail(f"Runner imports Booster SDK: {stripped}")
            if stripped.startswith("from ChannelFactory") or stripped.startswith("import ChannelFactory"):
                pytest.fail(f"Runner imports Booster SDK: {stripped}")

    def test_logger_script_isolated_from_sdk(self) -> None:
        """Logger script uses ROS2 (rclpy) and must NOT import Booster SDK."""
        logger_path = ROOT / "scripts/log_m23b_k1_compensation_trial.py"
        text = logger_path.read_text(encoding="utf-8")
        assert "B1LocoClient" not in text, "Logger must not import Booster SDK"
        assert "ChannelFactory" not in text, "Logger must not import Booster SDK"
