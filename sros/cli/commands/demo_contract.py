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

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "_global": {"domain_blocked": ["full_clause_text"]},
        "step1": {
            "action": "analyze_contract_structure",
            "resource": "legal_drive/contract_442.pdf",
            "output": "Contract structure analyzed. 4 clause categories identified.",
            "drift": 0.03,
            "governance": {
                "verdict": "allow",
                "policy_name": "document_read_only_policy",
                "risk_level": "low",
                "reason": "Document structure analysis is a metadata-only read operation."
            }
        },
        "step2": {
            "action": "extract_risk_clauses",
            "resource": "legal_drive/contract_442.pdf",
            "requested_fields": ["indemnity", "termination", "liability"],
            "output": "Extracted 8 clause summaries. Full text retained in governed environment.",
            "drift": 0.22,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "data_exfiltration_prevention",
                "risk_level": "high",
                "reason": "Policy restricts output to summaries only to prevent data exfiltration.",
                "conditions": ["Full clause text export denied", "Summary-only output enforced"]
            }
        },
        "step3": {
            "action": "validate_output_compliance",
            "resource": "mirror_os/output_validator",
            "output": "Data governance check passed. No full text in output payload.",
            "drift": 0.04,
            "governance": {
                "verdict": "allow",
                "policy_name": "compliance_audit_policy",
                "risk_level": "low",
                "reason": "Output validation is a read-only compliance check."
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
