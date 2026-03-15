"""SROS Demo - Fintech Loan Review with PII Governance."""

import typer
from .. import demo_utils
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    srxml_path, receipt_path = demo_utils.resolve_demo_paths("fintech_loan_review")
    
    demo_utils.print_banner(
        "Fintech Loan Review Demo",
        "Financial Services",
        "PII Field Restriction (Fair Lending)"
    )

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["SSN", "raw_income"]},
        "step1": {
            "action": "classify_pii_fields",
            "resource": "customer_db/schema",
            "requested_fields": ["id", "SSN", "income", "debt_ratio"],
            "output": "Fields classified. PII restricted: SSN, raw_income. Safe: debt_to_income_ratio",
            "drift": 0.01,
            "governance": {
                "verdict": "allow",
                "policy_name": "pii_classification_read_only",
                "risk_level": "low",
                "reason": "Schema inspection is read-only. No PII data records accessed."
            }
        },
        "step2": {
            "action": "generate_credit_score",
            "resource": "credit_engine/v1",
            "requested_fields": ["SSN", "income", "debt_ratio"],
            "output": "Credit risk score: 720. Based on debt_to_income_ratio (0.32).",
            "drift": 0.08,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "pii_access_restriction",
                "risk_level": "medium",
                "reason": "PII fields (SSN, raw_income) blocked by recursive policy.",
                "conditions": ["SSN field access denied", "raw_income field access denied"]
            }
        },
        "step3": {
            "action": "validate_field_access_compliance",
            "resource": "audit_logs/v1",
            "output": "Compliance check passed. 0 restricted field accesses detected in tracer.",
            "drift": 0.02,
            "governance": {
                "verdict": "allow",
                "policy_name": "compliance_audit_policy",
                "risk_level": "low",
                "reason": "Compliance audit is a read-only validation operation."
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
