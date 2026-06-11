"""Plan or run three guarded M19C SDK state smoke trials."""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

from log_k1_sdk_state_smoke import FIELDS, make_sample_row, try_import_sdk, init_channel

OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
DATA_DIR = Path("data/m19_sdk_state_smoke/trials")
TRIALS = [
    ("M19C_SMOKE_S1_lab_hard_floor_U020_R1", 0.20),
    ("M19C_SMOKE_S1_lab_hard_floor_U040_R1", 0.40),
    ("M19C_SMOKE_S1_lab_hard_floor_U060_R1", 0.60),
]


def run_trials(execute: bool, interface: str, sample_hz: float, output_dir: Path, data_dir: Path) -> dict:
    module, module_name, import_error = try_import_sdk()
    init_result = ""
    if execute and module is not None:
        init_result = init_channel(module, interface)
    trials = []
    data_dir.mkdir(parents=True, exist_ok=True)
    for trial_id, vx in TRIALS:
        path = data_dir / f"{trial_id}.csv"
        rows = []
        if execute and module is not None:
            period = 1.0 / sample_hz if sample_hz > 0 else 0.2
            t0 = time.time()
            while time.time() - t0 <= 10.0:
                row = make_sample_row(t0, module, import_error)
                row["trial_id"] = trial_id
                rows.append(row)
                time.sleep(period)
        executed = execute and module is not None
        if executed:
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["trial_id"] + FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
        trials.append(
            {
                "trial_id": trial_id,
                "vx": vx,
                "planned_output_csv": str(path),
                "output_csv": str(path) if executed else "",
                "samples": len(rows),
                "executed": executed,
            }
        )
    summary = {
        "timestamp": datetime.now().isoformat(),
        "execute_requested": execute,
        "sdk_module_imported": module_name,
        "sdk_available": module is not None,
        "channel_init_result": init_result,
        "trials": trials,
        "dynamic_smoke_trials_run": any(item["executed"] for item in trials),
        "full_72_trial_protocol_run": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "m19c_sdk_state_smoke_trials_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "m19c_sdk_state_smoke_trials_report.md").write_text(
        "# M19C SDK State Smoke Trials\n\n"
        f"Execute requested: {execute}\n\n"
        f"Dynamic smoke trials run: {summary['dynamic_smoke_trials_run']}\n\n"
        "Only three smoke trials are supported here; the full 72-trial measurement protocol is not run.\n",
        encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Actually run guarded SDK smoke trial logging.")
    parser.add_argument("--interface", default="lo")
    parser.add_argument("--sample-hz", type=float, default=5.0)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args(argv)
    summary = run_trials(args.execute, args.interface, args.sample_hz, args.output_dir, args.data_dir)
    print(f"Dynamic smoke trials run: {summary['dynamic_smoke_trials_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
