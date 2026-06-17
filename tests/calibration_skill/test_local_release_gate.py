"""Local release gate tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "run_local_release_gate.py"


def test_dry_run_lists_release_checks(tmp_path):
    summary = tmp_path / "summary.json"
    result = subprocess.run(
        [sys.executable, str(GATE), "--dry-run", "--summary", str(summary)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(summary.read_text(encoding="utf-8"))
    names = [check["name"] for check in data["checks"]]
    assert names == [
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


def test_packaging_metadata_validation_function_passes():
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_local_release_gate", GATE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.validate_packaging_metadata()
    assert result["status"] == "passed"
    assert result["console_scripts"]["calibration-skill"] == "calibration_skill.cli:main"


def test_failure_propagates_when_repository_is_dirty(tmp_path):
    dirty = ROOT / "_m26e_release_gate_dirty_probe.tmp"
    try:
        dirty.write_text("dirty\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(GATE), "--summary", str(tmp_path / "summary.json")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        data = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
        assert result.returncode == 1
        assert data["status"] == "failed"
        assert data["checks"][0]["name"] == "repository_initially_clean"
        assert data["checks"][0]["status"] == "failed"
    finally:
        if dirty.exists():
            dirty.unlink()


def test_release_gate_source_does_not_restore_repository():
    text = GATE.read_text(encoding="utf-8")
    forbidden = ('["git", "checkout"', '["git", "restore"', '["git", "reset"', '["git", "clean"')
    assert not any(command in text for command in forbidden)
