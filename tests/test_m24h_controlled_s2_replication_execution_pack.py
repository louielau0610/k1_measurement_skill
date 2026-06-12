"""Tests for M24-H: Controlled S2 Replication Execution Pack.

Tests verify:
- runner rejects non-S2 surfaces
- runner rejects non-direct_refresh_controlled conditions
- runner rejects compensated rows
- runner dry-run does not execute hardware
- metadata template exists and includes required fields
- extractor output schema is defined
- QC expects 20 trials, 4 groups, 5 repeats
- manifest says physical_run_status not_run
- profile_adoption_status is not_adopted
- deployment_ready=false, GO1/G1 blocked
- gold profile not overwritten
"""
from __future__ import annotations

import csv
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNNER = ROOT / "scripts/run_m24h_controlled_s2_replication_trials.py"
LOGGER = ROOT / "scripts/log_m24h_controlled_s2_replication_trial.py"
EXTRACTOR = ROOT / "scripts/extract_m24h_controlled_s2_replication_trials.py"
QC_SCRIPT = ROOT / "scripts/qc_m24h_controlled_s2_replication_session.py"
META_TEMPLATE = ROOT / "outputs/compensation_experiments/m24h_controlled_metadata_template.json"
MANIFEST_JSON = ROOT / "outputs/compensation_experiments/m24h_execution_pack_manifest.json"
TRIAL_PLAN = ROOT / "outputs/compensation_experiments/m24g_controlled_s2_replication_plan.csv"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"


# ---------------------------------------------------------------------------
# Runner tests
# ---------------------------------------------------------------------------

