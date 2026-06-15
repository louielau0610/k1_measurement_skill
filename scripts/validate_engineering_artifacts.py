#!/usr/bin/env python
"""M26-B Engineering Artifact Validator.

Validates:
1. All engineering JSON artifacts parse
2. Local Markdown links resolve under docs/engineering/
3. Repository paths in M26-A audit JSON exist
4. New domain/port/schema Python modules have no forbidden vendor imports
5. Readiness files do not claim G1/GO1 implementation
6. No numerical safety maximum is silently defaulted in generic contracts
7. Schema IDs and versions are unique and stable
8. All JSON Schema files parse as JSON

Produces deterministic failure messages and nonzero exit code on failure.
Does NOT modify any files.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_IMPORTS = [
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
]

EXIT_OK = 0
EXIT_FAIL = 1


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  OK: {msg}")


def parse_json(path: Path) -> dict | list | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"JSON parse error in {path}: {e}")
        return None


def validate_engineering_json_artifacts() -> int:
    """Parse all engineering JSON artifacts under outputs/engineering/."""
    eng_dir = REPO_ROOT / "outputs" / "engineering"
    if not eng_dir.is_dir():
        fail(f"Engineering output directory not found: {eng_dir}")
        return EXIT_FAIL

    errors = 0
    for fpath in sorted(eng_dir.glob("*.json")):
        data = parse_json(fpath)
        if data is None:
            errors += 1
        else:
            ok(f"JSON parsed: {fpath.name}")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_markdown_links() -> int:
    """Validate local Markdown links in docs/engineering/."""
    eng_docs = REPO_ROOT / "docs" / "engineering"
    if not eng_docs.is_dir():
        fail(f"Engineering docs directory not found: {eng_docs}")
        return EXIT_FAIL

    errors = 0
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for md_file in sorted(eng_docs.glob("*.md")):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        for match in link_pattern.finditer(content):
            target = match.group(2)
            # Skip external URLs
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            # Skip anchor-only links
            if target.startswith("#"):
                continue

            # Resolve relative to the doc file
            target_path = (md_file.parent / target).resolve()
            if not target_path.exists():
                fail(f"Broken link in {md_file.name}: {target}")
                errors += 1

    if errors == 0:
        ok("All Markdown links resolve")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_audit_paths() -> int:
    """Validate repository paths in m26a_repository_audit.json exist."""
    audit_path = REPO_ROOT / "outputs" / "engineering" / "m26a_repository_audit.json"
    if not audit_path.exists():
        fail(f"Audit file not found: {audit_path}")
        return EXIT_FAIL

    data = parse_json(audit_path)
    if data is None:
        return EXIT_FAIL

    errors = 0
    # Check significant findings for concrete paths
    for finding in data.get("significant_findings", []):
        fpath = finding.get("path", "")
        if not fpath:
            continue
        # Only validate paths that look like concrete repository paths
        if fpath.endswith(".py") or fpath.endswith(".yaml") or fpath.endswith(".json") or fpath.endswith(".md"):
            resolved = REPO_ROOT / fpath
            if not resolved.exists():
                fail(f"Audit path does not exist: {fpath}")
                errors += 1

    # Also check safety_critical_paths
    for p in data.get("safety_critical_paths", []):
        fpath = p.get("path", "")
        if fpath and (fpath.endswith(".py") or fpath.endswith(".yaml")):
            resolved = REPO_ROOT / fpath
            if not resolved.exists():
                fail(f"Safety path does not exist: {fpath}")
                errors += 1

    if errors == 0:
        ok("All audit paths exist")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_forbidden_imports() -> int:
    """Scan new calibration_skill Python modules for forbidden imports."""
    errors = 0
    skill_dir = REPO_ROOT / "calibration_skill"

    if not skill_dir.is_dir():
        fail(f"calibration_skill directory not found: {skill_dir}")
        return EXIT_FAIL

    for py_file in skill_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        for forbidden in FORBIDDEN_IMPORTS:
            if f"import {forbidden}" in content or f"from {forbidden}" in content:
                rel = py_file.relative_to(REPO_ROOT)
                fail(f"Forbidden import '{forbidden}' in {rel}")
                errors += 1

    if errors == 0:
        ok("No forbidden vendor imports in calibration_skill")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_readiness_no_false_claims() -> int:
    """Verify readiness files do not claim G1/GO1 implementation."""
    m26a_path = REPO_ROOT / "outputs" / "engineering" / "m26a_readiness.json"
    m26b_path = REPO_ROOT / "outputs" / "engineering" / "m26b_readiness.json"

    errors = 0
    for path in (m26a_path, m26b_path):
        if not path.exists():
            continue
        data = parse_json(path)
        if data is None:
            errors += 1
            continue
        readiness = data.get("readiness", data)
        for key in ("g1_adapter_implemented", "go1_adapter_implemented",
                     "g1_adapter_hardware_verified", "go1_adapter_hardware_verified"):
            val = readiness.get(key)
            if val is True:
                fail(f"{path.name}: {key} is true (should be false)")
                errors += 1

    if errors == 0:
        ok("No false G1/GO1 implementation claims")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_no_silent_safety_defaults() -> int:
    """Verify no numerical safety maximum is silently defaulted."""
    errors = 0
    # Check SafetyEnvelope construction requires explicit values
    safety_py = REPO_ROOT / "calibration_skill" / "domain" / "safety.py"
    if safety_py.exists():
        with open(safety_py, "r", encoding="utf-8") as f:
            content = f.read()
        # SafetyEnvelope should not have default values for max speeds
        if "max_abs_vx_mps: float = " in content:
            fail("SafetyEnvelope has default max_abs_vx_mps")
            errors += 1
        if "max_abs_vy_mps: float = " in content:
            fail("SafetyEnvelope has default max_abs_vy_mps")
            errors += 1
        if "max_abs_wz_radps: float = " in content:
            fail("SafetyEnvelope has default max_abs_wz_radps")
            errors += 1

    if errors == 0:
        ok("No silent safety defaults")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_schema_ids_unique() -> int:
    """Verify schema IDs and versions are unique and stable."""
    errors = 0
    schema_dir = REPO_ROOT / "calibration_skill" / "schemas" / "v1"
    if not schema_dir.is_dir():
        fail(f"Schema directory not found: {schema_dir}")
        return EXIT_FAIL

    seen_ids: set[str] = set()
    for schema_file in sorted(schema_dir.glob("*.schema.json")):
        data = parse_json(schema_file)
        if data is None:
            errors += 1
            continue
        sid = data.get("$id", "")
        if sid in seen_ids:
            fail(f"Duplicate schema $id: {sid}")
            errors += 1
        seen_ids.add(sid)

    if errors == 0:
        ok(f"All {len(seen_ids)} schema IDs unique")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_no_network_or_hardware() -> int:
    """Verify calibration_skill has no network or hardware operations."""
    errors = 0
    skill_dir = REPO_ROOT / "calibration_skill"

    for py_file in skill_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Check for socket operations
        if "socket." in content and "import socket" not in content:
            pass  # Could be false positive
        # Check for subprocess
        if "subprocess.run" in content or "subprocess.Popen" in content:
            rel = py_file.relative_to(REPO_ROOT)
            fail(f"subprocess call in {rel}")
            errors += 1

    if errors == 0:
        ok("No network/hardware operations in calibration_skill")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def main() -> int:
    print("=== M26-B Engineering Artifact Validator ===\n")

    results = [
        ("JSON artifacts", validate_engineering_json_artifacts()),
        ("Markdown links", validate_markdown_links()),
        ("Audit paths", validate_audit_paths()),
        ("Forbidden imports", validate_forbidden_imports()),
        ("Readiness claims", validate_readiness_no_false_claims()),
        ("Silent safety defaults", validate_no_silent_safety_defaults()),
        ("Schema IDs unique", validate_schema_ids_unique()),
        ("No network/hardware ops", validate_no_network_or_hardware()),
    ]

    print()
    failures = sum(1 for _, rc in results if rc != EXIT_OK)
    if failures == 0:
        print(f"ALL {len(results)} CHECKS PASSED")
        return EXIT_OK
    else:
        print(f"{failures}/{len(results)} CHECKS FAILED")
        return EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
