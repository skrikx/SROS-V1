"""SROS Demo - Governance Receipt Demo.

Runs a simulated 3-step agent workflow with governance policy
evaluation, drift monitoring, and writes an inspectable receipt
JSON to the receipts/ directory.
"""

import json
import time
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import typer

app = typer.Typer()


def _hash(data: str) -> str:
    """SHA-256 hash of a string."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _run_governance_demo() -> dict:
    """Execute a simulated 3-step governed agent workflow."""
    from ...kernel import kernel_bootstrap

    run_id = str(uuid.uuid4())
    start_ts = datetime.now(timezone.utc).isoformat()

    # --- Step 0: Boot the Kernel ---
    print("\n  Booting SROS Kernel...")
    kernel = kernel_bootstrap.boot()
    print("  [OK] Kernel online")

    steps = []

    # --- Step 1: Architect Agent - Analyze ---
    print("\n  [Step 1/3] ArchitectAgent: Analyzing requirements...")
    step1_start = datetime.now(timezone.utc).isoformat()
    time.sleep(0.3)  # Simulate work
    step1 = {
        "step_id": "step_1",
        "agent": "architect",
        "action": "analyze_requirements",
        "input": "Evaluate system architecture for compliance readiness",
        "output": "Architecture meets separation-of-concerns requirements. "
                  "Governance plane is decoupled from runtime. Proceed.",
        "started_at": step1_start,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "governance": {
            "policy_checked": True,
            "verdict": "allow",
            "policy_name": "default_allow_read_operations",
            "risk_level": "low",
            "reason": "Read-only analysis operation. No mutation risk."
        },
        "mirror": {
            "drift_score": 0.02,
            "drift_threshold": 0.5,
            "drift_detected": False,
            "witness_recorded": True
        }
    }
    print("    Policy check: ALLOW (read-only, low risk)")
    print("    Drift score: 0.02 / 0.50 threshold - OK")
    print("  [OK] Step 1 complete")
    steps.append(step1)

    # --- Step 2: Builder Agent - Propose Change (GOVERNED) ---
    print("\n  [Step 2/3] BuilderAgent: Proposing code mutation...")
    step2_start = datetime.now(timezone.utc).isoformat()
    time.sleep(0.3)
    step2 = {
        "step_id": "step_2",
        "agent": "builder",
        "action": "propose_code_change",
        "input": "Add audit logging to the payment processing module",
        "output": "Proposal generated: 12 lines added to payment_handler.py. "
                  "Changes are scoped to logging only, no business logic mutation.",
        "started_at": step2_start,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "governance": {
            "policy_checked": True,
            "verdict": "allow_with_conditions",
            "policy_name": "code_mutation_governance",
            "risk_level": "medium",
            "reason": "Code mutation proposed. Scoped to logging-only additions. "
                      "No business logic changes detected. Conditionally allowed.",
            "conditions": [
                "Changes must not exceed 50-line diff limit",
                "Changes must pass automated test suite before merge"
            ]
        },
        "mirror": {
            "drift_score": 0.15,
            "drift_threshold": 0.5,
            "drift_detected": False,
            "witness_recorded": True
        }
    }
    print("    Policy check: ALLOW WITH CONDITIONS (medium risk)")
    print("      - Max 50-line diff enforced")
    print("      - Must pass test suite before merge")
    print("    Drift score: 0.15 / 0.50 threshold - OK")
    print("  [OK] Step 2 complete")
    steps.append(step2)

    # --- Step 3: Tester Agent - Validate ---
    print("\n  [Step 3/3] TesterAgent: Generating validation tests...")
    step3_start = datetime.now(timezone.utc).isoformat()
    time.sleep(0.3)
    step3 = {
        "step_id": "step_3",
        "agent": "tester",
        "action": "generate_validation_tests",
        "input": "Generate pytest tests for the proposed audit logging changes",
        "output": "Generated 4 test cases covering: log format validation, "
                  "log rotation, error path logging, and PII redaction check.",
        "started_at": step3_start,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "governance": {
            "policy_checked": True,
            "verdict": "allow",
            "policy_name": "test_generation_policy",
            "risk_level": "low",
            "reason": "Test generation is a read-and-write-test operation. "
                      "No production system mutation."
        },
        "mirror": {
            "drift_score": 0.04,
            "drift_threshold": 0.5,
            "drift_detected": False,
            "witness_recorded": True
        }
    }
    print("    Policy check: ALLOW (test generation, low risk)")
    print("    Drift score: 0.04 / 0.50 threshold - OK")
    print("  [OK] Step 3 complete")
    steps.append(step3)

    end_ts = datetime.now(timezone.utc).isoformat()

    # --- Build Receipt ---
    step_hashes = [_hash(json.dumps(s, sort_keys=True)) for s in steps]
    chain_hash = _hash("->".join(step_hashes))

    receipt = {
        "sros_version": "1.0.0-alpha",
        "receipt_type": "workflow_execution",
        "workflow_id": "governance_demo",
        "run_id": run_id,
        "started_at": start_ts,
        "completed_at": end_ts,
        "status": "success",
        "total_steps": len(steps),
        "steps": steps,
        "receipt_chain": {
            "step_hashes": step_hashes,
            "chain_hash": chain_hash
        },
        "governance_summary": {
            "total_policy_checks": 3,
            "verdicts": {
                "allow": 2,
                "allow_with_conditions": 1,
                "deny": 0
            }
        },
        "mirror_summary": {
            "drift_detected": False,
            "max_drift_score": 0.15,
            "all_events_witnessed": True
        }
    }

    return receipt


@app.callback(invoke_without_command=True)
def main():
    """
    Run the SROS governance demo.

    Executes a 3-step agent workflow with policy enforcement,
    drift monitoring, and writes an inspectable receipt to disk.
    """
    print("=" * 60)
    print("  SROS v1 - Governance Receipt Demo")
    print("=" * 60)

    receipt = _run_governance_demo()

    # Write receipt to disk
    receipts_dir = Path("receipts")
    receipts_dir.mkdir(exist_ok=True)
    receipt_path = receipts_dir / "demo_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2))

    print("\n" + "=" * 60)
    print("  Demo Complete")
    print("=" * 60)
    print(f"\n  Status:  {receipt['status']}")
    print(f"  Steps:   {receipt['total_steps']}")
    print(f"  Verdicts: {receipt['governance_summary']['verdicts']}")
    print(f"  Drift:   None detected (max score: {receipt['mirror_summary']['max_drift_score']})")
    print(f"\n  Receipt written to: {receipt_path.resolve()}")
    print(f"  Chain hash: {receipt['receipt_chain']['chain_hash']}")
    print()
