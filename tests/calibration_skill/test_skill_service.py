from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from calibration_skill.adapters.mock import DeterministicMonotonicClock, MockFailureConfig
from calibration_skill.runtime.dry_run import build_mock_dry_run_service
from calibration_skill.schemas.validation import get_schema_document, validate_skill_response
from calibration_skill.skill.operations import (
    OP_DRY_RUN_VELOCITY_COMMAND,
    OP_PREFLIGHT,
)

from test_m26c_helpers import authorization, command_payload, request, safety_envelope, velocity_command
from calibration_skill.schemas.codec import encode_operator_authorization, encode_safety_envelope, encode_velocity_command


def _service(failures=None):
    return build_mock_dry_run_service(
        clock=DeterministicMonotonicClock(),
        failure_config=failures or MockFailureConfig(),
    )


def test_valid_preflight():
    response = _service().handle_request(request(OP_PREFLIGHT))
    assert response["status"] == "success"
    assert response["result"]["preflight_report"]["is_ready"] is True


def test_unknown_operation_schema_version_missing_id_dry_run_and_real_platform_rejected():
    svc = _service()
    assert svc.handle_request(request("nope"))["error"]["code"] == "configuration_invalid"
    bad_version = request(OP_PREFLIGHT)
    bad_version["schema_version"] = "2.0.0"
    assert svc.handle_request(bad_version)["error"]["code"] == "configuration_invalid"
    missing_id = request(OP_PREFLIGHT, request_id="")
    assert svc.handle_request(missing_id)["error"]["code"] == "configuration_invalid"
    assert svc.handle_request(request(OP_PREFLIGHT, dry_run=False))["error"]["code"] == "unsupported_platform"
    assert svc.handle_request(request(OP_PREFLIGHT, platform="booster_k1"))["error"]["code"] == "unsupported_platform"


def test_missing_safety_expired_authorization_and_expired_command_rejected():
    svc = _service()
    missing = svc.handle_request(request(OP_DRY_RUN_VELOCITY_COMMAND, payload={}))
    assert missing["error"]["code"] == "configuration_invalid"
    expired_auth_payload = {
        "safety_envelope": encode_safety_envelope(safety_envelope()),
        "velocity_command": encode_velocity_command(velocity_command()),
        "operator_authorization": encode_operator_authorization(authorization(expiry_ns=900_000_000)),
    }
    assert svc.handle_request(request(OP_DRY_RUN_VELOCITY_COMMAND, payload=expired_auth_payload))["error"]["code"] == "configuration_invalid"
    expired_cmd_payload = {
        "safety_envelope": encode_safety_envelope(safety_envelope()),
        "velocity_command": encode_velocity_command(velocity_command(expiry_ns=1_000_000_001)),
        "operator_authorization": encode_operator_authorization(authorization()),
    }
    response = svc.handle_request(request(OP_DRY_RUN_VELOCITY_COMMAND, payload=expired_cmd_payload))
    assert response["status"] == "rejected"
    assert response["error"]["code"] == "command_expired"


def test_valid_dry_run_velocity_command_and_failure_response_schema_compatibility():
    svc = _service()
    response = svc.handle_request(request(OP_DRY_RUN_VELOCITY_COMMAND, payload=command_payload()))
    assert response["status"] == "success"
    assert response["audit_reference"] == "audit-req-1"
    assert validate_skill_response(response)["valid"]
    failing = _service(MockFailureConfig(command_rejection=True))
    failure = failing.handle_request(request(OP_DRY_RUN_VELOCITY_COMMAND, payload=command_payload()))
    assert failure["status"] == "rejected"
    assert failure["error"]["code"] == "precondition_failed"
    assert validate_skill_response(failure)["valid"]


def test_response_schema_accepts_service_response_with_jsonschema():
    response = _service().handle_request(request(OP_PREFLIGHT))
    schema = get_schema_document("skill_response")
    error_schema = get_schema_document("error")
    registry = Registry().with_resource("urn:calibration-skill:schema:error:v1", Resource.from_contents(error_schema))
    Draft202012Validator(schema, registry=registry).validate(response)
