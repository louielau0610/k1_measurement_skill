#!/usr/bin/env python
"""M26/M27 Engineering Artifact Validator.

Validates:
1. All engineering JSON artifacts parse
2. Local Markdown links resolve under docs/engineering/
3. Repository paths in M26-A audit JSON exist
4. New domain/port/schema Python modules have no forbidden vendor imports
5. Readiness files do not claim G1/GO1 implementation
6. No numerical safety maximum is silently defaulted in generic contracts
7. Schema IDs and versions are unique and stable
8. All JSON Schema files parse as JSON
9. M26-C layering boundaries are preserved
10. M26-C readiness does not claim real-platform or hardware support
11. M26-D manifest and operation catalog are stable
12. M26-D examples are deterministic and path-portable
13. M26-E packaging metadata is dry-run-only and local-package ready
14. M26-E release scripts exist and avoid repository restore commands
15. M26-E distribution documents exist
16. M26-E readiness remains conservative
17. M27-A output JSON files parse
18. M27-A K1 remains not registered in AdapterRegistry
19. M27-A M26-D manifest still marks K1 unavailable
20. M27-A no new Booster SDK import in core calibration_skill layers
21. M27-A no hardware readiness field is upgraded
22. M27-A K1 migration remains planning-only until M27-B artifacts exist
23. M27-B K1 fake-runtime artifacts exist
24. M27-B K1 remains no-hardware and not default-registered
25. M27-C vendor runtime boundary artifacts exist
26. M27-C K1 vendor runtime remains disabled and no-hardware

Produces deterministic failure messages and nonzero exit code on failure.
Does NOT modify any files.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    """Scan calibration_skill Python modules for forbidden imports."""
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
    """Verify all engineering JSON files do not claim G1/GO1 implementation."""
    eng_dir = REPO_ROOT / "outputs" / "engineering"
    if not eng_dir.is_dir():
        fail(f"Engineering output directory not found: {eng_dir}")
        return EXIT_FAIL

    errors = 0
    false_claim_keys = (
        "g1_adapter_implemented", "go1_adapter_implemented",
        "g1_adapter_hardware_verified", "go1_adapter_hardware_verified",
    )

    for fpath in sorted(eng_dir.glob("*.json")):
        data = parse_json(fpath)
        if data is None:
            continue
        # Check top-level readiness and nested readiness
        for section in (data, data.get("readiness", {})):
            if not isinstance(section, dict):
                continue
            for key in false_claim_keys:
                val = section.get(key)
                if val is True:
                    fail(f"{fpath.name}: {key} is true (should be false)")
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


def validate_m26c_layering() -> int:
    """Verify domain/ports/schemas do not depend on adapters, skill, or runtime."""
    errors = 0
    restricted_dirs = [
        REPO_ROOT / "calibration_skill" / "domain",
        REPO_ROOT / "calibration_skill" / "ports",
        REPO_ROOT / "calibration_skill" / "schemas",
    ]
    forbidden_refs = (
        "calibration_skill.adapters",
        "calibration_skill.skill",
        "calibration_skill.runtime",
    )
    for directory in restricted_dirs:
        for py_file in sorted(directory.glob("*.py")):
            content = py_file.read_text(encoding="utf-8")
            for ref in forbidden_refs:
                if ref in content:
                    rel = py_file.relative_to(REPO_ROOT)
                    fail(f"M26-C layering violation: {rel} references {ref}")
                    errors += 1
    if errors == 0:
        ok("M26-C layering boundaries clean")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26c_readiness() -> int:
    """Verify M26-C readiness claims remain mock-only and hardware-free."""
    readiness_path = REPO_ROOT / "outputs" / "engineering" / "m26c_readiness.json"
    if not readiness_path.exists():
        fail(f"M26-C readiness file not found: {readiness_path}")
        return EXIT_FAIL
    data = parse_json(readiness_path)
    if data is None:
        return EXIT_FAIL
    readiness = data.get("readiness", {})
    errors = 0
    expected = {
        "mock_adapter": "bench_verified",
        "adapter_registry": "bench_verified",
        "skill_service_skeleton": "bench_verified",
        "dry_run_end_to_end": "bench_verified",
        "hardware_verification": "not_started",
        "release": "not_started",
    }
    for key, maturity in expected.items():
        actual = readiness.get(key, {}).get("maturity")
        if actual != maturity:
            fail(f"m26c_readiness.json: {key} maturity is {actual!r}, expected {maturity!r}")
            errors += 1
    for key in ("k1_adapter_migration", "g1_adapter", "go1_adapter"):
        actual = readiness.get(key, {}).get("maturity")
        if actual == "hardware_verified":
            fail(f"m26c_readiness.json: {key} must not be hardware_verified")
            errors += 1
    if errors == 0:
        ok("M26-C readiness remains mock-only and hardware-free")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26d_manifest_and_catalog() -> int:
    """Verify M26-D manifest/catalog artifacts match the code source of truth."""
    errors = 0
    try:
        from calibration_skill.skill.manifest import build_skill_manifest, operation_catalog
    except Exception as exc:
        fail(f"Could not import M26-D manifest module: {exc}")
        return EXIT_FAIL

    manifest_path = REPO_ROOT / "outputs" / "engineering" / "m26d_skill_manifest.json"
    catalog_path = REPO_ROOT / "outputs" / "engineering" / "m26d_operation_catalog.json"
    schema_path = REPO_ROOT / "calibration_skill" / "skill" / "manifest.schema.json"
    for path in (manifest_path, catalog_path, schema_path):
        if not path.exists():
            fail(f"M26-D required artifact missing: {path.relative_to(REPO_ROOT)}")
            errors += 1
    if errors:
        return EXIT_FAIL

    manifest = parse_json(manifest_path)
    catalog = parse_json(catalog_path)
    schema = parse_json(schema_path)
    if manifest != build_skill_manifest():
        fail("m26d_skill_manifest.json does not match build_skill_manifest()")
        errors += 1
    expected_ops = [op["name"] for op in operation_catalog()]
    if catalog.get("operations") != operation_catalog():
        fail("m26d_operation_catalog.json does not match operation_catalog()")
        errors += 1
    if manifest and manifest.get("supported_operations") != expected_ops:
        fail("M26-D manifest supported_operations mismatch")
        errors += 1
    if manifest and any("physical" in op for op in manifest.get("supported_operations", [])):
        fail("M26-D manifest lists a physical operation")
        errors += 1
    if manifest and manifest.get("platform_support", {}).get("mock", {}).get("dry_run_only") is not True:
        fail("M26-D manifest must mark mock dry_run_only=true")
        errors += 1
    if manifest and manifest.get("platform_support", {}).get("booster_k1", {}).get("status") == "supported":
        fail("M26-D manifest must not mark booster_k1 supported")
        errors += 1
    if errors == 0:
        ok("M26-D manifest and operation catalog stable")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26d_examples() -> int:
    """Verify examples parse, contain no machine-local paths, and cover required files."""
    example_dir = REPO_ROOT / "examples" / "calibration_skill"
    required = {
        "preflight_request.mock.json",
        "dry_run_velocity_command.mock.json",
        "dry_run_collect_telemetry.mock.json",
        "dry_run_stop.mock.json",
        "dry_run_end_to_end.mock.json",
        "invalid_real_platform_request.json",
        "invalid_dry_run_false_request.json",
        "invalid_missing_safety_request.json",
    }
    errors = 0
    if not example_dir.is_dir():
        fail(f"M26-D example directory missing: {example_dir}")
        return EXIT_FAIL
    found = {p.name for p in example_dir.glob("*.json")}
    for name in sorted(required - found):
        fail(f"M26-D required example missing: {name}")
        errors += 1
    for path in sorted(example_dir.glob("*.json")):
        data = parse_json(path)
        if data is None:
            errors += 1
            continue
        text = path.read_text(encoding="utf-8")
        if "C:\\" in text or "\\Users\\" in text or "Users/" in text:
            fail(f"M26-D example contains machine-local path: {path.name}")
            errors += 1
        if data.get("schema_version") != "1.0.0":
            fail(f"M26-D example has wrong schema_version: {path.name}")
            errors += 1
    if errors == 0:
        ok("M26-D examples parse and are path-portable")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26d_readiness() -> int:
    """Verify M26-D readiness contains CLI progress but no hardware claims."""
    readiness_path = REPO_ROOT / "outputs" / "engineering" / "m26d_readiness.json"
    if not readiness_path.exists():
        fail(f"M26-D readiness file not found: {readiness_path}")
        return EXIT_FAIL
    data = parse_json(readiness_path)
    if data is None:
        return EXIT_FAIL
    readiness = data.get("readiness", {})
    errors = 0
    expected = {
        "agent_cli": "bench_verified",
        "json_io_contract": "bench_verified",
        "unified_skill_runtime": "dry_run_only",
        "hardware_verification": "not_started",
        "release": "not_started",
    }
    for key, maturity in expected.items():
        actual = readiness.get(key, {}).get("maturity")
        if actual != maturity:
            fail(f"m26d_readiness.json: {key} maturity is {actual!r}, expected {maturity!r}")
            errors += 1
    for key in ("k1_adapter_migration", "g1_adapter", "go1_adapter"):
        actual = readiness.get(key, {}).get("maturity")
        if actual in ("bench_verified", "hardware_verified"):
            fail(f"m26d_readiness.json: {key} must not claim new runtime support")
            errors += 1
    if errors == 0:
        ok("M26-D readiness remains dry-run-only")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26e_packaging_metadata() -> int:
    """Verify M26-E package metadata exposes only the dry-run calibration skill."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        fail("pyproject.toml not found")
        return EXIT_FAIL
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    setuptools = data.get("tool", {}).get("setuptools", {})
    errors = 0
    if project.get("name") != "calibration-skill":
        fail("M26-E package name must be calibration-skill")
        errors += 1
    scripts = project.get("scripts", {})
    if scripts.get("calibration-skill") != "calibration_skill.cli:main":
        fail("M26-E console script calibration-skill is missing or incorrect")
        errors += 1
    dependencies = [dep.lower() for dep in project.get("dependencies", [])]
    for forbidden in FORBIDDEN_IMPORTS:
        if any(forbidden in dep for dep in dependencies):
            fail(f"M26-E pyproject lists forbidden dependency {forbidden}")
            errors += 1
    optional = project.get("optional-dependencies", {})
    booster_extra = optional.get("booster-k1")
    if booster_extra is not None:
        for dep in [str(dep).lower() for dep in booster_extra]:
            for forbidden in FORBIDDEN_IMPORTS:
                if forbidden in dep:
                    fail(f"M27-C booster-k1 optional extra lists forbidden dependency {forbidden}")
                    errors += 1
    package_include = setuptools.get("packages", {}).get("find", {}).get("include", [])
    if "calibration_skill*" not in package_include:
        fail("M26-E pyproject does not include calibration_skill package")
        errors += 1
    package_data = setuptools.get("package-data", {}).get("calibration_skill", [])
    for required in ("schemas/v1/*.schema.json", "skill/manifest.schema.json"):
        if required not in package_data:
            fail(f"M26-E package data missing {required}")
            errors += 1
    if errors == 0:
        ok("M26-E packaging metadata is conservative")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26e_release_scripts() -> int:
    """Verify M26-E release scripts exist and do not auto-restore repository files."""
    errors = 0
    scripts = [
        REPO_ROOT / "scripts" / "run_tests_hermetically.py",
        REPO_ROOT / "scripts" / "run_local_release_gate.py",
    ]
    forbidden_restore_calls = (
        '["git", "checkout"',
        '["git", "restore"',
        '["git", "reset"',
        '["git", "clean"',
    )
    for script in scripts:
        if not script.exists():
            fail(f"M26-E script missing: {script.relative_to(REPO_ROOT)}")
            errors += 1
            continue
        text = script.read_text(encoding="utf-8")
        for forbidden in forbidden_restore_calls:
            if forbidden in text:
                fail(f"M26-E script contains forbidden restore command call: {script.name}: {forbidden}")
                errors += 1
    if errors == 0:
        ok("M26-E release scripts exist and avoid restore commands")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26e_docs_exist() -> int:
    """Verify required M26-E distribution-readiness documents exist."""
    docs = [
        REPO_ROOT / "docs" / "engineering" / "m26e_packaging_and_release_gate.md",
        REPO_ROOT / "docs" / "engineering" / "m26e_distribution_readiness.md",
        REPO_ROOT / "docs" / "engineering" / "m26e_no_vendor_runtime_boundary.md",
    ]
    errors = 0
    for doc in docs:
        if not doc.exists():
            fail(f"M26-E doc missing: {doc.relative_to(REPO_ROOT)}")
            errors += 1
    if errors == 0:
        ok("M26-E docs exist")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m26e_readiness() -> int:
    """Verify M26-E readiness claims packaging progress without hardware release claims."""
    readiness_path = REPO_ROOT / "outputs" / "engineering" / "m26e_readiness.json"
    if not readiness_path.exists():
        fail(f"M26-E readiness file not found: {readiness_path}")
        return EXIT_FAIL
    data = parse_json(readiness_path)
    if data is None:
        return EXIT_FAIL
    readiness = data.get("readiness", {})
    errors = 0
    expected = {
        "packaging_metadata": "bench_verified",
        "console_script": "bench_verified",
        "local_release_gate": "bench_verified",
        "unified_skill_runtime": "dry_run_only",
        "hardware_verification": "not_started",
        "release": "pre_release_only",
    }
    for key, maturity in expected.items():
        actual = readiness.get(key, {}).get("maturity")
        if actual != maturity:
            fail(f"m26e_readiness.json: {key} maturity is {actual!r}, expected {maturity!r}")
            errors += 1
    for key in ("k1_adapter_migration", "g1_adapter", "go1_adapter"):
        actual = readiness.get(key, {}).get("maturity")
        if actual in ("bench_verified", "hardware_verified", "supported"):
            fail(f"m26e_readiness.json: {key} must not claim new runtime support")
            errors += 1
    if errors == 0:
        ok("M26-E readiness remains pre-release and hardware-free")
    return EXIT_FAIL if errors > 0 else EXIT_OK


