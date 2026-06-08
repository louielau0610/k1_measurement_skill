"""Generate M7 field-test template artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from k1_measurement.field_test_pack import write_ground_truth_trial_sheet


def main() -> int:
    path = write_ground_truth_trial_sheet("templates/ground_truth_trial_sheet.csv")
    print(f"Wrote ground-truth trial sheet template: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
