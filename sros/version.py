"""Canonical SROS release version helpers."""

from pathlib import Path

_VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"


def get_release_version() -> str:
    """Return the canonical release identity from VERSION."""
    return _VERSION_FILE.read_text(encoding="utf-8").strip()


def get_package_version() -> str:
    """Return a packaging-safe version string."""
    return get_release_version().lstrip("v")
