from calibration_skill.adapters.mock import DeterministicMonotonicClock, MockFailureConfig
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from calibration_skill.skill.operations import OP_DRY_RUN_END_TO_END

from test_m26c_helpers import command_payload, request


def _response(failures=None, request_id="req-1"):
    service = build_mock_dry_run_service(
        clock=DeterministicMonotonicClock(),
        failure_config=failures or MockFailureConfig(),
    )
    return service.handle_request(request(OP_DRY_RUN_END_TO_END, request_id=request_id, payload=command_payload(OP_DRY_RUN_END_TO_END))), service


def test_full_success_path_generates_audit_and_telemetry():
    response, service = _response()
    assert response["status"] == "success"
    assert response["result"]["receipt"]["disposition"] == "accepted"
    assert response["result"]["telemetry_sample"]["quality_flags"] == ["mock", "dry_run"]
    assert response["result"]["audit_record"]["hardware_evidence_claimed"] is False
    assert service.audit_records


def test_preflight_failure_still_restores_safe_state_and_audits():
    response, _ = _response(MockFailureConfig(preflight_blocker=True))
    assert response["status"] == "rejected"
    audit = response["result"]["audit_record"]
    assert audit["cleanup_result"] == "stop_attempted_then_restore"
    assert audit["session_status"] == "rejected"


def test_command_failure_still_attempts_stop_restore_and_audits():
    response, _ = _response(MockFailureConfig(command_rejection=True))
    assert response["status"] == "rejected"
    assert response["result"]["stop_receipt"]["command_sequence_id"].startswith("mock-stop")
    assert response["result"]["audit_record"]["cleanup_result"] == "stop_attempted_then_restore"


def test_deterministic_repeated_runs_with_same_inputs():
    first, _ = _response(request_id="req-repeat")
    second, _ = _response(request_id="req-repeat")
    assert first == second
