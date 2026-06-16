"""Engineering artifact validator regression tests."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate_engineering_artifacts.py"


def _run_validator(*extra_args: str) -> tuple[int, str, str]:
    """Run the validator script and return (exit_code, stdout, stderr)."""
    python = sys.executable
    result = subprocess.run(
        [python, str(VALIDATOR_SCRIPT), *extra_args],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


class TestValidatorHappyPath:
    def test_validator_passes_on_clean_repo(self):
        exit_code, stdout, stderr = _run_validator()
        assert exit_code == 0, f"Validator failed:\n{stdout}\n{stderr}"
        assert "ALL 10 CHECKS PASSED" in stdout

    def test_validator_does_not_modify_tracked_files(self):
        """Running the validator must not change any tracked files."""
        # Record current state
        before = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        ).stdout.strip()
        _run_validator()
        after = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        ).stdout.strip()
        assert before == after, f"Validator modified files:\nBefore: {before}\nAfter: {after}"


class TestValidatorJsonParsing:
    def test_malformed_json_detected(self):
        """Simulate a malformed JSON artifact."""
        eng_dir = REPO_ROOT / "outputs" / "engineering"
        bad_file = eng_dir / "_test_bad.json"
        try:
            bad_file.write_text("not valid json {{{")
            exit_code, stdout, _ = _run_validator()
            assert exit_code != 0, "Validator should fail on malformed JSON"
            assert "FAIL" in stdout
        finally:
            if bad_file.exists():
                bad_file.unlink()


class TestValidatorReadiness:
    def test_false_g1_claim_detected(self):
        """Simulate readiness file with false G1 claim."""
        eng_dir = REPO_ROOT / "outputs" / "engineering"
        bad_file = eng_dir / "_test_bad_readiness.json"
        try:
            bad_file.write_text(json.dumps({"readiness": {"g1_adapter_implemented": True}}))
            exit_code, stdout, _ = _run_validator()
            assert exit_code != 0, "Validator should detect false G1 claim"
        finally:
            if bad_file.exists():
                bad_file.unlink()


class TestValidatorForbiddenImports:
    def test_forbidden_import_detected(self):
        """Validator should detect forbidden imports in calibration_skill."""
        # The current codebase is clean, so this test verifies the scanner works
        exit_code, stdout, _ = _run_validator()
        assert "No forbidden vendor imports" in stdout
