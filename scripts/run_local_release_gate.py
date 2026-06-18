#!/usr/bin/env python
"""Run the local packaging and release gate."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PY = ["py", "-3.12"]
FORBIDDEN_IMPORTS = {
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
}


def run(command: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 180) -> dict[str, Any]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": "passed" if result.returncode == 0 else "failed",
    }


def git_status() -> str:
    result = run(["git", "status", "--porcelain=v1"], timeout=30)
    if result["returncode"] != 0:
        raise RuntimeError(result["stderr"] or "git status failed")
    return result["stdout"]


def check_repo_clean(summary_path: Path | None, *, final: bool = False) -> dict[str, Any]:
    status = git_status()
    allowed = ""
    if final and summary_path is not None:
        rel = summary_path.resolve().relative_to(REPO_ROOT).as_posix()
        allowed_lines = {f"?? {rel}", f" M {rel}", f"M  {rel}"}
        lines = [line for line in status.splitlines() if line not in allowed_lines]
        allowed = "\n".join(line for line in status.splitlines() if line in allowed_lines)
        status = "\n".join(lines)
        if status:
            status += "\n"
    return {
        "status": "passed" if not status else "failed",
        "porcelain": status,
        "allowed_summary_porcelain": allowed,
    }


def validate_packaging_metadata() -> dict[str, Any]:
    pyproject = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {})
    scripts = project.get("scripts", {})
    packages = data.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {}).get("include", [])
    package_data = data.get("tool", {}).get("setuptools", {}).get("package-data", {}).get("calibration_skill", [])
    dependencies = project.get("dependencies", [])
    forbidden_deps = [dep for dep in dependencies if any(name in dep.lower() for name in FORBIDDEN_IMPORTS)]
    errors = []
    if project.get("name") != "calibration-skill":
        errors.append("project.name must be calibration-skill")
    if scripts.get("calibration-skill") != "calibration_skill.cli:main":
        errors.append("console script missing")
    if "calibration_skill*" not in packages:
        errors.append("calibration_skill package not included")
    if not any(pattern.endswith("*.schema.json") for pattern in package_data):
        errors.append("schema package data pattern missing")
    if forbidden_deps:
        errors.append(f"forbidden runtime dependencies: {forbidden_deps}")
    return {
        "status": "passed" if not errors else "failed",
        "project_name": project.get("name"),
        "dependencies": dependencies,
        "console_scripts": scripts,
        "package_data": package_data,
        "errors": errors,
    }


def inspect_artifacts(dist_dir: Path) -> dict[str, Any]:
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    errors: list[str] = []
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as zf:
            names = zf.namelist()
        required = [
            "calibration_skill/schemas/v1/skill_request.schema.json",
            "calibration_skill/skill/manifest.schema.json",
        ]
        for name in required:
            if name not in names:
                errors.append(f"{wheel.name} missing {name}")
        forbidden_prefixes = ("data/", "outputs/", "platforms/", "dist/")
        for name in names:
            if name.startswith(forbidden_prefixes):
                errors.append(f"{wheel.name} includes high-risk path {name}")
    return {
        "status": "passed" if wheels and sdists and not errors else "failed",
        "wheels": [p.name for p in wheels],
        "sdists": [p.name for p in sdists],
        "errors": errors,
    }


def build_check() -> dict[str, Any]:
    probe = run([*PY, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('build') else 1)"], timeout=30)
    if probe["returncode"] != 0:
        return {"status": "skipped_missing_dependency", "reason": "python build module is not installed"}
    with tempfile.TemporaryDirectory(prefix="m26e-build-") as tmp:
        dist_dir = Path(tmp) / "dist"
        result = run([*PY, "-m", "build", "--outdir", str(dist_dir)], timeout=240)
        inspected = inspect_artifacts(dist_dir) if result["returncode"] == 0 else {"status": "failed", "errors": ["build failed"]}
        return {"status": inspected["status"] if result["returncode"] == 0 else "failed", "build": result, "inspection": inspected}


def install_smoke() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="m26e-install-smoke-") as tmp:
        venv_dir = Path(tmp) / "venv"
        create = run([*PY, "-m", "venv", "--system-site-packages", str(venv_dir)], timeout=120)
        if create["returncode"] != 0:
            return {"status": "skipped_missing_dependency", "reason": "venv creation failed", "create": create}
        exe = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        install = run([str(exe), "-m", "pip", "install", "--no-deps", "-e", str(REPO_ROOT)], timeout=180)
        smoke = run([str(exe), "-m", "calibration_skill.cli", "manifest"], timeout=60) if install["returncode"] == 0 else {"status": "failed", "returncode": 1}
        console = run([str(venv_dir / ("Scripts/calibration-skill.exe" if os.name == "nt" else "bin/calibration-skill")), "manifest"], timeout=60) if install["returncode"] == 0 else {"status": "failed", "returncode": 1}
        status = "passed" if install["returncode"] == 0 and smoke["returncode"] == 0 and console["returncode"] == 0 else "failed"
        return {"status": status, "install": install, "module_cli": smoke, "console_cli": console}


def no_vendor_check() -> dict[str, Any]:
    guard = """
