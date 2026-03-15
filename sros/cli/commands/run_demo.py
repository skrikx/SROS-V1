"""SROS Demo - Governance Receipt Demo."""

import typer
from pathlib import Path
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    print("=" * 60)
    print("  SROS v1 - Governance Receipt Demo")
    print("=" * 60)

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "step1": {
            "action": "analyze_requirements",
            "output": "Architecture meets separation-of-concerns requirements. Proceed.",
            "drift": 0.02,
            "governance": {
                "verdict": "allow",
                "policy_name": "default_allow_read_operations",
                "risk_level": "low",
                "reason": "Read-only analysis operation."
            }
        },
        "step2": {
            "action": "propose_code_change",
            "output": "Proposal generated: 12 lines added to payment_handler.py.",
            "drift": 0.15,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "code_mutation_governance",
                "risk_level": "medium",
                "reason": "Code mutation proposed. Conditionally allowed.",
                "conditions": ["Max 50-line diff enforced", "Must pass test suite"]
            }
        },
        "step3": {
            "action": "generate_validation_tests",
            "output": "Generated 4 test cases covering validation and logging.",
            "drift": 0.04,
            "governance": {
                "verdict": "allow",
                "policy_name": "test_generation_policy",
                "risk_level": "low",
                "reason": "Test generation is a read-and-write-test operation."
            }
        }
    }

    runner = GoverningWorkflowRunner(policies, metadata)
    srxml_path = str(Path("examples/governance_demo.srxml").resolve())
    receipt_dir = Path("receipts")
    receipt_dir.mkdir(exist_ok=True)
    receipt_path = receipt_dir / "demo_receipt.json"

    receipt = runner.run(srxml_path, str(receipt_path))

    print("\n" + "=" * 60)
    print("  Demo Complete")
    print("=" * 60)
    print(f"\n  Status:  {receipt['status']}")
    print(f"  Steps:   {receipt['total_steps']}")
    print(f"  Verdicts: {receipt['governance_summary']['verdicts']}")
    print(f"  Drift:   None detected (max score: {receipt['mirror_summary']['max_drift_score']})")
    print(f"\n  Receipt written to: {receipt_path.resolve()}")
    print(f"  Chain hash: {receipt['receipt_chain']['chain_hash']}\n")