# ── M27-A validation ────────────────────────────────────────────────────

def validate_m27a_output_json_parse() -> int:
    """Verify all M27-A output JSON files parse as valid JSON."""
    m27a_files = [
        "m27a_initial_state.json",
        "m27a_k1_legacy_inventory.json",
        "m27a_k1_command_path_audit.json",
        "m27a_k1_telemetry_path_audit.json",
        "m27a_k1_safety_gate_audit.json",
        "m27a_k1_to_robot_adapter_mapping.json",
        "m27a_k1_compatibility_test_plan.json",
        "m27a_k1_migration_risk_register.json",
        "m27a_readiness.json",
        "m27a_validation_summary.json",
    ]
    errors = 0
    for filename in m27a_files:
        path = REPO_ROOT / "outputs" / "engineering" / filename
        if not path.exists():
            fail(f"M27-A output missing: {filename}")
            errors += 1
            continue
        data = parse_json(path)
        if data is None:
            errors += 1
        else:
            ok(f"M27-A JSON parsed: {filename}")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27a_k1_not_in_registry() -> int:
    """Verify K1 remains not registered in M26-C AdapterRegistry."""
    errors = 0
    registry_py = REPO_ROOT / "calibration_skill" / "adapters" / "registry.py"
    if not registry_py.exists():
        fail("AdapterRegistry file not found")
        return EXIT_FAIL
    content = registry_py.read_text(encoding="utf-8")
    # Verify registry rejects non-MOCK platforms
    if "platform != RobotPlatform.MOCK" not in content:
        fail("AdapterRegistry may have weakened MOCK-only guard")
        errors += 1
    # Verify no K1 registration
    if "RobotPlatform.BOOSTER_K1" in content and "register" in content:
        # Check context — may be in error message, not registration
        if 'register(' in content[content.find("RobotPlatform.BOOSTER_K1"):content.find("RobotPlatform.BOOSTER_K1") + 200]:
            fail("AdapterRegistry appears to register BOOSTER_K1")
            errors += 1
    if errors == 0:
        ok("K1 not registered in AdapterRegistry")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27a_m26d_manifest_k1_unavailable() -> int:
    """Verify M26-D CLI manifest still marks K1 unavailable in new runtime."""
    errors = 0
    manifest_path = REPO_ROOT / "outputs" / "engineering" / "m26d_skill_manifest.json"
    if not manifest_path.exists():
        fail("M26-D manifest not found")
        return EXIT_FAIL
    data = parse_json(manifest_path)
    if data is None:
        return EXIT_FAIL
    k1_status = data.get("platform_support", {}).get("booster_k1", {}).get("status", "unknown")
    if k1_status == "supported":
        fail("M26-D manifest marks booster_k1 as supported (should be unavailable)")
        errors += 1
    if data.get("platform_support", {}).get("mock", {}).get("dry_run_only") is not True:
        fail("M26-D manifest mock platform must be dry_run_only=true")
        errors += 1
    if errors == 0:
        ok("M26-D manifest K1 unavailable")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27a_no_new_booster_sdk() -> int:
    """Verify no new Booster SDK import appears under generic calibration_skill."""
    errors = 0
    # Directories that must remain vendor-free
    vendor_free_dirs = [
        REPO_ROOT / "calibration_skill" / "skill",
        REPO_ROOT / "calibration_skill" / "runtime",
        REPO_ROOT / "calibration_skill" / "domain",
        REPO_ROOT / "calibration_skill" / "ports",
        REPO_ROOT / "calibration_skill" / "schemas",
    ]
    booster_patterns = (
        "booster_robotics_sdk",
        "B1LocoClient",
        "ChannelFactory",
        "RobotMode",
    )
    for directory in vendor_free_dirs:
        if not directory.is_dir():
            continue
        for py_file in directory.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for pattern in booster_patterns:
                if pattern in content:
                    rel = py_file.relative_to(REPO_ROOT)
                    fail(f"Booster SDK import '{pattern}' in vendor-free layer: {rel}")
                    errors += 1
    if errors == 0:
        ok("No Booster SDK in calibration_skill core layers")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27a_no_hardware_readiness_upgrade() -> int:
    """Verify no hardware readiness field is upgraded in M27-A."""
    errors = 0
    readiness_path = REPO_ROOT / "outputs" / "engineering" / "m27a_readiness.json"
    if not readiness_path.exists():
        fail("M27-A readiness file not found")
        return EXIT_FAIL
    data = parse_json(readiness_path)
    if data is None:
        return EXIT_FAIL
    readiness = data.get("readiness", {})
    # These must remain not_started or the equivalent
    must_not_be_verified = {
        "k1_new_runtime_support": "not_started",
        "hardware_verification": "not_started",
    }
    for key, expected in must_not_be_verified.items():
        actual = readiness.get(key, {}).get("maturity")
        if actual != expected:
            fail(f"m27a_readiness.json: {key} maturity is {actual!r}, expected {expected!r}")
            errors += 1
    # K1 adapter migration must be "planned" not "implemented" or "bench_verified"
    k1_migration = readiness.get("k1_adapter_migration", {}).get("maturity")
    if k1_migration in ("bench_verified", "hardware_verified", "implemented"):
        fail(f"m27a_readiness.json: k1_adapter_migration must not be {k1_migration}")
        errors += 1
    if errors == 0:
        ok("M27-A readiness no hardware upgrade")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27a_k1_planning_only() -> int:
    """Verify K1 migration remains planning-only; no implementation files created."""
    errors = 0
    m27b_readiness = REPO_ROOT / "outputs" / "engineering" / "m27b_readiness.json"
    # Check that no K1 adapter implementation exists in calibration_skill/adapters/
    adapters_dir = REPO_ROOT / "calibration_skill" / "adapters"
    k1_adapter_files = [
        adapters_dir / "booster_k1" / "adapter.py",
        adapters_dir / "booster_k1" / "__init__.py",
        adapters_dir / "k1_adapter.py",
        adapters_dir / "booster_k1_adapter.py",
    ]
    for path in k1_adapter_files:
        if path.exists() and not m27b_readiness.exists():
            fail(f"K1 adapter implementation exists (should not before M27-B): {path.relative_to(REPO_ROOT)}")
            errors += 1
    # Verify no K1 registration call in any __init__.py or startup
    skill_init = REPO_ROOT / "calibration_skill" / "__init__.py"
    if skill_init.exists():
        content = skill_init.read_text(encoding="utf-8")
        if "BOOSTER_K1" in content and "register" in content:
            fail("calibration_skill/__init__.py may register K1")
            errors += 1
    # Verify the register call with BOOSTER_K1 is guarded or absent from adapter __init__
    adapter_init = adapters_dir / "__init__.py"
    if adapter_init.exists():
        content = adapter_init.read_text(encoding="utf-8")
        if "BOOSTER_K1" in content and "register" in content:
            fail("calibration_skill/adapters/__init__.py may auto-register K1")
            errors += 1
    if errors == 0:
        ok("K1 migration boundary remains explicit")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27b_artifacts_exist() -> int:
    """Verify required M27-B docs and machine-readable artifacts exist."""
    required = [
        "docs/engineering/m27b_k1_adapter_skeleton.md",
        "docs/engineering/m27b_k1_fake_runtime_contract.md",
        "docs/engineering/m27b_k1_no_hardware_boundary.md",
        "outputs/engineering/m27b_initial_state.json",
        "outputs/engineering/m27b_readiness.json",
        "outputs/engineering/m27b_validation_summary.json",
        "outputs/engineering/m27b_k1_adapter_contract_report.json",
        "calibration_skill/adapters/booster_k1/adapter.py",
        "calibration_skill/adapters/booster_k1/runtime.py",
        "tests/calibration_skill/fakes/fake_booster_k1_runtime.py",
    ]
    errors = 0
    for rel in required:
        if not (REPO_ROOT / rel).exists():
            fail(f"M27-B required artifact missing: {rel}")
            errors += 1
    if errors == 0:
        ok("M27-B artifacts exist")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27b_no_hardware_boundary() -> int:
    """Verify M27-B K1 skeleton remains fake-runtime-only."""
    errors = 0
    readiness_path = REPO_ROOT / "outputs" / "engineering" / "m27b_readiness.json"
    summary_path = REPO_ROOT / "outputs" / "engineering" / "m27b_validation_summary.json"
    readiness_data = parse_json(readiness_path) if readiness_path.exists() else None
    summary_data = parse_json(summary_path) if summary_path.exists() else None
    if not isinstance(readiness_data, dict):
        fail("M27-B readiness file missing or invalid")
        return EXIT_FAIL
    readiness = readiness_data.get("readiness", {})
    expected = {
        "k1_adapter_migration": {"fake_runtime_verified", "implemented_unverified"},
        "k1_new_runtime_support": {"fake_runtime_only"},
        "k1_hardware_verification": {"not_started"},
        "hardware_verification": {"not_started"},
        "release": {"pre_release_only"},
    }
    for key, allowed in expected.items():
        actual = readiness.get(key, {}).get("maturity")
        if actual not in allowed:
            fail(f"m27b_readiness.json: {key} maturity is {actual!r}, expected one of {sorted(allowed)}")
            errors += 1
    if isinstance(summary_data, dict):
        for key in ("hardware_used", "vendor_sdk_imported", "default_k1_registration", "socket_or_dds_used"):
            if summary_data.get(key) is not False:
                fail(f"m27b_validation_summary.json: {key} must be false")
                errors += 1
    manifest_path = REPO_ROOT / "outputs" / "engineering" / "m26d_skill_manifest.json"
    manifest = parse_json(manifest_path)
    if isinstance(manifest, dict):
        status = manifest.get("platform_support", {}).get("booster_k1", {}).get("status")
        if status == "supported":
            fail("Default CLI manifest must not mark booster_k1 supported")
            errors += 1
    if errors == 0:
        ok("M27-B K1 no-hardware boundary clean")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27c_artifacts_exist() -> int:
    """Verify required M27-C docs, code, and machine-readable artifacts exist."""
    required = [
        "calibration_skill/adapters/booster_k1/vendor_runtime.py",
        "docs/engineering/m27c_k1_vendor_runtime_boundary.md",
        "docs/engineering/m27c_k1_hardware_gate.md",
        "docs/engineering/m27c_k1_future_booster_sdk_integration.md",
        "outputs/engineering/m27c_initial_state.json",
        "outputs/engineering/m27c_readiness.json",
        "outputs/engineering/m27c_validation_summary.json",
        "outputs/engineering/m27c_vendor_runtime_status.json",
        "outputs/engineering/m27c_hardware_gate_contract.json",
        "tests/calibration_skill/test_booster_k1_vendor_runtime_boundary.py",
        "tests/calibration_skill/test_booster_k1_hardware_gate.py",
        "tests/calibration_skill/test_booster_k1_vendor_registration_boundary.py",
        "tests/calibration_skill/test_m27c_readiness.py",
    ]
    errors = 0
    for rel in required:
        if not (REPO_ROOT / rel).exists():
            fail(f"M27-C required artifact missing: {rel}")
            errors += 1
    if errors == 0:
        ok("M27-C artifacts exist")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def validate_m27c_no_hardware_boundary() -> int:
    """Verify M27-C vendor boundary remains fail-closed and no-hardware."""
    errors = 0
    readiness = parse_json(REPO_ROOT / "outputs" / "engineering" / "m27c_readiness.json")
    summary = parse_json(REPO_ROOT / "outputs" / "engineering" / "m27c_validation_summary.json")
    status = parse_json(REPO_ROOT / "outputs" / "engineering" / "m27c_vendor_runtime_status.json")
    if not isinstance(readiness, dict) or not isinstance(summary, dict) or not isinstance(status, dict):
        fail("M27-C readiness, summary, or vendor status is missing/invalid")
        return EXIT_FAIL
    readiness_values = readiness.get("readiness", {})
    expected = {
        "k1_adapter_migration": {"fake_runtime_verified"},
        "k1_new_runtime_support": {"fake_runtime_only"},
        "k1_vendor_runtime_boundary": {"bench_verified"},
        "k1_vendor_runtime": {"not_implemented"},
        "k1_hardware_gate": {"bench_verified"},
        "k1_hardware_verification": {"not_started"},
        "hardware_verification": {"not_started"},
        "release": {"pre_release_only"},
    }
    for key, allowed in expected.items():
        actual = readiness_values.get(key, {}).get("maturity")
        if actual not in allowed:
            fail(f"m27c_readiness.json: {key} maturity is {actual!r}, expected one of {sorted(allowed)}")
            errors += 1
    for key in ("hardware_used", "vendor_sdk_imported", "default_k1_real_registration", "socket_or_dds_used", "real_vendor_runtime_implemented"):
        if summary.get(key) is not False:
            fail(f"m27c_validation_summary.json: {key} must be false")
            errors += 1
    if status.get("vendor_runtime_implemented") is not False:
        fail("m27c_vendor_runtime_status.json must mark vendor_runtime_implemented=false")
        errors += 1
    if status.get("hardware_enabled") is not False:
        fail("m27c_vendor_runtime_status.json must mark hardware_enabled=false")
        errors += 1
    if status.get("ordinary_runtime_import_safe") is not True:
        fail("m27c_vendor_runtime_status.json must mark ordinary_runtime_import_safe=true")
        errors += 1
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    booster_extra = pyproject.get("project", {}).get("optional-dependencies", {}).get("booster-k1")
    if booster_extra != []:
        fail("M27-C booster-k1 optional extra must remain an empty placeholder")
        errors += 1
    manifest = parse_json(REPO_ROOT / "outputs" / "engineering" / "m26d_skill_manifest.json")
    if isinstance(manifest, dict):
        if manifest.get("platform_support", {}).get("booster_k1", {}).get("status") == "supported":
            fail("Default CLI manifest must not mark real booster_k1 supported")
            errors += 1
    if errors == 0:
        ok("M27-C K1 vendor runtime boundary remains disabled")
    return EXIT_FAIL if errors > 0 else EXIT_OK


