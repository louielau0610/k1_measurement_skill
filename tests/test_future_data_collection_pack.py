"""Tests for M21 future data collection pack validation."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_future_data_collection_pack import check_disallowed, check_flags, load_json, JSON_TEMPLATES

def test_all_templates_load():
    for tpl in JSON_TEMPLATES:
        data = load_json(tpl)
        assert len(data) > 0

def test_no_remote_controller_state():
    for tpl in JSON_TEMPLATES:
        data = load_json(tpl)
        assert len(check_disallowed(data)) == 0

def test_unsafe_flags_rejected():
    bad = {"safe_command_adapter_ready": True}
    assert len(check_flags(bad)) > 0

def test_pack_validator_runs():
    from validate_future_data_collection_pack import main
    assert main() == 0

def test_disallowed_field_detected():
    bad = {"trial_records": [{"remote_controller_state": "test"}]}
    assert len(check_disallowed(bad)) > 0

def test_navigation_unsafe_flags_false():
    data = load_json(JSON_TEMPLATES[0])
    assert len(check_flags(data)) == 0
