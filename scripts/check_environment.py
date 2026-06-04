"""Check local environment for K1 measurement development."""

from __future__ import annotations

import importlib.util
import shutil
import sys


DEPENDENCIES = ["numpy", "pandas", "matplotlib", "yaml", "scipy", "pytest", "jsonschema"]


def dependency_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    for dependency in DEPENDENCIES:
        print(f"{dependency}: {'available' if dependency_available(dependency) else 'missing'}")
    print(f"ros2 command: {'available' if shutil.which('ros2') else 'missing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
