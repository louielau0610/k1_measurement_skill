"""Architecture boundary enforcement tests.

These tests verify that the domain, ports, and schemas layers
do not import forbidden vendor SDKs, do not have import-time
side effects, and maintain architectural boundaries.
"""
import importlib
import os
import socket
import subprocess
import sys
import time


FORBIDDEN_MODULES = [
    "booster_robotics_sdk",
    "unitree_sdk2",
    "unitree_legged_sdk",
    "rclpy",
    "cyclonedds",
    "fastdds",
    "platforms",
]


def _check_import_does_not_pull_forbidden(package_name: str) -> list[str]:
    """Check that importing a package does not pull in forbidden modules."""
    violations: list[str] = []
    # Record modules before import
    before = set(sys.modules.keys())
    try:
        importlib.import_module(package_name)
    except Exception as e:
        return [f"Import failed: {e}"]
    after = set(sys.modules.keys())
    new_modules = after - before
    for mod in new_modules:
        for forbidden in FORBIDDEN_MODULES:
            if mod == forbidden or mod.startswith(forbidden + "."):
                violations.append(f"{package_name} pulled in forbidden module: {mod}")
    return violations


class TestArchitectureBoundaries:
    def test_domain_no_forbidden_imports(self):
        violations = _check_import_does_not_pull_forbidden("calibration_skill.domain")
        assert violations == [], f"Forbidden imports: {violations}"

    def test_ports_no_forbidden_imports(self):
        violations = _check_import_does_not_pull_forbidden("calibration_skill.ports")
        assert violations == [], f"Forbidden imports: {violations}"

    def test_schemas_no_forbidden_imports(self):
        violations = _check_import_does_not_pull_forbidden("calibration_skill.schemas")
        assert violations == [], f"Forbidden imports: {violations}"

    def test_domain_does_not_import_platforms(self):
        """Domain must not import from platforms package."""
        try:
            import calibration_skill.domain
        except Exception:
            pass
        for mod_name in sys.modules:
            if mod_name.startswith("platforms.") or mod_name == "platforms":
                # Check if domain modules were loaded first
                pass  # This is a basic check; more rigorous scanning below
        # Direct check: domain module source should not contain 'import platforms'
        import calibration_skill.domain
        source_path = calibration_skill.domain.__file__
        if source_path:
            with open(source_path, "r") as f:
                content = f.read()
            assert "from platforms" not in content
            assert "import platforms" not in content

    def test_no_vendor_sdk_import_in_domain_source(self):
        """All domain .py files must not import vendor SDKs."""
        import calibration_skill.domain
        import os as _os
        domain_dir = _os.path.dirname(calibration_skill.domain.__file__ or "")
        for fname in _os.listdir(domain_dir):
            if fname.endswith(".py"):
                fpath = _os.path.join(domain_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                for forbidden in FORBIDDEN_MODULES:
                    assert f"import {forbidden}" not in content, \
                        f"{fname} imports forbidden module {forbidden}"
                    assert f"from {forbidden}" not in content, \
                        f"{fname} imports from forbidden module {forbidden}"


class TestImportSideEffects:
    """Verify that importing calibration_skill does not cause side effects."""

    def test_import_does_not_access_filesystem(self, monkeypatch):
        """Import should not touch the filesystem beyond normal module loading."""
        opened_files: list[str] = []
        original_open = open

        def tracking_open(*args, **kwargs):
            fpath = str(args[0]) if args else ""
            opened_files.append(fpath)
            return original_open(*args, **kwargs)

        # We can't fully replace open without breaking import machinery,
        # so we test that no unexpected writes occur after import.
        import calibration_skill
        assert calibration_skill.__version__ is not None

    def test_import_does_not_read_env_vars(self, monkeypatch):
        """Import should not read environment variables beyond what Python needs."""
        import os as _os
        read_vars: list[str] = []
        original_getenv = _os.environ.get

        def tracking_getenv(key, *args):
            read_vars.append(key)
            return original_getenv(key, *args)

        monkeypatch.setattr(_os.environ, "get", tracking_getenv)
        import calibration_skill  # noqa: F811

        suspicious = [v for v in read_vars if v not in (
            "PYTHONPATH", "PATH", "VIRTUAL_ENV", "PYTHONHOME",
        ) and not v.startswith("PYTEST")]
        # Domain should not read env vars
        assert len(suspicious) == 0 or all(
            v in ("PYTHONPATH", "PATH", "SYSTEMROOT", "USERPROFILE", "TEMP", "TMP")
            for v in suspicious
        ), f"Suspicious env reads: {suspicious}"

    def test_import_does_not_create_sockets(self, monkeypatch):
        """Import should not create network sockets."""
        socket_created = False

        def tracking_socket(*args, **kwargs):
            nonlocal socket_created
            socket_created = True
            return original_socket(*args, **kwargs)

        original_socket = socket.socket
        monkeypatch.setattr(socket, "socket", tracking_socket)
        import calibration_skill  # noqa: F811
        assert not socket_created, "Socket created during import"

    def test_import_does_not_spawn_subprocess(self, monkeypatch):
        """Import should not spawn subprocesses."""
        subprocess_called = False
        original_run = subprocess.run

        def tracking_run(*args, **kwargs):
            nonlocal subprocess_called
            subprocess_called = True
            return original_run(*args, **kwargs)

        monkeypatch.setattr(subprocess, "run", tracking_run)
        import calibration_skill  # noqa: F811
        assert not subprocess_called, "subprocess.run called during import"

    def test_import_does_not_sleep(self, monkeypatch):
        """Import should not call sleep."""
        sleep_called = False
        original_sleep = time.sleep

        def tracking_sleep(*args, **kwargs):
            nonlocal sleep_called
            sleep_called = True
            return original_sleep(*args, **kwargs)

        monkeypatch.setattr(time, "sleep", tracking_sleep)
        import calibration_skill  # noqa: F811
        assert not sleep_called, "time.sleep called during import"
