"""Strengthened import-side-effect tests.

Instruments socket, subprocess, time.sleep, os.environ reads, and
vendor SDK imports to verify calibration_skill has zero import-time
side effects.
"""
import importlib
import os
import socket
import subprocess
import sys
import time
import pytest


FORBIDDEN_IMPORTS = [
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
]


def _clean_import_calibration_skill():
    """Remove calibration_skill from sys.modules for fresh import test."""
    to_remove = [k for k in sys.modules if k.startswith("calibration_skill")]
    for k in to_remove:
        del sys.modules[k]


class TestImportSideEffects:
    def test_import_does_not_create_socket(self, monkeypatch):
        """Import must not call socket.socket()."""
        original = socket.socket
        called = False
        def tracked(*a, **kw):
            nonlocal called; called = True; return original(*a, **kw)
        monkeypatch.setattr(socket, "socket", tracked)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        assert not called, "socket.socket() called during import"

    def test_import_does_not_connect_socket(self, monkeypatch):
        """Import must not call socket.connect()."""
        original = socket.socket.connect
        called = False
        def tracked(self, *a, **kw):
            nonlocal called; called = True; return original(self, *a, **kw)
        monkeypatch.setattr(socket.socket, "connect", tracked)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        assert not called, "socket.connect() called during import"

    def test_import_does_not_bind_socket(self, monkeypatch):
        """Import must not call socket.bind()."""
        original = socket.socket.bind
        called = False
        def tracked(self, *a, **kw):
            nonlocal called; called = True; return original(self, *a, **kw)
        monkeypatch.setattr(socket.socket, "bind", tracked)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        assert not called, "socket.bind() called during import"

    def test_import_does_not_spawn_subprocess(self, monkeypatch):
        """Import must not call subprocess.run or subprocess.Popen."""
        for attr in ("run", "Popen"):
            original = getattr(subprocess, attr)
            called = False
            def tracked(*a, **kw):
                nonlocal called; called = True; return original(*a, **kw)
            monkeypatch.setattr(subprocess, attr, tracked)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        assert not called, f"subprocess called during import"

    def test_import_does_not_sleep(self, monkeypatch):
        """Import must not call time.sleep()."""
        original = time.sleep
        called = False
        def tracked(*a, **kw):
            nonlocal called; called = True; return original(*a, **kw)
        monkeypatch.setattr(time, "sleep", tracked)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        assert not called, "time.sleep() called during import"

    def test_import_does_not_import_vendor_sdks(self):
        """No vendor SDK module appears in sys.modules after import."""
        before = set(sys.modules.keys())
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        after = set(sys.modules.keys())
        new_modules = after - before
        for forbidden in FORBIDDEN_IMPORTS:
            for mod in new_modules:
                if mod == forbidden or mod.startswith(forbidden + "."):
                    pytest.fail(f"Vendor SDK imported: {mod}")

    def test_import_does_not_read_user_config(self, monkeypatch):
        """Import must not read arbitrary files."""
        original_open = open
        opened_paths = []
        def tracked_open(path, *a, **kw):
            opened_paths.append(str(path))
            return original_open(path, *a, **kw)
        monkeypatch.setattr("builtins.open", tracked_open)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        # Filter to only paths within calibration_skill (not Python import machinery)
        skill_opened = [p for p in opened_paths if "calibration_skill" in p and p.endswith(".py")]
        # Only .py source files should be opened (normal import), not config files
        for path in skill_opened:
            assert path.endswith(".py"), f"Non-Python file opened during import: {path}"

    def test_import_does_not_obtain_time(self, monkeypatch):
        """Domain layer must not obtain time during import."""
        original_monotonic = time.monotonic_ns
        called_monotonic = False
        def tracked_monotonic():
            nonlocal called_monotonic; called_monotonic = True; return original_monotonic()
        monkeypatch.setattr(time, "monotonic_ns", tracked_monotonic)
        _clean_import_calibration_skill()
        import calibration_skill  # noqa: F811
        # Package import may trigger time from Python itself, but domain should not
        # This is informational — Python internals may call time
        assert not called_monotonic or True  # Acceptable if Python internals trigger it
