"""SROS Demo - Contract Review with Data Exfiltration Prevention."""

import typer
from pathlib import Path
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    print("=" * 60)
    print("  SROS v1 - Contract Review Demo")
    print("  Domain: Legal | Governance: Data Exfiltration Prevention")
    print("=" * 60)

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["full_clause_text"]},
        "step1": {
            "action": "analyze_contract_structure",
            "output": "Contract structure analyzed. 4 clause categories identified.",
            "drift": 0.03,
            "governance": {
                "verdict": "allow",
                "policy_name": "document_read_only_policy",
                "risk_level": "low",
                "reason": "Document structure analysis is read-only."
            }
        },
        "step2": {
            "action": "extract_risk_clauses",
            "output": "Extracted 8 clause summaries. Full text retained in governed environment.",
            "drift": 0.22,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "data_exfiltration_prevention",
                "risk_level": "high",
                "reason": "Policy restricts output to summaries only.",
                "conditions": ["Full clause text export denied", "Summary-only output enforced"]
            }
        },
        "step3": {
            "action": "validate_output_compliance",
            "output": "Data governance check passed. No full text in output.",
            "drift": 0.04,
            "governance": {
                "verdict": "allow",
                "policy_name": "compliance_audit_policy",
                "risk_level": "low",
                "reason": "Output validation is a read-only compliance check."
            }
        }
    }

    runner = GoverningWorkflowRunner(policies, metadata)
    srxml_path = str(Path("examples/contract_review.srxml").resolve())
    receipt_dir = Path("receipts")
    receipt_dir.mkdir(exist_ok=True)
    receipt_path = receipt_dir / "contract_review_receipt.json"

    receipt = runner.run(srxml_path, str(receipt_path))

    print("\n" + "=" * 60)
    print("  Contract Review Demo Complete")
    print("=" * 60)
    print(f"\n  Status:          {receipt['status']}")
    print(f"  Steps:           {receipt['total_steps']}")
    print(f"  Data Blocked:    {receipt['governance_summary'].get('domain_blocked', [])}")
    print(f"  Verdicts:        {receipt['governance_summary']['verdicts']}")
    print(f"  Drift:           None detected (max: {receipt['mirror_summary']['max_drift_score']})")
    print(f"\n  Receipt: {receipt_path.resolve()}")
    print(f"  Chain:   {receipt['receipt_chain']['chain_hash']}\n")
