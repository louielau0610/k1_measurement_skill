"""Discover K1 Booster SDK state sources without running M19 analysis."""
from __future__ import annotations

import argparse
import inspect
import json
from datetime import datetime
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("outputs/real_k1_validation_m19")
SDK_MODULE_CANDIDATES = ["booster_robotics_sdk_python", "booster_robotics_sdk"]
CLASS_NAMES = [
    "B1LowStateSubscriber",
    "B1OdometerStateSubscriber",
    "LowState",
    "ImuState",
    "Odometer",
    "Frame",
    "Transform",
    "B1LocoClient",
    "ChannelFactory",
]


def public_methods(obj: Any) -> list[str]:
    return sorted(name for name, member in inspect.getmembers(obj) if not name.startswith("_") and callable(member))


def public_fields(obj: Any) -> list[str]:
    return sorted(name for name in dir(obj) if not name.startswith("_") and not callable(getattr(obj, name, None)))


def try_import_sdk() -> tuple[Any | None, str | None]:
    for module_name in SDK_MODULE_CANDIDATES:
        try:
            module = __import__(module_name)
            return module, module_name
        except Exception:
            continue
    return None, None


def class_info(module: Any | None, name: str) -> dict[str, Any]:
    if module is None or not hasattr(module, name):
        return {"available": False}
    cls = getattr(module, name)
    constructable = False
    construct_error = ""
    instance_fields: list[str] = []
    try:
        instance = cls()
        constructable = True
        instance_fields = public_fields(instance)
    except Exception as exc:
        construct_error = repr(exc)
    return {
        "available": True,
        "doc": inspect.getdoc(cls) or "",
        "public_methods": public_methods(cls),
        "class_fields": public_fields(cls),
        "constructable": constructable,
        "construct_error": construct_error,
        "instance_fields": instance_fields,
    }


def discover(output_dir: Path = OUTPUT_DIR, try_transforms: bool = False) -> dict[str, Any]:
    module, module_name = try_import_sdk()
    classes = {name: class_info(module, name) for name in CLASS_NAMES}
    transform_results: list[dict[str, Any]] = []
    if try_transforms and module is not None and classes["B1LocoClient"]["available"] and classes["Frame"]["available"] and classes["Transform"]["available"]:
        try:
            client = getattr(module, "B1LocoClient")()
            if hasattr(client, "Init"):
                client.Init()
            frame_cls = getattr(module, "Frame")
            transform_cls = getattr(module, "Transform")
            frames = [getattr(frame_cls, name) for name in public_fields(frame_cls)[:4]]
            for src in frames:
                for dst in frames:
                    transform = transform_cls()
                    try:
                        result = client.GetFrameTransform(src, dst, transform)
                        transform_results.append({"src": str(src), "dst": str(dst), "return_code": result, "success": result == 0})
                    except Exception as exc:
                        transform_results.append({"src": str(src), "dst": str(dst), "error": repr(exc), "success": False})
        except Exception as exc:
            transform_results.append({"error": repr(exc), "success": False})
    summary = {
        "timestamp": datetime.now().isoformat(),
        "sdk_module_imported": module_name,
        "sdk_available": module is not None,
        "classes": classes,
        "frame_members": classes.get("Frame", {}).get("class_fields", []),
        "transform_fields": classes.get("Transform", {}).get("instance_fields", []) or classes.get("Transform", {}).get("class_fields", []),
        "get_frame_transform_checked": try_transforms,
        "get_frame_transform_results": transform_results,
        "usable_state_source_detected": bool(
            classes.get("B1OdometerStateSubscriber", {}).get("available")
            or classes.get("B1LowStateSubscriber", {}).get("available")
            or any(item.get("success") for item in transform_results)
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sdk_state_discovery_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    (output_dir / "sdk_state_discovery_report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# K1 SDK State Source Discovery",
        "",
        f"SDK module imported: `{summary['sdk_module_imported']}`",
        f"SDK available: {summary['sdk_available']}",
        f"Usable state source detected: {summary['usable_state_source_detected']}",
        "",
        "## Classes",
    ]
    for name, info in summary["classes"].items():
        lines.append(f"- `{name}`: available={info.get('available')}, constructable={info.get('constructable', False)}")
        methods = info.get("public_methods") or []
        if methods:
            lines.append(f"  - methods: {', '.join(methods[:20])}")
    lines.extend(
        [
            "",
            f"Frame members: {', '.join(summary['frame_members']) if summary['frame_members'] else 'none detected'}",
            f"Transform fields: {', '.join(summary['transform_fields']) if summary['transform_fields'] else 'none detected'}",
            "",
            "This discovery step does not run empirical M19 analysis.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--try-transforms", action="store_true", help="Call B1LocoClient.GetFrameTransform if SDK import succeeds.")
    args = parser.parse_args(argv)
    summary = discover(args.output_dir, args.try_transforms)
    print(f"SDK available: {summary['sdk_available']}")
    print(f"Usable state source detected: {summary['usable_state_source_detected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
