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

    policies = [
        {
            "name": "healthcare_policy",
            "rules": [
                {
                    "id": "hc-1",
                    "priority": 10,
                    "action": "classify_symptom_severity",
                    "resource": "patient_records/v4",
                    "effect": "allow_with_conditions",
                    "reason": "Patient data access requested. Identity fields (PHI) blocked.",
                    "risk_level": "medium",
                    "conditions": ["Patient name denied", "DOB denied", "MRN denied"]
                },
                {
                    "id": "hc-2",
                    "priority": 20,
                    "action": "generate_triage_score",
                    "resource": "triage_algorithm/v2",
                    "requested_fields_all": ["diagnosis_history"],
                    "effect": "allow_with_conditions",
                    "reason": "Diagnosis history access blocked to prevent diagnostic bias.",
                    "risk_level": "medium",
                    "conditions": ["Diagnosis history access denied"]
                },
                {
                    "id": "hc-3",
                    "priority": 30,
                    "action": "audit_phi_access",
                    "resource": "compliance_store/hipaa",
                    "effect": "allow",
                    "reason": "Compliance audit operation. Read-only.",
                    "risk_level": "low"
                }
            ]
        }
    ]
    
    metadata = {
        "_global": {"domain_blocked": ["patient_name", "dob", "mrn", "diagnosis_history"]},
        "step1": {
            "action": "classify_symptom_severity",
            "resource": "patient_records/v4",
            "requested_fields": ["name", "vital_signs", "symptoms"],
            "output": "Severity classification: moderate. Elevated HR (102).",
            "drift": 0.05,
        },
        "step2": {
            "action": "generate_triage_score",
            "resource": "triage_algorithm/v2",
            "requested_fields": ["vital_signs", "diagnosis_history"],
            "output": "Triage priority: 2. Recommend cardiac evaluation within 1 hr.",
            "drift": 0.12,
        },
        "step3": {
            "action": "audit_phi_access",
            "resource": "compliance_store/hipaa",
            "output": "HIPAA compliance check passed. 0 unauthorized PHI accesses detected.",
            "drift": 0.03,
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
