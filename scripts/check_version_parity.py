#!/usr/bin/env python3
"""Enforce version parity across release-critical files."""

from pathlib import Path
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pyproject_version = pyproject["project"]["version"]

    sys.path.insert(0, str(ROOT))
    from sros import __version__ as package_version  # pylint: disable=import-outside-toplevel

    versions = {
        "VERSION": version_file,
        "pyproject.toml": pyproject_version,
        "sros.__version__": package_version,
    }

    unique = set(versions.values())
    if len(unique) != 1:
        print("Version mismatch detected:")
        for key, value in versions.items():
            print(f"- {key}: {value}")
        return 1

    print(f"Version parity OK: {unique.pop()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
