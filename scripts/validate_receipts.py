#!/usr/bin/env python3
"""Validate baseline receipt schema for committed demo receipts."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"


REQUIRED_TOP_LEVEL = ["workflow_id", "run_id", "receipt_chain", "steps", "status"]
REQUIRED_CHAIN = ["chain_hash", "step_hashes"]


def validate_receipt(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"missing top-level key '{key}'")

    chain = data.get("receipt_chain", {})
    for key in REQUIRED_CHAIN:
        if key not in chain:
            errors.append(f"missing receipt_chain key '{key}'")

    if not isinstance(data.get("steps"), list):
        errors.append("'steps' must be a list")

    return errors


def main() -> int:
    json_files = sorted(RECEIPTS.glob("*_receipt.json"))
    if not json_files:
        print("No receipt files found.")
        return 1

    failed = False
    for file_path in json_files:
        errors = validate_receipt(file_path)
        if errors:
            failed = True
            print(f"FAIL {file_path}:")
            for err in errors:
                print(f"- {err}")
        else:
            print(f"OK {file_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
