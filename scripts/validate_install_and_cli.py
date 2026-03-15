#!/usr/bin/env python3
"""Validate installed package import and CLI availability."""

import subprocess
import sys


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)


def main() -> int:
    run([sys.executable, "-c", "import sros; print(sros.__version__)"])
    run(["sros", "--help"])
    print("Import and CLI checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
