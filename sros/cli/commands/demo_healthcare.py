"""SROS Demo - Healthcare Triage with HIPAA-Aligned Access Control."""

import typer
from .. import demo_utils
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    srxml_path, receipt_path = demo_utils.resolve_demo_paths("healthcare_triage")
    
    demo_utils.print_banner(
        "Healthcare Triage Demo",
        "Healthcare",
        "HIPAA-Aligned Access Control (PHI)"
    )

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["patient_name", "dob", "mrn", "diagnosis_history"]},
        "step1": {
            "action": "classify_symptom_severity",
            "resource": "patient_records/v4",
            "requested_fields": ["name", "vital_signs", "symptoms"],
            "output": "Severity classification: moderate. Elevated HR (102).",
            "drift": 0.05,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "phi_access_restriction",
                "risk_level": "medium",
                "reason": "Patient data access requested. Identity fields (PHI) blocked.",
                "conditions": ["Patient name denied", "DOB denied", "MRN denied"]
            }
        },
        "step2": {
            "action": "generate_triage_score",
            "resource": "triage_algorithm/v2",
            "requested_fields": ["vital_signs", "diagnosis_history"],
            "output": "Triage priority: 2. Recommend cardiac evaluation within 1 hr.",
            "drift": 0.12,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "diagnosis_history_restriction",
                "risk_level": "medium",
                "reason": "Diagnosis history access blocked to prevent diagnostic bias.",
                "conditions": ["Diagnosis history access denied"]
            }
        },
        "step3": {
            "action": "audit_phi_access",
            "resource": "compliance_store/hipaa",
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

    ui = {
        "step": demo_utils.print_step,
        "verdict": demo_utils.print_verdict,
        "drift": demo_utils.print_drift
    }

    runner = GoverningWorkflowRunner(policies, metadata, ui_handlers=ui)
    receipt = runner.run(str(srxml_path), str(receipt_path))

    demo_utils.print_footer(receipt, receipt_path)
