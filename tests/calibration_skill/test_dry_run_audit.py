from calibration_skill.adapters.mock import DeterministicMonotonicClock
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from calibration_skill.skill.operations import OP_DRY_RUN_END_TO_END

from test_m26c_helpers import command_payload, request


def test_audit_contains_required_dry_run_fields_and_digest():
    service = build_mock_dry_run_service(clock=DeterministicMonotonicClock())
    response = service.handle_request(request(OP_DRY_RUN_END_TO_END, payload=command_payload(OP_DRY_RUN_END_TO_END)))
    audit = response["result"]["audit_record"]
    assert audit["session_id"] == "audit-req-1"
    assert audit["requested_operation"] == OP_DRY_RUN_END_TO_END
    assert audit["platform"] == "mock"
    assert audit["safety_policy_id"] == "mock-policy"
    assert audit["authorization_id"] == "auth-1"
    assert audit["receipt"]["disposition"] == "accepted"
    assert audit["telemetry_evidence"]["source_adapter"] == "MockRobotAdapter"
    assert audit["hardware_evidence_claimed"] is False
    assert len(audit["audit_digest"]) == 64
    assert service.audit_records == [audit]
