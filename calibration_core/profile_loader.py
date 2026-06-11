"""Load calibration profiles for skill-facing use."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

K1_GOLD_PROFILE = Path("outputs/real_k1_validation_m19/k1_gold_profile_v1.json")


def load_profile(path: Path = K1_GOLD_PROFILE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_k1_gold_profile(path: Path = K1_GOLD_PROFILE) -> dict[str, Any]:
    profile = load_profile(path)
    return {
        "robot_id": profile["robot_id"],
        "tested_surfaces": profile["surfaces"],
        "speed_list": profile["speeds"],
        "region_labels": profile["region_labels"],
        "recommended_reliable_ranges": profile["recommended_reliable_ranges"],
        "deadzone_ranges": profile["deadzone_ranges"],
        "drift_prone_ranges": profile["drift_prone_ranges"],
        "limitations": profile["limitations"],
    }
