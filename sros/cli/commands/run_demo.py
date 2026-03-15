"""SROS Demo - Governance Receipt Demo."""

import typer
from .. import demo_utils
from ...runtime.governing_runner import GoverningWorkflowRunner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    srxml_path, receipt_path = demo_utils.resolve_demo_paths("governance_demo")
    
    demo_utils.print_banner(
        "Governance Receipt Demo",
        "General Systems",
        "Recursive Policy Evaluation"
    )

    policies = [{"effect": "allow", "name": "base_allow"}]
    
    metadata = {
        "step1": {
            "action": "analyze_requirements",
            "resource": "doc_store/requirements.txt",
            "output": "Architecture meets separation-of-concerns requirements. Proceed.",
            "drift": 0.02,
            "governance": {
                "verdict": "allow",
                "policy_name": "default_allow_read_operations",
                "risk_level": "low",
                "reason": "Read-only analysis operation on public requirements."
            }
        },
        "step2": {
            "action": "propose_code_change",
            "resource": "src/payment_handler.py",
            "output": "Proposal generated: 12 lines added to payment_handler.py.",
            "drift": 0.15,
            "governance": {
                "verdict": "allow_with_conditions",
                "policy_name": "code_mutation_governance",
                "risk_level": "medium",
                "reason": "Code mutation proposed to payment module.",
                "conditions": ["Max 50-line diff enforced", "Must pass test suite before commit"]
            }
        },
        "step3": {
            "action": "generate_validation_tests",
            "resource": "tests/test_payments.py",
            "output": "Generated 4 test cases covering validation and logging.",
            "drift": 0.04,
            "governance": {
                "verdict": "allow",
                "policy_name": "test_generation_policy",
                "risk_level": "low",
                "reason": "Test generation is a permitted write operation to the test plane."
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
