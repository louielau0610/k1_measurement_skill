"""M26-E packaging metadata tests."""
from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_DEP_NAMES = {
    "booster",
    "unitree",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
    "ros2",
}


def load_pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_exists_and_parses():
    data = load_pyproject()
    assert data["project"]["name"] == "calibration-skill"
    assert data["build-system"]["build-backend"] == "setuptools.build_meta"


def test_console_entry_point_declared():
    scripts = load_pyproject()["project"]["scripts"]
    assert scripts["calibration-skill"] == "calibration_skill.cli:main"


def test_calibration_skill_package_and_data_declared():
    data = load_pyproject()
    include = data["tool"]["setuptools"]["packages"]["find"]["include"]
    package_data = data["tool"]["setuptools"]["package-data"]["calibration_skill"]
    assert "calibration_skill*" in include
    assert "schemas/v1/*.schema.json" in package_data
    assert "skill/manifest.schema.json" in package_data


def test_runtime_dependencies_stay_dry_run_only():
    dependencies = [dep.lower() for dep in load_pyproject()["project"]["dependencies"]]
    assert dependencies == ["jsonschema>=4.18"]
    assert not any(name in dep for dep in dependencies for name in FORBIDDEN_DEP_NAMES)


def test_high_risk_paths_are_not_packaged():
    data = load_pyproject()
    include = data["tool"]["setuptools"]["packages"]["find"]["include"]
    package_data = data["tool"]["setuptools"]["package-data"]["calibration_skill"]
    serialized = repr({"include": include, "patterns": package_data})
    for path in ("data", "outputs", "platforms", "dist", "vendor", "raw"):
        assert path not in serialized