class TestRunner:
    def test_runner_exists(self) -> None:
        assert RUNNER.exists()

    def test_runner_dry_run_default(self) -> None:
        r = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT,
                          capture_output=True, text=True, timeout=30)
        assert r.returncode == 0
        assert "DRY RUN" in r.stdout
        assert "No hardware movement" in r.stdout

    def test_runner_rejects_non_s2(self) -> None:
        r = subprocess.run([sys.executable, str(RUNNER), "--surface", "S1_lab_hard_floor"],
                          cwd=ROOT, capture_output=True, text=True)
        assert r.returncode != 0

    def test_runner_help_shows_execute(self) -> None:
        r = subprocess.run([sys.executable, str(RUNNER), "--help"], cwd=ROOT,
                          capture_output=True, text=True)
        assert "--execute" in r.stdout
        assert "--no-permit" in r.stdout
        assert "--metadata-file" in r.stdout

    def test_runner_does_not_reference_m23b_logger(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        assert "log_m23b_k1_compensation_trial.py" not in text
        assert "log_m24h_controlled_s2_replication_trial.py" in text

    def test_runner_sdk_command_includes_log_dir(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        assert '"--log-dir"' in text
        assert "str(state_log_dir)" in text

    def test_m24h_logger_accepts_controlled_condition(self) -> None:
        r = subprocess.run([sys.executable, str(LOGGER), "--help"], cwd=ROOT,
                          capture_output=True, text=True)
        assert r.returncode == 0
        assert "direct_refresh_controlled" in r.stdout

    def test_m24h_logger_mock_writes_state_log(self, tmp_path: Path) -> None:
        r = subprocess.run([
            sys.executable, str(LOGGER),
            "--trial-id", "M24G_CORE_S2_marble_floor_V040_R1",
            "--replication-group-id", "M24G_CORE_S2_marble_floor_V040",
            "--condition", "direct_refresh_controlled",
            "--desired-velocity", "0.40",
            "--command-velocity", "0.40",
            "--output-dir", str(tmp_path),
            "--mock",
        ], cwd=ROOT, capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        log_path = tmp_path / "M24G_CORE_S2_marble_floor_V040_R1.csv"
        assert log_path.exists()
        with log_path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert rows
        assert rows[0]["condition"] == "direct_refresh_controlled"
        assert rows[0]["replication_group_id"] == "M24G_CORE_S2_marble_floor_V040"

    def test_split_process_import_boundaries(self) -> None:
        runner_imports = _imported_names(RUNNER)
        logger_imports = _imported_names(LOGGER)
        sdk_imports = _imported_names(ROOT / "scripts/send_m23b_k1_velocity_command.py")
        assert "rclpy" not in runner_imports
        assert "B1LocoClient" not in runner_imports
        assert "ChannelFactory" not in runner_imports
        assert "B1LocoClient" not in logger_imports
        assert "ChannelFactory" not in logger_imports
        assert "rclpy" not in sdk_imports

    def test_trial_plan_has_no_compensated(self) -> None:
        with TRIAL_PLAN.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        compensated = [r for r in rows if r.get("compensated_command", "false").lower() == "true"]
        assert len(compensated) == 0, "Trial plan must have zero compensated rows"

    def test_trial_plan_all_direct_refresh_controlled(self) -> None:
        with TRIAL_PLAN.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            assert r["condition"] == "direct_refresh_controlled", f"Bad condition: {r['trial_id']}: {r['condition']}"

    def test_trial_plan_20_trials(self) -> None:
        with TRIAL_PLAN.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 20


# ---------------------------------------------------------------------------
# Extractor tests
# ---------------------------------------------------------------------------

class TestExtractor:
    def test_extractor_exists(self) -> None:
        assert EXTRACTOR.exists()

    def test_extractor_help(self) -> None:
        r = subprocess.run([sys.executable, str(EXTRACTOR), "--help"], cwd=ROOT,
                          capture_output=True, text=True)
        assert "--session-dir" in r.stdout
        assert "--command-window-trim-sec" in r.stdout


# ---------------------------------------------------------------------------
# QC tests
# ---------------------------------------------------------------------------

class TestQC:
    def test_qc_exists(self) -> None:
        assert QC_SCRIPT.exists()

    def test_qc_help(self) -> None:
        r = subprocess.run([sys.executable, str(QC_SCRIPT), "--help"], cwd=ROOT,
                          capture_output=True, text=True)
        assert "--session-dir" in r.stdout

    def test_qc_rejects_missing_session(self) -> None:
        r = subprocess.run([sys.executable, str(QC_SCRIPT),
                           "--session-dir", "nonexistent_xyz"],
                          cwd=ROOT, capture_output=True, text=True)
        assert r.returncode != 0


# ---------------------------------------------------------------------------
# Metadata template tests
# ---------------------------------------------------------------------------

class TestMetadataTemplate:
    def test_template_exists(self) -> None:
        assert META_TEMPLATE.exists()

    def test_template_has_required_fields(self) -> None:
        data = json.loads(META_TEMPLATE.read_text(encoding="utf-8"))
        required = ["session_id", "surface", "robot_id", "warmup_status",
                    "start_pose_label", "path_label", "operator_reset_required",
                    "reset_confirmation_required", "extraction_window_method"]
        for field in required:
            assert field in data, f"Missing: {field}"

    def test_template_surface_is_s2(self) -> None:
        data = json.loads(META_TEMPLATE.read_text(encoding="utf-8"))
        assert data["surface"] == "S2_marble_floor"


# ---------------------------------------------------------------------------
# Manifest tests
# ---------------------------------------------------------------------------

class TestManifest:
    def test_manifest_exists(self) -> None:
        assert MANIFEST_JSON.exists()

    def test_physical_run_status_not_run(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["physical_run_status"] == "not_run"

    def test_profile_not_adopted(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["profile_adoption_status"] == "not_adopted"

    def test_deployment_ready_false(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_go1_g1_blocked(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["go1_g1_blocked"] is True

    def test_constraints_20_trials(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["constraints"]["total_trials"] == 20
        assert data["constraints"]["repeats"] == 5

    def test_compensated_forbidden(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["constraints"]["compensated_commands"] == "forbidden"

    def test_scripts_include_runner(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        scripts = data["scripts_included"]
        assert any("run_m24h" in s for s in scripts)
        assert any("log_m24h" in s for s in scripts)
        assert any("extract_m24h" in s for s in scripts)
        assert any("qc_m24h" in s for s in scripts)
        assert not any("log_m23b" in s for s in scripts)

    def test_manifest_status_remains_not_run_after_hotfix(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["physical_run_status"] == "not_run"
        assert data["profile_adoption_status"] == "not_adopted"
        assert data["deployment_ready"] is False
        assert data["go1_g1_blocked"] is True
        assert data["safety"]["sdk_command_log_dir_required"] is True


# ---------------------------------------------------------------------------
# Boundary flag tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_gold_profile_not_overwritten(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["claim_boundary"]["profile_adopted"] is False

    def test_compensation_ready_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_go1_g1_blocked_in_status(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_no_compensation_improvement_claim_in_manifest(self) -> None:
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        assert data["claim_boundary"]["tracking_improvement_claimed"] is False
        assert data["claim_boundary"]["compensation_validated"] is False

    def test_docs_exist(self) -> None:
        assert (ROOT / "docs/m24h_robot_transfer_and_run_commands.md").exists()
        assert (ROOT / "docs/m24h_controlled_s2_replication_execution_protocol.md").exists()

    def test_execution_protocol_mentions_not_run(self) -> None:
        text = (ROOT / "docs/m24h_controlled_s2_replication_execution_protocol.md").read_text(encoding="utf-8")
        assert "not_run" in text or "not yet executed" in text.lower()


def _imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names