import builtins
forbidden = {'booster_robotics_sdk','unitree_sdk2','unitree_legged_sdk','rclpy','cyclonedds','fastdds'}
real_import = builtins.__import__
seen = []
def guarded(name, *args, **kwargs):
    root = name.split('.')[0].lower()
    if root in forbidden:
        raise RuntimeError('forbidden import attempted: ' + name)
    seen.append(name)
    return real_import(name, *args, **kwargs)
builtins.__import__ = guarded
import calibration_skill.cli as cli
code = cli.main(['invoke', '--input', 'examples/calibration_skill/dry_run_end_to_end.mock.json'])
raise SystemExit(code)
"""
    result = run([*PY, "-c", guard], timeout=60)
    return {"status": "passed" if result["returncode"] == 0 else "failed", "result": result}


def check_order(summary_path: Path | None) -> list[tuple[str, Any]]:
    checks: list[tuple[str, Any]] = []
    checks.append(("repository_initially_clean", check_repo_clean(summary_path)))
    if checks[-1][1]["status"] != "passed":
        return checks
    checks.append(("engineering_artifact_validation", run([*PY, "scripts/validate_engineering_artifacts.py"], timeout=120)))
    checks.append(("compileall", run([*PY, "-m", "compileall", "calibration_skill", "calibration_core", "k1_measurement", "platforms", "scripts", "tests", "-q"], timeout=180)))
    checks.append(("targeted_calibration_skill_tests", run([*PY, "-m", "pytest", "tests/calibration_skill", "-q"], timeout=180)))
    checks.append(("full_suite_hermetic", run([*PY, "scripts/run_tests_hermetically.py", "--", *PY, "-m", "pytest", "tests/", "--tb=no", "-q"], timeout=300)))
    checks.append(("cli_manifest_smoke", run([*PY, "-m", "calibration_skill.cli", "manifest"], timeout=60)))
    checks.append(("cli_examples_smoke", run([*PY, "-m", "calibration_skill.cli", "examples", "--operation", "dry_run_end_to_end"], timeout=60)))
    checks.append(("packaging_metadata_validation", validate_packaging_metadata()))
    checks.append(("build_wheel_sdist", build_check()))
    checks.append(("install_smoke", install_smoke()))
    checks.append(("no_vendor_sdk_import", no_vendor_check()))
    checks.append(("repository_final_clean", check_repo_clean(summary_path, final=True)))
    return checks


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalize_summary(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_summary(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_summary(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_summary(item) for item in value]
    if isinstance(value, str):
        text = re.sub(r"m26e-install-smoke-[A-Za-z0-9_]+", "m26e-install-smoke-<tmp>", value)
        text = re.sub(r"pip-ephem-wheel-cache-[A-Za-z0-9_]+", "pip-ephem-wheel-cache-<tmp>", text)
        text = re.sub(r"sha256=[0-9a-fA-F]{64}", "sha256=<sha256>", text)
        text = re.sub(r"\b\d+ passed in [0-9.]+s(?: \([0-9:]+\))?", lambda m: m.group(0).split(" in ")[0] + " in <duration>", text)
        return text
    return value


def infer_milestone(summary_path: Path | None) -> str:
    if summary_path is None:
        return "M26-E"
    name = summary_path.name.lower()
    if name.startswith("m27d1_"):
        return "M27-D.1"
    if name.startswith("m27d_"):
        return "M27-D"
    return "M26-E"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", help="Optional JSON summary output path")
    parser.add_argument("--dry-run", action="store_true", help="Emit check plan without running commands")
    args = parser.parse_args(argv)
    summary_path = (REPO_ROOT / args.summary).resolve() if args.summary else None
    if args.dry_run:
        names = [
            "repository_initially_clean",
            "engineering_artifact_validation",
            "compileall",
            "targeted_calibration_skill_tests",
            "full_suite_hermetic",
            "cli_manifest_smoke",
            "cli_examples_smoke",
            "packaging_metadata_validation",
            "build_wheel_sdist",
            "install_smoke",
            "no_vendor_sdk_import",
            "repository_final_clean",
        ]
        summary = {"status": "planned", "checks": [{"name": name, "status": "planned"} for name in names]}
        if summary_path:
            write_summary(summary_path, summary)
        print(json.dumps(summary, sort_keys=True))
        return 0

    checks = check_order(summary_path)
    summary = {
        "milestone": infer_milestone(summary_path),
        "status": "passed" if all(item[1].get("status") in {"passed", "skipped_missing_dependency"} for item in checks) else "failed",
        "checks": [{"name": name, **result} for name, result in checks],
    }
    if summary_path:
        write_summary(summary_path, summary)
    print(json.dumps({"status": summary["status"], "checks": len(checks)}, sort_keys=True))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
