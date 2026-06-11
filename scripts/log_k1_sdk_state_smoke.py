"""Log standing K1 SDK state samples for a short smoke test."""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

OUTPUT_CSV = Path("data/m19_sdk_state_smoke/standing_state_samples.csv")
OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
SDK_MODULE_CANDIDATES = ["booster_robotics_sdk_python", "booster_robotics_sdk"]
FIELDS = ["timestamp", "t_rel", "source", "x", "y", "yaw_rad", "yaw_deg", "raw_repr", "error"]


def try_import_sdk() -> tuple[Any | None, str | None, str]:
    for module_name in SDK_MODULE_CANDIDATES:
        try:
            return __import__(module_name), module_name, ""
        except Exception as exc:
            last_error = repr(exc)
    return None, None, last_error if "last_error" in locals() else "no module candidates attempted"


def init_channel(module: Any, interface: str) -> str:
    factory_cls = getattr(module, "ChannelFactory", None)
    if factory_cls is None:
        return "ChannelFactory unavailable"
    factory = factory_cls.Instance()
    result = factory.Init(0, interface)
    return f"ChannelFactory.Init returned {result}"


def sample_transform(module: Any) -> dict[str, Any]:
    client_cls = getattr(module, "B1LocoClient", None)
    frame_cls = getattr(module, "Frame", None)
    transform_cls = getattr(module, "Transform", None)
    if client_cls is None or frame_cls is None or transform_cls is None:
        return {"source": "GetFrameTransform", "error": "required SDK classes unavailable"}
    client = client_cls()
    if hasattr(client, "Init"):
        client.Init()
    frame_values = [getattr(frame_cls, name) for name in dir(frame_cls) if not name.startswith("_") and not callable(getattr(frame_cls, name, None))]
    if len(frame_values) < 2:
        return {"source": "GetFrameTransform", "error": "not enough Frame members"}
    transform = transform_cls()
    result = client.GetFrameTransform(frame_values[0], frame_values[1], transform)
    fields = {name: getattr(transform, name) for name in dir(transform) if not name.startswith("_") and not callable(getattr(transform, name, None))}
    return {"source": "GetFrameTransform", "raw_repr": repr(fields), "return_code": result}


def make_sample_row(t0: float, module: Any | None, source_error: str = "") -> dict[str, Any]:
    now = time.time()
    if module is None:
        return {"timestamp": datetime.now().isoformat(), "t_rel": now - t0, "source": "sdk_unavailable", "error": source_error}
    try:
        sample = sample_transform(module)
        sample.update({"timestamp": datetime.now().isoformat(), "t_rel": now - t0})
        return sample
    except Exception as exc:
        return {"timestamp": datetime.now().isoformat(), "t_rel": now - t0, "source": "sdk_sample_error", "error": repr(exc)}


def log_standing_state(duration_sec: float, sample_hz: float, interface: str, output_csv: Path, output_dir: Path) -> dict[str, Any]:
    module, module_name, import_error = try_import_sdk()
    init_result = ""
    if module is not None:
        try:
            init_result = init_channel(module, interface)
        except Exception as exc:
            init_result = repr(exc)
    rows = []
    period = 1.0 / sample_hz if sample_hz > 0 else 0.2
    t0 = time.time()
    while time.time() - t0 <= duration_sec:
        rows.append(make_sample_row(t0, module, import_error))
        time.sleep(period)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    usable_samples = sum(1 for row in rows if not row.get("error") and row.get("source") != "sdk_unavailable")
    summary = {
        "timestamp": datetime.now().isoformat(),
        "interface": interface,
        "duration_sec": duration_sec,
        "sample_hz": sample_hz,
        "sdk_module_imported": module_name,
        "sdk_available": module is not None,
        "channel_init_result": init_result,
        "samples_written": len(rows),
        "usable_samples": usable_samples,
        "position_available": False,
        "yaw_available": False,
        "output_csv": str(output_csv),
        "full_m19c_measurement_run_ready": usable_samples > 1,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sdk_state_smoke_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report = (
        "# K1 SDK Standing State Smoke Report\n\n"
        f"SDK available: {summary['sdk_available']}\n\n"
        f"Samples written: {summary['samples_written']}\n\n"
        f"Usable samples: {summary['usable_samples']}\n\n"
        f"Full M19C measurement run ready: {summary['full_m19c_measurement_run_ready']}\n\n"
        "This smoke log does not compute empirical M19 statistics.\n"
    )
    (output_dir / "sdk_state_smoke_report.md").write_text(report, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="lo")
    parser.add_argument("--duration-sec", type=float, default=10.0)
    parser.add_argument("--sample-hz", type=float, default=5.0)
    parser.add_argument("--output-csv", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args(argv)
    summary = log_standing_state(args.duration_sec, args.sample_hz, args.interface, args.output_csv, args.output_dir)
    print(f"SDK standing smoke samples_written={summary['samples_written']}")
    print(f"SDK standing smoke ready={summary['full_m19c_measurement_run_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
