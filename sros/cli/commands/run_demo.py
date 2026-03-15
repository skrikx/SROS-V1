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

    policies = [
        {
            "name": "governance_demo_policy",
            "rules": [
                {
                    "id": "gd-1",
                    "priority": 10,
                    "action": "analyze_requirements",
                    "effect": "allow",
                    "reason": "Read-only analysis operation on public requirements.",
                    "risk_level": "low"
                },
                {
                    "id": "gd-2",
                    "priority": 20,
                    "action": "propose_code_change",
                    "effect": "allow_with_conditions",
                    "reason": "Code mutation proposed to payment module.",
                    "risk_level": "medium",
                    "conditions": ["Max 50-line diff enforced", "Must pass test suite before commit"]
                },
                {
                    "id": "gd-3",
                    "priority": 30,
                    "action": "generate_validation_tests",
                    "effect": "allow",
                    "reason": "Test generation is a permitted write operation to the test plane.",
                    "risk_level": "low"
                }
            ]
        }
    ]
    
    metadata = {
        "step1": {
            "action": "analyze_requirements",
            "resource": "doc_store/requirements.txt",
            "output": "Architecture meets separation-of-concerns requirements. Proceed.",
            "drift": 0.02,
        },
        "step2": {
            "action": "propose_code_change",
            "resource": "src/payment_handler.py",
            "output": "Proposal generated: 12 lines added to payment_handler.py.",
            "drift": 0.15,
        },
        "step3": {
            "action": "generate_validation_tests",
            "resource": "tests/test_payments.py",
            "output": "Generated 4 test cases covering validation and logging.",
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
