"""Receipt schema validation helpers."""

import json
from pathlib import Path
from typing import Any, Dict

RECEIPT_SCHEMA_VERSION = "1.0.0"
_SCHEMA_PATH = Path(__file__).with_name("receipt_schema.json")
RECEIPT_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_receipt(receipt: Dict[str, Any]) -> None:
    """Validate receipt against the canonical schema."""
    required = RECEIPT_SCHEMA["required"]
    for key in required:
        if key not in receipt:
            raise ValueError(f"Receipt missing required field: {key}")

    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise ValueError("Receipt schema_version mismatch")

    chain = receipt.get("receipt_chain", {})
    if "step_hashes" not in chain or "chain_hash" not in chain:
        raise ValueError("Receipt chain fields are required")

    if receipt.get("trace_count") != receipt.get("mirror_summary", {}).get("total_traces"):
        raise ValueError("trace_count must match mirror_summary.total_traces")
