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

    policies = [
        {
            "name": "fintech_policy",
            "rules": [
                {
                    "id": "ft-1",
                    "priority": 10,
                    "action": "classify_pii_fields",
                    "resource": "customer_db/schema",
                    "effect": "allow",
                    "reason": "Schema inspection is read-only. No PII data records accessed.",
                    "risk_level": "low"
                },
                {
                    "id": "ft-2",
                    "priority": 20,
                    "action": "generate_credit_score",
                    "resource": "credit_engine/v1",
                    "requested_fields_all": ["SSN"],
                    "effect": "allow_with_conditions",
                    "reason": "PII fields (SSN, raw_income) blocked by recursive policy.",
                    "risk_level": "medium",
                    "conditions": ["SSN field access denied", "raw_income field access denied"]
                },
                {
                    "id": "ft-3",
                    "priority": 30,
                    "action": "validate_field_access_compliance",
                    "resource": "audit_logs/v1",
                    "effect": "allow",
                    "reason": "Compliance audit is a read-only validation operation.",
                    "risk_level": "low"
                }
            ]
        }
    ]
    
    metadata = {
        "_global": {"domain_blocked": ["SSN", "raw_income"]},
        "step1": {
            "action": "classify_pii_fields",
            "resource": "customer_db/schema",
            "requested_fields": ["id", "SSN", "income", "debt_ratio"],
            "output": "Fields classified. PII restricted: SSN, raw_income. Safe: debt_to_income_ratio",
            "drift": 0.01,
        },
        "step2": {
            "action": "generate_credit_score",
            "resource": "credit_engine/v1",
            "requested_fields": ["SSN", "income", "debt_ratio"],
            "output": "Credit risk score: 720. Based on debt_to_income_ratio (0.32).",
            "drift": 0.08,
        },
        "step3": {
            "action": "validate_field_access_compliance",
            "resource": "audit_logs/v1",
            "output": "Compliance check passed. 0 restricted field accesses detected in tracer.",
            "drift": 0.02,
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
