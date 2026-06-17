"""Hermetic test runner behavior tests."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_tests_hermetically.py"


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "tracked.txt").write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True)


def copy_runner(tmp_path: Path) -> Path:
    target = tmp_path / "run_tests_hermetically.py"
    shutil.copy2(RUNNER, target)
    subprocess.run(["git", "add", target.name], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "add runner"], cwd=tmp_path, check=True, capture_output=True)
    return target


def run_runner(repo: Path, runner: Path, *command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(runner), "--json", "--", *command],
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=30,
    )


def test_clean_pass(tmp_path):
    init_repo(tmp_path)
    runner = copy_runner(tmp_path)
    result = run_runner(tmp_path, runner, sys.executable, "-c", "print('ok')")
    summary = json.loads(result.stdout)
    assert result.returncode == 0
    assert summary["child_returncode"] == 0
    assert summary["repository_mutated"] is False


def test_initially_dirty_fails(tmp_path):
    init_repo(tmp_path)
    runner = copy_runner(tmp_path)
    (tmp_path / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    result = run_runner(tmp_path, runner, sys.executable, "-c", "print('should not run')")
    summary = json.loads(result.stdout)
    assert result.returncode == 2
    assert summary["child_returncode"] is None


def test_mutation_fails_without_auto_restore(tmp_path):
    init_repo(tmp_path)
    runner = copy_runner(tmp_path)
    result = run_runner(tmp_path, runner, sys.executable, "-c", "open('created.txt','w').write('x')")
    summary = json.loads(result.stdout)
    assert result.returncode == 3
    assert summary["repository_mutated"] is True
    assert (tmp_path / "created.txt").exists()


def test_child_failure_fails(tmp_path):
    init_repo(tmp_path)
    runner = copy_runner(tmp_path)
    result = run_runner(tmp_path, runner, sys.executable, "-c", "raise SystemExit(7)")
    summary = json.loads(result.stdout)
    assert result.returncode == 1
    assert summary["child_returncode"] == 7


def test_runner_source_contains_no_restore_commands():
    text = RUNNER.read_text(encoding="utf-8")
    forbidden = ('["git", "checkout"', '["git", "restore"', '["git", "reset"', '["git", "clean"')
    assert not any(command in text for command in forbidden)
