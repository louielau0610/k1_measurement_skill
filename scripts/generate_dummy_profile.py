"""Generate a dummy measurement profile without robot access."""

from __future__ import annotations

import json

from k1_measurement.metrics import summarize_velocity_samples
from k1_measurement.profile_builder import build_measurement_profile


def main() -> int:
    speed_points = [
        summarize_velocity_samples(0.1, [0.09, 0.10, 0.10]),
        summarize_velocity_samples(0.2, [0.18, 0.19, 0.20]),
    ]
    profile = build_measurement_profile(
        environment={"floor_type": "tile", "condition": "dry", "slope": "flat"},
        speed_points=speed_points,
        confidence="dummy",
    )
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
