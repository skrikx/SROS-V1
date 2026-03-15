import json
from pathlib import Path

from typer.testing import CliRunner

from sros import __version__
from sros.cli.main import app
from sros.governance.policy_engine import PolicyEngine
from sros.runtime.governing_runner import GoverningWorkflowRunner
from sros.runtime.receipt_validator import validate_receipt
from sros.version import get_release_version


runner = CliRunner()


def test_release_version_is_canonical_v1():
    assert get_release_version() == "v1.0.0"
    assert __version__ == "v1.0.0"


def test_cli_help_surface_is_stable_five_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "run-demo" in result.output
    assert "demo-fintech" in result.output
    assert "demo-healthcare" in result.output
    assert "demo-contract" in result.output


def test_demo_command_fails_cleanly_when_asset_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["run-demo"])
    assert result.exit_code == 2
    assert "Missing required workflow asset" in result.output


def test_policy_engine_deterministic_resolution_and_default_deny():
    engine = PolicyEngine()
    engine.load_policy(
        {
            "name": "governance",
            "rules": [
                {"id": "r3", "priority": 30, "action": "read", "effect": "allow", "reason": "generic", "risk_level": "low"},
                {"id": "r1", "priority": 10, "action": "read", "resource": "secret", "effect": "deny", "reason": "blocked", "risk_level": "high"},
                {"id": "r2", "priority": 20, "action": "read", "resource": "secret", "requested_fields_all": ["name"], "effect": "allow_with_conditions", "reason": "masked", "risk_level": "medium", "conditions": ["mask pii"]},
            ],
        }
    )

    denied = engine.evaluate("read", {"resource": "secret"})
    assert denied.verdict == "deny"
    assert denied.matched_rule_id == "r1"

    denied_with_field = engine.evaluate("read", {"resource": "secret", "requested_fields": ["name"]})
    assert denied_with_field.verdict == "deny"
    assert denied_with_field.matched_rule_id == "r1"

    allowed = engine.evaluate("read", {"resource": "public"})
    assert allowed.verdict == "allow"
    assert allowed.matched_rule_id == "r3"

    default_deny = engine.evaluate("write", {"resource": "public"})
    assert default_deny.allowed is False
    assert default_deny.verdict == "deny"


def test_governing_runner_derives_governance_from_engine(tmp_path):
    workflow = tmp_path / "workflow.srxml"
    workflow.write_text(
        """<workflow id=\"wf\"><step id=\"step1\" agent=\"architect\"><instruction>a</instruction></step><step id=\"step2\" agent=\"builder\"><instruction>b</instruction></step></workflow>""",
        encoding="utf-8",
    )
    receipt_path = tmp_path / "receipt.json"

    policies = [
        {
            "name": "wf-policy",
            "rules": [
                {"id": "allow-step1", "priority": 10, "action": "action1", "step_id": "step1", "effect": "allow", "reason": "ok", "risk_level": "low"},
                {"id": "deny-step2", "priority": 10, "action": "action2", "step_id": "step2", "effect": "deny", "reason": "blocked", "risk_level": "high"},
            ],
        }
    ]
    metadata = {
        "step1": {"action": "action1", "resource": "r1", "output": "done", "drift": 0.01},
        "step2": {"action": "action2", "resource": "r2", "output": "nope", "drift": 0.02},
    }

    receipt = GoverningWorkflowRunner(policies, metadata).run(str(workflow), str(receipt_path))

    assert receipt["steps"][0]["governance"]["verdict"] == "allow"
    assert receipt["steps"][1]["status"] == "denied"
    assert receipt["steps"][1]["governance"]["verdict"] == "deny"
    assert receipt["steps"][1]["governance"]["policy_name"] == "wf-policy"
    assert receipt["steps"][1]["governance"]["rule_id"] == "deny-step2"
    validate_receipt(receipt)


def test_receipts_validate_and_hash_chain_is_deterministic_for_stable_inputs(tmp_path):
    workflow = Path("examples/governance_demo.srxml")
    metadata = {
        "step1": {"action": "analyze_requirements", "resource": "doc_store/requirements.txt", "output": "ok", "drift": 0.02},
        "step2": {"action": "propose_code_change", "resource": "src/payment_handler.py", "output": "ok", "drift": 0.15},
        "step3": {"action": "generate_validation_tests", "resource": "tests/test_payments.py", "output": "ok", "drift": 0.04},
    }
    policies = [
        {
            "name": "demo",
            "rules": [
                {"id": "s1", "priority": 10, "action": "analyze_requirements", "effect": "allow", "reason": "ok", "risk_level": "low"},
                {"id": "s2", "priority": 20, "action": "propose_code_change", "effect": "allow_with_conditions", "reason": "ok", "risk_level": "medium", "conditions": ["c1"]},
                {"id": "s3", "priority": 30, "action": "generate_validation_tests", "effect": "allow", "reason": "ok", "risk_level": "low"},
            ],
        }
    ]

    r1 = GoverningWorkflowRunner(policies, metadata).run(str(workflow), str(tmp_path / "r1.json"))
    r2 = GoverningWorkflowRunner(policies, metadata).run(str(workflow), str(tmp_path / "r2.json"))

    assert r1["receipt_chain"] == r2["receipt_chain"]

    for receipt_file in Path("receipts").glob("*.json"):
        validate_receipt(json.loads(receipt_file.read_text(encoding="utf-8")))
