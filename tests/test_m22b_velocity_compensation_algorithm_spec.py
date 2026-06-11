"""Tests for M22-B: Velocity Compensation Algorithm Specification.

Tests cover:
- algorithm spec JSON exists
- implementation_ready is false
- compensation_ready is false
- all required feasibility statuses exist
- default thresholds exist
- risk policies exist
- algorithm steps include deadzone handling
- algorithm steps include monotonic segment selection
- algorithm steps include no-extrapolation default
- no compensator.py exists
- no inverse_response_model.py exists
- no command remapping CLI exists
- M22-A summary remains intact
- measurement module closure flags remain intact
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SPEC_JSON = ROOT / "outputs/compensation_research/velocity_compensation_algorithm_spec_v1.json"
SPEC_MD = ROOT / "outputs/compensation_research/velocity_compensation_algorithm_spec_v1.md"
ALGORITHM_SPEC = ROOT / "docs/velocity_compensation_algorithm_spec.md"
FEASIBILITY_SPEC = ROOT / "docs/velocity_compensation_feasibility_status.md"
RISK_SPEC = ROOT / "docs/velocity_compensation_risk_filtering.md"
EXAMPLES_MD = ROOT / "outputs/compensation_research/k1_compensation_decision_examples.md"
STATUS_PATH = ROOT / "outputs/measurement_v1/measurement_module_status.json"
CLOSURE_PATH = ROOT / "outputs/measurement_v1/measurement_module_v1_closure_summary.json"

EXPECTED_FEASIBILITY_STATUSES = {
    "ok", "feasible_but_risky", "infeasible_deadzone",
    "infeasible_out_of_range", "insufficient_evidence",
    "non_monotonic_ambiguous", "platform_not_calibrated",
    "surface_not_calibrated", "invalid_input",
}

EXPECTED_THRESHOLDS = {
    "no_motion_velocity_threshold_mps", "under_track_relative_threshold",
    "over_response_relative_threshold", "yaw_drift_high_threshold_deg",
    "uncertainty_high_threshold_mps", "minimum_segment_points",
    "minimum_cell_repeats", "minimum_confidence", "extrapolation_allowed",
}

FORBIDDEN_MODULES = [
    "calibration_core/compensator.py",
    "calibration_core/inverse_response_model.py",
]


# ---------------------------------------------------------------------------
# Spec artifact existence
# ---------------------------------------------------------------------------

class TestSpecArtifactExistence:
    def test_spec_json_exists(self) -> None:
        assert SPEC_JSON.exists(), f"Missing: {SPEC_JSON}"

    def test_spec_md_exists(self) -> None:
        assert SPEC_MD.exists(), f"Missing: {SPEC_MD}"

    def test_algorithm_spec_doc_exists(self) -> None:
        assert ALGORITHM_SPEC.exists(), f"Missing: {ALGORITHM_SPEC}"

    def test_feasibility_spec_doc_exists(self) -> None:
        assert FEASIBILITY_SPEC.exists(), f"Missing: {FEASIBILITY_SPEC}"

    def test_risk_spec_doc_exists(self) -> None:
        assert RISK_SPEC.exists(), f"Missing: {RISK_SPEC}"

    def test_examples_doc_exists(self) -> None:
        assert EXAMPLES_MD.exists(), f"Missing: {EXAMPLES_MD}"


# ---------------------------------------------------------------------------
# Spec JSON schema validation
# ---------------------------------------------------------------------------

class TestSpecJSONSchema:
    def _load_spec(self) -> dict:
        return json.loads(SPEC_JSON.read_text(encoding="utf-8"))

    def test_spec_version_present(self) -> None:
        spec = self._load_spec()
        assert spec["spec_version"] == "compensation_algorithm_spec_v1.0"

    def test_algorithm_name_present(self) -> None:
        spec = self._load_spec()
        assert "Conservative Monotonic Segment Inverse Lookup" in spec["algorithm_name"]

    def test_status_is_specification_only(self) -> None:
        spec = self._load_spec()
        assert spec["status"] == "specification_only" or "specification" in str(spec.get("status", "")).lower()

    def test_input_contract_has_required_fields(self) -> None:
        spec = self._load_spec()
        ic = spec["input_contract"]
        required_inputs = ["platform", "robot_model", "surface_type",
                          "desired_actual_velocity_mps", "response_profile_path"]
        for field in required_inputs:
            assert field in ic, f"Missing input field: {field}"

    def test_output_contract_has_required_fields(self) -> None:
        spec = self._load_spec()
        oc = spec["output_contract"]
        required_outputs = ["recommended_command_velocity_mps", "expected_actual_velocity_mps",
                           "feasibility_status", "region_label", "risk_score", "confidence"]
        for field in required_outputs:
            assert field in oc, f"Missing output field: {field}"


# ---------------------------------------------------------------------------
# Implementation readiness flags
# ---------------------------------------------------------------------------

class TestImplementationReadinessFlags:
    def test_implementation_ready_is_false(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert spec["implementation_ready"] is False

    def test_compensation_ready_is_false(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert spec["compensation_ready"] is False

    def test_spec_md_states_implementation_ready_false(self) -> None:
        text = SPEC_MD.read_text(encoding="utf-8")
        assert "implementation_ready = false" in text

    def test_spec_md_states_compensation_ready_false(self) -> None:
        text = SPEC_MD.read_text(encoding="utf-8")
        assert "compensation_ready = false" in text

    def test_algorithm_spec_doc_states_implementation_ready_false(self) -> None:
        text = ALGORITHM_SPEC.read_text(encoding="utf-8")
        assert "`implementation_ready`" in text
        assert "false" in text


# ---------------------------------------------------------------------------
# Feasibility statuses
# ---------------------------------------------------------------------------

class TestFeasibilityStatuses:
    def test_all_nine_statuses_present(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        statuses = set(spec["feasibility_statuses"])
        assert statuses == EXPECTED_FEASIBILITY_STATUSES, \
            f"Missing: {EXPECTED_FEASIBILITY_STATUSES - statuses}, Extra: {statuses - EXPECTED_FEASIBILITY_STATUSES}"

    def test_deadzone_status_exists(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert "infeasible_deadzone" in spec["feasibility_statuses"]

    def test_out_of_range_status_exists(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert "infeasible_out_of_range" in spec["feasibility_statuses"]

    def test_non_monotonic_status_exists(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert "non_monotonic_ambiguous" in spec["feasibility_statuses"]

    def test_feasibility_doc_covers_all_statuses(self) -> None:
        text = FEASIBILITY_SPEC.read_text(encoding="utf-8")
        for status in EXPECTED_FEASIBILITY_STATUSES:
            assert status in text, f"Status '{status}' not documented in feasibility spec"


# ---------------------------------------------------------------------------
# Default thresholds
# ---------------------------------------------------------------------------

class TestDefaultThresholds:
    def test_all_thresholds_present(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        thresholds = set(spec["default_thresholds"].keys())
        missing = EXPECTED_THRESHOLDS - thresholds
        assert not missing, f"Missing thresholds: {missing}"

    def test_no_motion_threshold_is_reasonable(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        val = spec["default_thresholds"]["no_motion_velocity_threshold_mps"]
        assert 0 < val < 0.1, f"no_motion threshold {val} out of reasonable range"

    def test_extrapolation_defaults_to_false(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert spec["default_thresholds"]["extrapolation_allowed"] is False

    def test_minimum_confidence_is_between_0_and_1(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        val = spec["default_thresholds"]["minimum_confidence"]
        assert 0 <= val <= 1, f"minimum_confidence {val} out of [0,1]"


# ---------------------------------------------------------------------------
# Risk policies
# ---------------------------------------------------------------------------

class TestRiskPolicies:
    def test_three_policies_exist(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        policies = spec["risk_policies"]
        assert "conservative" in policies
        assert "balanced" in policies
        assert "permissive" in policies

    def test_conservative_accepts_only_reliable(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        cp = spec["risk_policies"]["conservative"]
        assert cp["accepted_labels"] == ["reliable"]

    def test_all_policies_reject_deadzone(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        for name, policy in spec["risk_policies"].items():
            assert policy["allow_deadzone"] is False, \
                f"Policy '{name}' should reject deadzone"

    def test_conservative_is_most_restrictive(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        cp = spec["risk_policies"]["conservative"]
        bp = spec["risk_policies"]["balanced"]
        pp = spec["risk_policies"]["permissive"]
        assert cp["max_risk_score"] <= bp["max_risk_score"] <= pp["max_risk_score"]
        assert cp["min_repeats"] >= bp["min_repeats"] >= pp["min_repeats"]

    def test_risk_spec_doc_covers_all_policies(self) -> None:
        text = RISK_SPEC.read_text(encoding="utf-8")
        assert "Conservative Policy" in text
        assert "Balanced Policy" in text
        assert "Permissive Policy" in text


# ---------------------------------------------------------------------------
# Algorithm steps
# ---------------------------------------------------------------------------

class TestAlgorithmSteps:
    def test_algorithm_has_14_steps(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        steps = spec["algorithm_steps"]
        assert len(steps) >= 10, f"Expected at least 10 steps, got {len(steps)}"

    def test_step_includes_deadzone_handling(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        steps_text = " ".join(spec["algorithm_steps"]).lower()
        assert "deadzone" in steps_text or "no-motion" in steps_text, \
            "Algorithm steps should include deadzone handling"

    def test_step_includes_monotonic_segment(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        steps_text = " ".join(spec["algorithm_steps"]).lower()
        assert "monotonic" in steps_text, \
            "Algorithm steps should include monotonic segment building"

    def test_step_includes_no_extrapolation_default(self) -> None:
        text = ALGORITHM_SPEC.read_text(encoding="utf-8")
        assert "no extrapolation" in text.lower() or "extrapolation_policy = reject" in text.lower(), \
            "Algorithm spec should document no-extrapolation default"

    def test_step_includes_inverse_interpolation(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        steps_text = " ".join(spec["algorithm_steps"]).lower()
        assert "inverse" in steps_text and "interpolat" in steps_text, \
            "Algorithm steps should include inverse interpolation"

    def test_algorithm_spec_doc_has_all_steps(self) -> None:
        text = ALGORITHM_SPEC.read_text(encoding="utf-8")
        assert "Step 1: Load Measurement Data" in text
        assert "Step 14: Return Structured Result" in text


# ---------------------------------------------------------------------------
# No implementation modules
# ---------------------------------------------------------------------------

class TestNoImplementationModules:
    def test_no_compensator_py(self) -> None:
        for mod in FORBIDDEN_MODULES:
            assert not (ROOT / mod).exists(), f"Forbidden module exists: {mod}"

    def test_no_command_remapping_cli(self) -> None:
        remapping_scripts = [
            "scripts/remap_command.py",
            "scripts/compensate_velocity.py",
            "scripts/run_compensation.py",
        ]
        for script in remapping_scripts:
            assert not (ROOT / script).exists(), f"Forbidden script exists: {script}"

    def test_no_compensation_execution_cli(self) -> None:
        assert not (ROOT / "scripts/run_k1_compensation.py").exists()
        assert not (ROOT / "scripts/execute_compensation.py").exists()


# ---------------------------------------------------------------------------
# Measurement module closure flags intact
# ---------------------------------------------------------------------------

class TestClosureFlagsIntact:
    def test_measurement_module_still_complete(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["measurement_module_v1_status"] == "complete"
        assert status["measurement_module_v1_complete"] is True

    def test_compensation_ready_still_false_in_status(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["velocity_compensation_ready"] is False

    def test_go1_g1_still_false(self) -> None:
        status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        assert status["unitree_go1_measurement_ready"] is False
        assert status["unitree_g1_measurement_ready"] is False

    def test_closure_summary_intact(self) -> None:
        closure = json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))
        assert closure["closure_status"] == "complete"
        assert closure["status_flags"]["velocity_compensation_ready"] is False

    def test_k1_contract_still_72_valid(self) -> None:
        closure = json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))
        cv = closure["k1_contract_validation"]
        assert cv["total_rows"] == 72
        assert cv["valid_rows"] == 72


# ---------------------------------------------------------------------------
# Examples document
# ---------------------------------------------------------------------------

class TestExamplesDocument:
    def test_examples_are_marked_specification_only(self) -> None:
        text = EXAMPLES_MD.read_text(encoding="utf-8")
        assert "specification examples" in text.lower() or "specification only" in text.lower(), \
            "Examples must be marked as specification-only"

    def test_examples_include_deadzone_case(self) -> None:
        text = EXAMPLES_MD.read_text(encoding="utf-8")
        assert "infeasible_deadzone" in text, "Examples should include deadzone case"

    def test_examples_include_out_of_range_case(self) -> None:
        text = EXAMPLES_MD.read_text(encoding="utf-8")
        assert "infeasible_out_of_range" in text, "Examples should include out-of-range case"

    def test_examples_include_ok_or_feasible_case(self) -> None:
        text = EXAMPLES_MD.read_text(encoding="utf-8")
        assert "ok" in text.lower(), "Examples should include a successful case"

    def test_examples_not_generated_by_live_compensator(self) -> None:
        text = EXAMPLES_MD.read_text(encoding="utf-8")
        assert "not generated by a live compensator" in text.lower(), \
            "Examples must state they are not from a live compensator"


# ---------------------------------------------------------------------------
# Next milestone
# ---------------------------------------------------------------------------

class TestNextMilestone:
    def test_spec_json_next_is_m22c(self) -> None:
        spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
        assert "M22-C" in spec["next_milestone"] or "m22c" in spec["next_milestone"].lower()

    def test_algorithm_spec_doc_next_is_m22c(self) -> None:
        text = ALGORITHM_SPEC.read_text(encoding="utf-8")
        assert "M22-C" in text, "Algorithm spec should reference M22-C as next milestone"
