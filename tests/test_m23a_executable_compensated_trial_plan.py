"""Regression tests for the M23-A executable compensated trial plan hotfix."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_m23a_k1_compensation_experiment_plan as generator

EXPERIMENT_DIR = ROOT / "outputs/compensation_experiments"
FULL_PLAN = EXPERIMENT_DIR / "m23a_trial_plan.csv"
EXECUTABLE_PLAN = EXPERIMENT_DIR / "m23a_executable_trial_plan.csv"
EXECUTABLE_SUMMARY_JSON = EXPERIMENT_DIR / "m23a_executable_trial_plan_summary.json"
EXECUTABLE_SUMMARY_MD = EXPERIMENT_DIR / "m23a_executable_trial_plan_summary.md"
PLAN_JSON = EXPERIMENT_DIR / "m23a_experiment_plan.json"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_compensated_executable_rows_have_command_velocity() -> None:
    rows = _read_csv(FULL_PLAN)
    executable_compensated = [
        row
        for row in rows
        if row["condition"] == "compensated"
        and row["compensator_status"] in {"ok", "feasible_but_risky"}
    ]
    assert executable_compensated
    assert all(row["command_velocity_mps"].strip() for row in executable_compensated)


def test_executable_plan_has_complete_direct_compensated_pairs() -> None:
    rows = _read_csv(EXECUTABLE_PLAN)
    by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pair[row["pair_id"]].append(row)

    assert by_pair
    for pair_rows in by_pair.values():
        assert Counter(row["condition"] for row in pair_rows) == {"direct": 1, "compensated": 1}


def test_no_blank_command_in_executable_plan() -> None:
    rows = _read_csv(EXECUTABLE_PLAN)
    assert rows
    assert all(row["command_velocity_mps"].strip() for row in rows)


def test_infeasible_compensated_rows_are_excluded_from_executable_plan() -> None:
    full_rows = _read_csv(FULL_PLAN)
    executable_trial_ids = {row["trial_id"] for row in _read_csv(EXECUTABLE_PLAN)}
    infeasible_rows = [
        row
        for row in full_rows
        if row["condition"] == "compensated"
        and row["compensator_status"] not in {"ok", "feasible_but_risky"}
    ]
    assert infeasible_rows
    assert all(row["physical_run_status"] == "not_executable" for row in infeasible_rows)
    assert all(row["trial_id"] not in executable_trial_ids for row in infeasible_rows)


def test_generator_records_compensator_status_and_reason() -> None:
    rows = _read_csv(FULL_PLAN)
    compensated = [row for row in rows if row["condition"] == "compensated"]
    assert compensated
    assert all(row["compensator_status"].strip() for row in compensated)
    assert all(row["compensator_reason"].strip() for row in compensated)


def test_executable_plan_summary_reports_pair_count() -> None:
    summary = json.loads(EXECUTABLE_SUMMARY_JSON.read_text(encoding="utf-8"))
    rows = _read_csv(EXECUTABLE_PLAN)
    assert summary["executable_pair_count"] == len({row["pair_id"] for row in rows})
    assert summary["executable_pair_count"] > 0
    assert summary["compensated_command_velocity_complete"] is True
    assert "Executable pairs" in EXECUTABLE_SUMMARY_MD.read_text(encoding="utf-8")


def test_blank_feasible_compensated_command_is_validation_error() -> None:
    rows = [
        {
            "trial_id": "BAD_COMP",
            "pair_id": "PAIR1",
            "condition": "compensated",
            "command_velocity_mps": "",
            "compensator_status": "feasible_but_risky",
        }
    ]
    errors = generator._validate_trial_plan(rows)
    assert any("blank command_velocity_mps" in error for error in errors)


def test_default_balanced_plan_warns_when_no_executable_pairs(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_m23a_k1_compensation_experiment_plan.py",
            "--output-dir",
            str(tmp_path),
            "--no-randomize",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "WARNING: No executable compensated pairs" in result.stderr
    summary = json.loads((tmp_path / "m23a_executable_trial_plan_summary.json").read_text(encoding="utf-8"))
    assert summary["executable_pair_count"] == 0


def test_plan_json_points_to_executable_trial_plan() -> None:
    plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    assert plan["executable_trial_plan_csv"].endswith("m23a_executable_trial_plan.csv")
    assert plan["executable_pairs"] > 0


def test_m23b_runner_defaults_to_executable_trial_plan() -> None:
    from scripts import run_m23b_k1_compensation_trials as runner

    assert runner.TRIAL_PLAN_CSV.as_posix().endswith("m23a_executable_trial_plan.csv")
