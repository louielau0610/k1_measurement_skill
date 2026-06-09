"""Validate M21 future data collection pack templates."""
from __future__ import annotations
import json
import sys
from pathlib import Path

REQUIRED_DOCS = [
    "paper/experiments/m21_future_data_collection_pack_v1.md",
    "paper/experiments/m21_pre_session_checklist_v1.md",
    "paper/experiments/m21_trial_sheet_template_v1.md",
    "paper/experiments/m21_navigation_task_sheet_template_v1.md",
    "paper/experiments/m21_logging_manifest_template_v1.md",
    "paper/experiments/m21_post_session_validation_checklist_v1.md",
]

JSON_TEMPLATES = [
    "examples/future_experiments/m21_future_session_template.json",
    "examples/future_experiments/m21_future_trial_template.json",
]

DISALLOWED_FIELDS = {"remote_controller_state", "hand_controller_state", "unconfirmed_ros2_topic"}
UNSAFE_FLAGS = {
    "navigation_safety_improvement_claim_ready": True,
    "publication_ready": True,
    "safe_command_adapter_ready": True,
    "navigation_control_ready": True,
    "compensation_ready": True,
    "fabricated_results": True,
    "real_robot_experiments_run": True,
}

def load_json(path): 
    with open(path, "r", encoding="utf-8-sig") as f: return json.load(f)

def check_disallowed(data, path="", errors=None):
    if errors is None: errors = []
    if isinstance(data, dict):
        for k, v in data.items():
            cp = f"{path}.{k}" if path else k
            if k in DISALLOWED_FIELDS: errors.append(f"DISALLOWED: {cp}")
            check_disallowed(v, cp, errors)
    elif isinstance(data, list):
        for i, item in enumerate(data): check_disallowed(item, f"{path}[{i}]", errors)
    return errors

def check_flags(data, errors=None):
    if errors is None: errors = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k in UNSAFE_FLAGS and v == UNSAFE_FLAGS[k]:
                errors.append(f"UNSAFE FLAG: {k} is {v}")
        for v in data.values(): check_flags(v, errors)
    elif isinstance(data, list):
        for item in data: check_flags(item, errors)
    return errors

def main():
    errors = []
    for doc in REQUIRED_DOCS:
        if not Path(doc).exists():
            errors.append(f"Missing doc: {doc}")
    for tpl in JSON_TEMPLATES:
        if not Path(tpl).exists():
            errors.append(f"Missing template: {tpl}")
        else:
            data = load_json(tpl)
            errors.extend(check_disallowed(data))
            errors.extend(check_flags(data))
    if errors:
        for e in errors: print(f"  - {e}")
        return 1
    print(f"OK: All {len(REQUIRED_DOCS)} docs and {len(JSON_TEMPLATES)} JSON templates valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
