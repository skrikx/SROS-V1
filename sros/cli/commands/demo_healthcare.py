"""SROS Demo - Healthcare Triage with HIPAA-Aligned Access Control."""

import typer
from pathlib import Path
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    print("=" * 60)
    print("  SROS v1 - Healthcare Triage Demo")
    print("  Domain: Healthcare | Governance: HIPAA Access Control")
    print("=" * 60)

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["patient_name", "dob", "mrn", "diagnosis_history"]},
        "step1": {
            "action": "classify_symptom_severity",
            "output": "Severity classification: moderate. Elevated HR (102).",
            "drift": 0.05,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "phi_access_restriction",
                "risk_level": "medium",
                "reason": "Patient data access requested. Identity fields blocked.",
                "conditions": ["Patient name denied", "DOB denied", "MRN denied"]
            }
        },
        "step2": {
            "action": "generate_triage_score",
            "output": "Triage priority: 2. Recommend cardiac evaluation within 1 hr.",
            "drift": 0.12,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "diagnosis_history_restriction",
                "risk_level": "medium",
                "reason": "Diagnosis history access blocked to prevent bias.",
                "conditions": ["diagnosis_history access denied"]
            }
        },
        "step3": {
            "action": "audit_phi_access",
            "output": "HIPAA compliance check passed. 0 unauthorized PHI accesses detected.",
            "drift": 0.03,
            "governance": {
                "verdict": "allow",
                "policy_name": "compliance_audit_policy",
                "risk_level": "low",
                "reason": "Compliance audit operation. Read-only."
            }
        }
    }

    runner = GoverningWorkflowRunner(policies, metadata)
    srxml_path = str(Path("examples/healthcare_triage.srxml").resolve())
    receipt_dir = Path("receipts")
    receipt_dir.mkdir(exist_ok=True)
    receipt_path = receipt_dir / "healthcare_triage_receipt.json"

    receipt = runner.run(srxml_path, str(receipt_path))

    print("\n" + "=" * 60)
    print("  Healthcare Demo Complete")
    print("=" * 60)
    print(f"\n  Status:        {receipt['status']}")
    print(f"  Steps:         {receipt['total_steps']}")
    print(f"  PHI Blocked:   {receipt['governance_summary'].get('domain_blocked', [])}")
    print(f"  Verdicts:      {receipt['governance_summary']['verdicts']}")
    print(f"  Drift:         None detected (max: {receipt['mirror_summary']['max_drift_score']})")
    print(f"\n  Receipt: {receipt_path.resolve()}")
    print(f"  Chain:   {receipt['receipt_chain']['chain_hash']}\n")
