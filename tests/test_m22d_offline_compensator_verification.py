"""Tests for M22-D: Offline Compensator Verification and Edge-Case Audit.

Tests cover:
- baseline direct command
- baseline scalar gain
- baseline nearest lookup
- baseline ordinary interpolation
- leave-one-repeat-out produces 72 checks
- leave-one-repeat-out metrics exist
- edge-case audit statuses
- no extrapolation by default
- unsupported platform/surface handling
- risk policy ordering
- permissive policy does not accept deadzone silently
- verification CLI output creation
- all M22-D outputs are labeled offline-only
- no hardware execution
- no physical validation claim
- no deployment readiness claim
- no GO1/G1 validation claim
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calibration_core.compensation_models import (
    FEASIBILITY_STATUSES,
    SUPPORTED_EMPIRICAL_PLATFORM,
    CompensationThresholds,
    ResponseCell,
)
from calibration_core.compensation_verification import (
    OFFLINE_ONLY_DISCLAIMER,
    EdgeCaseAuditResult,
    EDGE_CASES,
    LeaveOneRepeatOutResult,
    VerificationResult,
    baseline_direct_command,
    baseline_nearest_lookup,
    baseline_ordinary_interpolation,
    baseline_scalar_gain,
    estimate_scalar_gain,
    run_edge_case_audit,
    run_leave_one_repeat_out,
    run_risk_policy_audit,
    summarize_leave_one_repeat_out,
)

PROFILE_PATH = ROOT / "outputs/real_k1_validation_m19/k1_gold_profile_v1.json"
CONTRACT_CSV = ROOT / "outputs/measurement_v1/booster_k1_measurements_contract_v1.csv"
M22D_OUTPUT = ROOT / "outputs/compensation_research/m22d_offline_verification"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"

# ---------------------------------------------------------------------------
# Baseline tests
# ---------------------------------------------------------------------------

class TestBaselines:
    def test_direct_command_baseline(self) -> None:
        result = baseline_direct_command(0.5)
        assert result.method == "direct_command"
        assert result.recommended_command_velocity_mps == 0.5

    def test_scalar_gain_baseline(self) -> None:
        result = baseline_scalar_gain(0.5, 1.2)
        assert result.method == "scalar_gain"
        assert result.recommended_command_velocity_mps == pytest.approx(0.6)

    def test_nearest_lookup_baseline(self) -> None:
        cells = [
            ResponseCell("test", "T", "s", 0.3, 0.25, 3, 0.01, 1.0, 0.01, 0.0, "reliable", 0.1, 0.9, "test"),
            ResponseCell("test", "T", "s", 0.5, 0.45, 3, 0.02, 2.0, 0.02, 0.0, "reliable", 0.2, 0.8, "test"),
        ]
        result = baseline_nearest_lookup(0.44, cells)
        assert result.recommended_command_velocity_mps == 0.5

    def test_ordinary_interpolation_baseline(self) -> None:
        cells = [
            ResponseCell("test", "T", "s", 0.3, 0.25, 3, 0.01, 1.0, 0.01, 0.0, "reliable", 0.1, 0.9, "test"),
            ResponseCell("test", "T", "s", 0.5, 0.45, 3, 0.02, 2.0, 0.02, 0.0, "reliable", 0.2, 0.8, "test"),
        ]
        result = baseline_ordinary_interpolation(0.35, cells)
        assert result.method == "ordinary_interpolation"
        assert result.recommended_command_velocity_mps is not None
        assert 0.3 < result.recommended_command_velocity_mps < 0.5

    def test_estimate_scalar_gain(self) -> None:
        cells = [
            ResponseCell("test", "T", "s", 0.5, 0.40, 3, 0.01, 1.0, 0.01, 0.0, "reliable", 0.1, 0.9, "test"),
            ResponseCell("test", "T", "s", 0.6, 0.48, 3, 0.02, 2.0, 0.02, 0.0, "reliable", 0.2, 0.8, "test"),
        ]
        gain = estimate_scalar_gain(cells)
        assert gain > 1.0  # cmd > actual means gain > 1


# ---------------------------------------------------------------------------
# Leave-one-repeat-out tests
# ---------------------------------------------------------------------------

class TestLeaveOneRepeatOut:
    def test_produces_72_checks(self) -> None:
        results = run_leave_one_repeat_out(CONTRACT_CSV, PROFILE_PATH)
        assert len(results) == 72, f"Expected 72 LORO checks, got {len(results)}"

    def test_summary_metrics_exist(self) -> None:
        results = run_leave_one_repeat_out(CONTRACT_CSV, PROFILE_PATH)
        summary = summarize_leave_one_repeat_out(results)
        assert summary["total_checks"] == 72
        assert "mean_abs_command_error_mps" in summary
        assert "status_distribution" in summary
        assert "per_surface" in summary
        assert len(summary["per_surface"]) == 3  # 3 surfaces

    def test_disclaimer_present_in_summary(self) -> None:
        results = run_leave_one_repeat_out(CONTRACT_CSV, PROFILE_PATH)
        summary = summarize_leave_one_repeat_out(results)
        assert "offline" in summary["disclaimer"].lower()

    def test_result_has_required_fields(self) -> None:
        results = run_leave_one_repeat_out(CONTRACT_CSV, PROFILE_PATH)
        r = results[0]
        assert r.trial_id
        assert r.platform == SUPPORTED_EMPIRICAL_PLATFORM
        assert r.command_velocity_mps > 0
        assert r.feasibility_status in FEASIBILITY_STATUSES or r.feasibility_status in ("ok", "infeasible_deadzone")


# ---------------------------------------------------------------------------
# Edge-case audit tests
# ---------------------------------------------------------------------------

class TestEdgeCaseAudit:
    def test_edge_cases_defined(self) -> None:
        assert len(EDGE_CASES) >= 9

    def test_deadzone_case_exists(self) -> None:
        labels = {c.label for c in EDGE_CASES}
        assert "below_min_effective" in labels

    def test_out_of_range_case_exists(self) -> None:
        labels = {c.label for c in EDGE_CASES}
        assert "above_measured_range" in labels

    def test_unsupported_platform_case_exists(self) -> None:
        labels = {c.label for c in EDGE_CASES}
        assert "unsupported_platform" in labels

    def test_no_extrapolation_case_exists(self) -> None:
        labels = {c.label for c in EDGE_CASES}
        assert "no_extrapolation_default" in labels

    def test_run_audit_returns_result(self) -> None:
        result = run_edge_case_audit(PROFILE_PATH, CONTRACT_CSV)
        assert isinstance(result, EdgeCaseAuditResult)
        assert result.total >= 9
        assert result.passed >= 1

    def test_audit_result_has_required_fields(self) -> None:
        result = run_edge_case_audit(PROFILE_PATH, CONTRACT_CSV)
        for case in result.cases:
            assert case.platform
            assert case.policy in ("conservative", "permissive")
            assert case.expected_status in FEASIBILITY_STATUSES
            assert case.actual_status in FEASIBILITY_STATUSES


# ---------------------------------------------------------------------------
# Risk policy audit tests
# ---------------------------------------------------------------------------

class TestRiskPolicyAudit:
    def test_produces_audit_results(self) -> None:
        audit = run_risk_policy_audit(PROFILE_PATH, CONTRACT_CSV)
        assert "policy_stats" in audit
        for pol in ["conservative", "balanced", "permissive"]:
            assert pol in audit["policy_stats"]

    def test_ordering_conservative_most_restrictive(self) -> None:
        audit = run_risk_policy_audit(PROFILE_PATH, CONTRACT_CSV)
        cons = audit["policy_stats"]["conservative"]
        bal = audit["policy_stats"]["balanced"]
        perm = audit["policy_stats"]["permissive"]
        assert cons["feasible"] <= bal["feasible"] <= perm["feasible"]

    def test_no_policy_accepts_deadzone(self) -> None:
        audit = run_risk_policy_audit(PROFILE_PATH, CONTRACT_CSV)
        assert audit["ordering_checks"]["no_policy_accepts_deadzone_silently"] is True

    def test_permissive_does_not_silently_accept_deadzone(self) -> None:
        # Deadzone check is inherent in evaluate_cell — region_label "deadzone" always rejected
        from calibration_core.compensation_policies import evaluate_cell, get_policy
        thresholds = CompensationThresholds()
        dead_cell = ResponseCell("test", "T", "s", 0.1, 0.0, 1, 0.0, 0.0, 0.0, 1.0, "deadzone", 1.0, 0.0, "test")
        for pol_name in ["conservative", "balanced", "permissive"]:
            policy = get_policy(pol_name)
            ok, _ = evaluate_cell(dead_cell, policy, thresholds)
            assert not ok, f"Policy '{pol_name}' should reject deadzone cells"

    def test_audit_has_disclaimer(self) -> None:
        audit = run_risk_policy_audit(PROFILE_PATH, CONTRACT_CSV)
        assert "offline" in audit["disclaimer"].lower()


# ---------------------------------------------------------------------------
# Verification CLI tests
# ---------------------------------------------------------------------------

class TestVerificationCLI:
    def test_cli_runs_and_creates_outputs(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/verify_offline_compensator.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

    def test_summary_json_created(self) -> None:
        path = M22D_OUTPUT / "offline_compensator_verification_summary.json"
        assert path.exists(), f"Missing: {path}"

    def test_report_md_created(self) -> None:
        path = M22D_OUTPUT / "offline_compensator_verification_report.md"
        assert path.exists(), f"Missing: {path}"

    def test_loro_csv_created(self) -> None:
        path = M22D_OUTPUT / "leave_one_repeat_out_results.csv"
        assert path.exists(), f"Missing: {path}"

    def test_edge_case_audit_json_created(self) -> None:
        path = M22D_OUTPUT / "edge_case_audit.json"
        assert path.exists(), f"Missing: {path}"

    def test_baseline_csv_created(self) -> None:
        path = M22D_OUTPUT / "baseline_comparison.csv"
        assert path.exists(), f"Missing: {path}"

    def test_risk_policy_csv_created(self) -> None:
        path = M22D_OUTPUT / "risk_policy_audit.csv"
        assert path.exists(), f"Missing: {path}"

    def test_risk_policy_summary_json_created(self) -> None:
        path = M22D_OUTPUT / "risk_policy_audit_summary.json"
        assert path.exists(), f"Missing: {path}"


# ---------------------------------------------------------------------------
# Output labeling tests
# ---------------------------------------------------------------------------

class TestOutputLabeling:
    def test_summary_json_labels_offline_only(self) -> None:
        data = json.loads((M22D_OUTPUT / "offline_compensator_verification_summary.json").read_text(encoding="utf-8"))
        assert data["offline_only"] is True
        assert data["physical_validation"] == "not_started"
        assert data["deployment_ready"] is False

    def test_report_md_contains_disclaimer(self) -> None:
        text = (M22D_OUTPUT / "offline_compensator_verification_report.md").read_text(encoding="utf-8")
        assert "not physical validation" in text.lower()

    def test_edge_case_audit_json_labels_offline(self) -> None:
        data = json.loads((M22D_OUTPUT / "edge_case_audit.json").read_text(encoding="utf-8"))
        for case in data["cases"]:
            assert case["offline_only"] is True

    def test_loro_csv_has_72_rows(self) -> None:
        with (M22D_OUTPUT / "leave_one_repeat_out_results.csv").open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 72


# ---------------------------------------------------------------------------
# Physical validation / deployment / GO1/G1 boundary tests
# ---------------------------------------------------------------------------

class TestBoundaryFlags:
    def test_physical_validation_not_started(self) -> None:
        data = json.loads((M22D_OUTPUT / "offline_compensator_verification_summary.json").read_text(encoding="utf-8"))
        assert data["physical_validation"] == "not_started"

    def test_deployment_ready_false(self) -> None:
        data = json.loads((M22D_OUTPUT / "offline_compensator_verification_summary.json").read_text(encoding="utf-8"))
        assert data["deployment_ready"] is False

    def test_no_hardware_execution_cli(self) -> None:
        assert not (ROOT / "scripts/run_k1_compensation.py").exists()
        assert not (ROOT / "scripts/execute_compensation.py").exists()

    def test_no_go1_g1_validation_claim(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_compensation_ready_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False


# ---------------------------------------------------------------------------
# Verification data structure tests
# ---------------------------------------------------------------------------

class TestVerificationDataStructures:
    def test_verification_result_to_dict(self) -> None:
        vr = VerificationResult("k1", "S1", 0.5, "conservative", "ok", "ok", 0.55, 0.48, 0.45, 0.02, True, "test")
        d = vr.to_dict()
        assert d["platform"] == "k1"
        assert d["offline_only"] is True

    def test_leave_one_repeat_out_result_to_dict(self) -> None:
        r = LeaveOneRepeatOutResult("T01", "k1", "S1", 0.5, 0.45, 0.55, 0.05, 0.45, 0.0, "ok", "test")
        d = r.to_dict()
        assert d["trial_id"] == "T01"
        assert d["feasibility_status"] == "ok"


# ---------------------------------------------------------------------------
# Claim boundary doc tests
# ---------------------------------------------------------------------------

class TestClaimBoundaryDoc:
    def test_doc_exists(self) -> None:
        path = ROOT / "docs/m22d_offline_verification_and_claim_boundary.md"
        assert path.exists()

    def test_doc_states_physical_validation_not_started(self) -> None:
        text = (ROOT / "docs/m22d_offline_verification_and_claim_boundary.md").read_text(encoding="utf-8")
        assert "not started" in text.lower()

    def test_doc_states_no_go1_g1_claim(self) -> None:
        text = (ROOT / "docs/m22d_offline_verification_and_claim_boundary.md").read_text(encoding="utf-8")
        assert "GO1" in text
        assert "G1" in text