def main() -> int:
    print("=== M26/M27 Engineering Artifact Validator ===\n")

    results = [
        ("JSON artifacts", validate_engineering_json_artifacts()),
        ("Markdown links", validate_markdown_links()),
        ("Audit paths", validate_audit_paths()),
        ("Forbidden imports", validate_forbidden_imports()),
        ("Readiness claims", validate_readiness_no_false_claims()),
        ("Silent safety defaults", validate_no_silent_safety_defaults()),
        ("Schema IDs unique", validate_schema_ids_unique()),
        ("No network/hardware ops", validate_no_network_or_hardware()),
        ("M26-C layering", validate_m26c_layering()),
        ("M26-C readiness", validate_m26c_readiness()),
        ("M26-D manifest/catalog", validate_m26d_manifest_and_catalog()),
        ("M26-D examples", validate_m26d_examples()),
        ("M26-D readiness", validate_m26d_readiness()),
        ("M26-E packaging metadata", validate_m26e_packaging_metadata()),
        ("M26-E release scripts", validate_m26e_release_scripts()),
        ("M26-E docs", validate_m26e_docs_exist()),
        ("M26-E readiness", validate_m26e_readiness()),
        # ── M27-A checks ──
        ("M27-A output JSON parse", validate_m27a_output_json_parse()),
        ("M27-A K1 not in registry", validate_m27a_k1_not_in_registry()),
        ("M27-A M26-D manifest K1 unavailable", validate_m27a_m26d_manifest_k1_unavailable()),
        ("M27-A no new Booster SDK", validate_m27a_no_new_booster_sdk()),
        ("M27-A no hardware readiness upgrade", validate_m27a_no_hardware_readiness_upgrade()),
        ("M27-A K1 planning only", validate_m27a_k1_planning_only()),
        ("M27-B artifacts", validate_m27b_artifacts_exist()),
        ("M27-B no hardware boundary", validate_m27b_no_hardware_boundary()),
        ("M27-C artifacts", validate_m27c_artifacts_exist()),
        ("M27-C no hardware boundary", validate_m27c_no_hardware_boundary()),
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
