"""SROS Demo - Fintech Loan Review with PII Governance."""

import typer
from pathlib import Path
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    print("=" * 60)
    print("  SROS v1 - Fintech Loan Review Demo")
    print("  Domain: Financial Services | Governance: PII Restriction")
    print("=" * 60)

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["SSN", "raw_income"]},
        "step1": {
            "action": "classify_pii_fields",
            "output": "Fields classified. PII restricted: SSN, raw_income. Safe: debt_to_income_ratio",
            "drift": 0.01,
            "governance": {
                "verdict": "allow",
                "policy_name": "pii_classification_read_only",
                "risk_level": "low",
                "reason": "Schema inspection is read-only. No PII accessed."
            }
        },
        "step2": {
            "action": "generate_credit_score",
            "output": "Credit risk score: 720. Based on debt_to_income_ratio (0.32).",
            "drift": 0.08,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "pii_access_restriction",
                "risk_level": "medium",
                "reason": "PII fields (SSN, raw_income) blocked by policy.",
                "conditions": ["SSN field access denied", "raw_income field access denied"]
            }
        },
        "step3": {
            "action": "validate_field_access_compliance",
            "output": "Compliance check passed. 0 restricted field accesses detected.",
            "drift": 0.02,
            "governance": {
                "verdict": "allow",
                "policy_name": "compliance_audit_policy",
                "risk_level": "low",
                "reason": "Compliance audit is a read-only validation operation."
            }
        }
    }

    runner = GoverningWorkflowRunner(policies, metadata)
    srxml_path = str(Path("examples/fintech_loan_review.srxml").resolve())
    receipt_dir = Path("receipts")
    receipt_dir.mkdir(exist_ok=True)
    receipt_path = receipt_dir / "fintech_loan_review_receipt.json"

    receipt = runner.run(srxml_path, str(receipt_path))

    print("\n" + "=" * 60)
    print("  Fintech Demo Complete")
    print("=" * 60)
    print(f"\n  Status:       {receipt['status']}")
    print(f"  Steps:        {receipt['total_steps']}")
    print(f"  PII Blocked:  {receipt['governance_summary'].get('domain_blocked', [])}")
    print(f"  Verdicts:     {receipt['governance_summary']['verdicts']}")
    print(f"  Drift:        None detected (max: {receipt['mirror_summary']['max_drift_score']})")
    print(f"\n  Receipt: {receipt_path.resolve()}")
    print(f"  Chain:   {receipt['receipt_chain']['chain_hash']}\n")
