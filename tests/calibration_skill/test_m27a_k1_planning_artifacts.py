"""M27-A K1 Planning Artifacts Validation Tests.

Validates that M27-A remains a planning/audit milestone without accidental migration:
- JSON artifact structure
- Mapping completeness
- Risk register contains required risks
- Hardware-gated tests are marked
- K1 support remains unavailable in manifest
- No K1 factory registered in AdapterRegistry
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ENG_DIR = REPO_ROOT / "outputs" / "engineering"


def _load_json(name: str) -> dict:
    path = ENG_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not found — may not be created yet")
    return json.loads(path.read_text(encoding="utf-8"))


# ── JSON artifact structure tests ──────────────────────────────────────

class TestM27AJsonArtifacts:
    """Verify all M27-A JSON artifacts parse and have required fields."""

    REQUIRED_ARTIFACTS = [
        "m27a_initial_state.json",
        "m27a_k1_legacy_inventory.json",
        "m27a_k1_command_path_audit.json",
        "m27a_k1_telemetry_path_audit.json",
        "m27a_k1_safety_gate_audit.json",
        "m27a_k1_to_robot_adapter_mapping.json",
        "m27a_k1_compatibility_test_plan.json",
        "m27a_k1_migration_risk_register.json",
        "m27a_readiness.json",
        "m27a_validation_summary.json",
    ]

    @pytest.mark.parametrize("filename", REQUIRED_ARTIFACTS)
    def test_artifact_exists_and_parses(self, filename):
        path = ENG_DIR / filename
        assert path.exists(), f"Missing artifact: {filename}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{filename} is not a JSON object"

    def test_inventory_has_summary(self):
        data = _load_json("m27a_k1_legacy_inventory.json")
        assert "inventory" in data, "Inventory missing 'inventory' key"
        assert len(data["inventory"]) > 0, "Inventory is empty"
        assert "summary" in data, "Inventory missing 'summary' key"

    def test_inventory_verified_motion_chain(self):
        data = _load_json("m27a_k1_legacy_inventory.json")
        summary = data.get("summary", {})
        assert summary.get("verified_motion_chain") == "kPrepare -> kWalking -> Move(vx, 0.0, 0.0)"

    def test_inventory_verified_safe_speed(self):
        data = _load_json("m27a_k1_legacy_inventory.json")
        summary = data.get("summary", {})
        assert summary.get("verified_safe_speed_max") == "0.6 m/s"

    def test_command_audit_has_lifecycle(self):
        data = _load_json("m27a_k1_command_path_audit.json")
        assert "lifecycle_sequence" in data
        assert len(data["lifecycle_sequence"]) > 0

    def test_command_audit_verified_chain(self):
        data = _load_json("m27a_k1_command_path_audit.json")
        chain = data.get("verified_motion_chain", {})
        assert chain.get("verification_status") == "verified_from_repository_evidence"
        assert "kPrepare" in str(chain.get("sequence", []))

    def test_telemetry_audit_has_sources(self):
        data = _load_json("m27a_k1_telemetry_path_audit.json")
        assert "telemetry_sources" in data
        assert len(data["telemetry_sources"]) > 0

    def test_safety_audit_has_config(self):
        data = _load_json("m27a_k1_safety_gate_audit.json")
        config = data.get("authoritative_safety_config", {})
        assert config.get("verified") is True
        assert config.get("content", {}).get("safe_command_speed_max") == 0.6

    def test_safety_audit_fail_closed(self):
        data = _load_json("m27a_k1_safety_gate_audit.json")
        assert data.get("dry_run_default", {}).get("status") is True
        assert data.get("fail_closed_behavior") is not None


# ── Mapping completeness tests ─────────────────────────────────────────

class TestMappingCompleteness:
    """Verify K1-to-RobotAdapter mapping is complete."""

    REQUIRED_CONTRACTS = [
        "RobotIdentity",
        "CapabilityDescriptor",
        "ConnectionConfig",
        "RobotAdapter.connect",
        "RobotAdapter.disconnect",
        "RobotAdapter.preflight",
        "RobotAdapter.motion_state",
        "RobotAdapter.enter_locomotion_ready",
        "RobotAdapter.send_velocity_command",
        "RobotAdapter.stop",
        "RobotAdapter.restore_safe_state",
        "TelemetryStream",
        "SafetyEnvelope",
        "OperatorAuthorization",
        "CommandReceipt",
        "ExecutionAuditRecord",
    ]

    def test_all_contracts_mapped(self):
        data = _load_json("m27a_k1_to_robot_adapter_mapping.json")
        mapped_contracts = {m["contract"] for m in data.get("mappings", [])}
        for contract in self.REQUIRED_CONTRACTS:
            assert contract in mapped_contracts, f"Missing mapping for {contract}"

    def test_high_risk_items_identified(self):
        data = _load_json("m27a_k1_to_robot_adapter_mapping.json")
        summary = data.get("summary", {})
        assert summary.get("high_risk") >= 3, "Should identify at least 3 high-risk mappings"
        high_risk = summary.get("high_risk_items", [])
        assert "send_velocity_command" in high_risk
        assert "stop" in high_risk


# ── Risk register tests ────────────────────────────────────────────────

class TestRiskRegister:
    """Verify risk register contains required risks."""

    REQUIRED_RISKS = [
        "SDK environment mismatch",
        "FastDDS configuration",
        "K1 mode lifecycle uncertainty",
        "Command frame ambiguity",
        "Odometry frame ambiguity",
        "Yaw drift variability",
        "Speed deadband",
        "Profile/environment mismatch",
        "Battery/state missing data",
        "Operator confirmation bypass risk",
        "Stale telemetry",
        "Stop acknowledgement uncertainty",
        "Import-time vendor side effects",
        "Package dependency contamination",
        "Windows vs Ubuntu divergence",
    ]

    def test_required_risks_present(self):
        data = _load_json("m27a_k1_migration_risk_register.json")
        risk_names = {r["name"] for r in data.get("risks", [])}
        for risk in self.REQUIRED_RISKS:
            assert risk in risk_names, f"Missing risk: {risk}"

    def test_risks_have_severity_and_mitigation(self):
        data = _load_json("m27a_k1_migration_risk_register.json")
        for risk in data.get("risks", []):
            assert "severity" in risk, f"Risk missing severity: {risk.get('name')}"
            assert "mitigation" in risk, f"Risk missing mitigation: {risk.get('name')}"
            assert "test_evidence_required" in risk, f"Risk missing test evidence: {risk.get('name')}"


# ── Hardware-gated test marking tests ──────────────────────────────────

class TestHardwareGatedMarking:
    """Verify hardware-gated tests are explicitly marked."""

    def test_all_hardware_tests_marked(self):
        data = _load_json("m27a_k1_compatibility_test_plan.json")
        hw_tests = data.get("hardware_gated_tests", [])
        assert len(hw_tests) > 0, "Must have hardware-gated tests"
        for test in hw_tests:
            assert test.get("requires_hardware") is True, f"HW test {test['id']} must have requires_hardware: true"
            assert test.get("ci_excluded") is True, f"HW test {test['id']} must have ci_excluded: true"

    def test_non_hardware_tests_not_marked_hardware(self):
        data = _load_json("m27a_k1_compatibility_test_plan.json")
        nh_tests = data.get("non_hardware_tests", [])
        assert len(nh_tests) > 0, "Must have non-hardware tests"
        for test in nh_tests:
            assert test.get("requires_hardware") is False, f"NH test {test['id']} must have requires_hardware: false"


# ── K1 support unavailable tests ───────────────────────────────────────

class TestK1SupportUnavailable:
    """Verify K1 remains unsupported in new runtime."""

    def test_k1_not_in_adapter_registry(self):
        """M26-C AdapterRegistry must reject K1 registration."""
        from calibration_skill.adapters.registry import AdapterRegistry
        from calibration_skill.domain.enums import RobotPlatform

        registry = AdapterRegistry()
        platforms = registry.list_registered_platforms()
        assert RobotPlatform.BOOSTER_K1 not in platforms, "K1 must not be auto-registered"
        # Registry starts empty; MOCK is only registered when explicitly done so in M26-C tests

    def test_k1_registration_rejected(self):
        """Registering K1 in M26-C registry must raise error."""
        from calibration_skill.adapters.registry import AdapterRegistry
        from calibration_skill.domain.capabilities import CapabilityDescriptor
        from calibration_skill.domain.enums import RobotPlatform

        registry = AdapterRegistry()
        caps = CapabilityDescriptor(platform_id="test")
        with pytest.raises(ValueError, match="M26-C registry only accepts mock"):
            registry.register(
                RobotPlatform.BOOSTER_K1,
                creator=lambda cfg: None,  # type: ignore
                capabilities=caps,
                dry_run_only=True,
            )

    def test_m26d_manifest_k1_unavailable(self):
        """M26-D manifest must mark K1 as unavailable."""
        manifest_path = ENG_DIR / "m26d_skill_manifest.json"
        if not manifest_path.exists():
            pytest.skip("M26-D manifest not found")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        k1_status = manifest.get("platform_support", {}).get("booster_k1", {}).get("status", "unknown")
        assert k1_status != "supported", f"M26-D manifest must not mark K1 supported (got: {k1_status})"

    def test_no_booster_sdk_in_calibration_skill(self):
        """Verify no Booster SDK import in calibration_skill package."""
        import ast
        skill_dir = REPO_ROOT / "calibration_skill"
        forbidden = ("booster_robotics_sdk", "B1LocoClient", "ChannelFactory", "RobotMode")
        for py_file in skill_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in (node.names if hasattr(node, 'names') else []):
                        for forbidden_mod in forbidden:
                            if forbidden_mod in str(alias.name):
                                pytest.fail(
                                    f"Forbidden import '{alias.name}' in {py_file.relative_to(REPO_ROOT)}"
                                )


# ── Readiness tests ────────────────────────────────────────────────────

class TestM27AReadiness:
    """Verify M27-A readiness does not claim implementation."""

    def test_readiness_k1_migration_planned_not_implemented(self):
        data = _load_json("m27a_readiness.json")
        readiness = data.get("readiness", {})
        assert readiness.get("k1_adapter_migration", {}).get("maturity") == "planned"
        assert readiness.get("k1_new_runtime_support", {}).get("maturity") == "not_started"
        assert readiness.get("hardware_verification", {}).get("maturity") == "not_started"

    def test_readiness_no_false_claims(self):
        data = _load_json("m27a_readiness.json")
        prohibited = data.get("prohibited_claims", [])
        assert len(prohibited) > 0, "Must have prohibited claims"
        # Verify no K1 support claim
        readiness = data.get("readiness", {})
        for key in ("k1_new_runtime_support", "hardware_verification"):
            assert readiness.get(key, {}).get("maturity") != "bench_verified", f"{key} must not be bench_verified"
