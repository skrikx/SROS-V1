"""SROS Demo - Contract Review with Data Exfiltration Prevention."""

import typer
from .. import demo_utils
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    srxml_path, receipt_path = demo_utils.resolve_demo_paths("contract_review")
    
    demo_utils.print_banner(
        "Contract Review Demo",
        "Legal / Compliance",
        "Data Exfiltration Prevention (Summary-Only)"
    )

    policies = [
        {
            "name": "contract_policy",
            "rules": [
                {
                    "id": "ct-1",
                    "priority": 10,
                    "action": "analyze_contract_structure",
                    "resource": "legal_drive/contract_442.pdf",
                    "effect": "allow",
                    "reason": "Document structure analysis is a metadata-only read operation.",
                    "risk_level": "low"
                },
                {
                    "id": "ct-2",
                    "priority": 20,
                    "action": "extract_risk_clauses",
                    "resource": "legal_drive/contract_442.pdf",
                    "effect": "allow_with_conditions",
                    "reason": "Policy restricts output to summaries only to prevent data exfiltration.",
                    "risk_level": "high",
                    "conditions": ["Full clause text export denied", "Summary-only output enforced"]
                },
                {
                    "id": "ct-3",
                    "priority": 30,
                    "action": "validate_output_compliance",
                    "resource": "mirror_os/output_validator",
                    "effect": "allow",
                    "reason": "Output validation is a read-only compliance check.",
                    "risk_level": "low"
                }
            ]
        }
    ]
    
    metadata = {
        "_global": {"domain_blocked": ["full_clause_text"]},
        "step1": {
            "action": "analyze_contract_structure",
            "resource": "legal_drive/contract_442.pdf",
            "output": "Contract structure analyzed. 4 clause categories identified.",
            "drift": 0.03,
        },
        "step2": {
            "action": "extract_risk_clauses",
            "resource": "legal_drive/contract_442.pdf",
            "requested_fields": ["indemnity", "termination", "liability"],
            "output": "Extracted 8 clause summaries. Full text retained in governed environment.",
            "drift": 0.22,
        },
        "step3": {
            "action": "validate_output_compliance",
            "resource": "mirror_os/output_validator",
            "output": "Data governance check passed. No full text in output payload.",
            "drift": 0.04,
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
