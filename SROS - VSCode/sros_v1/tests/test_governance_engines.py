"""
Governance Engine Tests

Tests for PolicyEngine, EvaluationEngine, PolicyCatalog, and RiskRegistry.
"""
import pytest
import time
from sros.governance.policy_engine import PolicyEngine, PolicyRule, PolicyEffect
from sros.governance.eval_engine import EvaluationEngine, PolicyProposal
from sros.governance.eval_catalog import PolicyCatalog, PolicyTemplate
from sros.governance.risk_registry import RiskRegistry, RiskLevel


class TestPolicyEngine:
    """Test policy engine with real evaluation logic."""
    
    @pytest.fixture
    def engine(self):
        return PolicyEngine(mode="strict", default_action="deny")
    
    def test_policy_engine_init(self, engine):
        """Test engine initialization."""
        assert engine.mode == "strict"
        assert engine.default_action == "deny"
        assert len(engine.policies) == 0
    
    def test_add_policy(self, engine):
        """Test adding policies."""
        rule = PolicyRule(
            id="allow_tester",
            effect=PolicyEffect.ALLOW,
            actions=["test.*"],
            resources=["memory/*"],
            principals=["tester"]
        )
        
        engine.add_policy(rule)
        assert len(engine.policies) == 1
    
        def test_evaluate_allowed(self, engine):
            """Test evaluation allowing action."""
        rule = PolicyRule(
            id="allow_gemini",
            effect=PolicyEffect.ALLOW,
            actions=["adapter.model.gemini"],
            resources=["agent/*"],
            principals=["*"]
        )
        
        engine.add_policy(rule)
        
        context = {
            "action": "adapter.model.gemini",
            "resource": "agent/tester",
            "principal": "runtime"
        }
        
        result = engine.evaluate("adapter.model.gemini", context)
        assert result.allowed == True
    
    def test_evaluate_denied(self, engine):
        """Test evaluation denying action."""
        rule = PolicyRule(
            id="deny_risky",
            effect=PolicyEffect.DENY,
            actions=["delete.*"],
            resources=["memory/*"],
            principals=["*"]
        )
        
        engine.add_policy(rule)
        
        context = {
            "action": "delete.memory",
            "resource": "memory/user_data",
            "principal": "agent"
        }
        
        result = engine.evaluate("delete.memory", context)
        assert result.allowed == False
    
    def test_default_deny(self, engine):
        """Test default deny when no rule matches."""
        context = {
            "action": "unknown",
            "resource": "unknown",
            "principal": "unknown"
        }
        
        result = engine.evaluate("unknown", context)
        assert result.allowed == False
    
    def test_pattern_matching(self, engine):
        """Test wildcard pattern matching."""
        rule = PolicyRule(
            id="allow_all_adapters",
            effect=PolicyEffect.ALLOW,
            actions=["adapter.*"],
            resources=["*"],
            principals=["*"]
        )
        
        engine.add_policy(rule)
        
        # Should match adapter.gemini, adapter.openai, etc.
        result = engine.evaluate("adapter.openai", {"action": "adapter.openai", "resource": "model", "principal": "agent"})
        assert result.allowed == True
    
    def test_priority_ordering(self, engine):
        """Test policies evaluated in priority order."""
        # Higher priority rule should be checked first
        allow_rule = PolicyRule(
            id="allow",
            effect=PolicyEffect.ALLOW,
            actions=["test"],
            resources=["*"],
            principals=["*"],
            priority=10
        )
        
        deny_rule = PolicyRule(
            id="deny",
            effect=PolicyEffect.DENY,
            actions=["test"],
            resources=["*"],
            principals=["*"],
            priority=5
        )
        
        engine.add_policy(allow_rule)
        engine.add_policy(deny_rule)
        
        # Higher priority (allow) should match first
        result = engine.evaluate("test", {"action": "test", "resource": "x", "principal": "y"})
        assert result.allowed == True
        assert result.rule_id == "allow"
    
    def test_audit_log(self, engine):
        """Test audit logging."""
        rule = PolicyRule(
            id="test_rule",
            effect=PolicyEffect.ALLOW,
            actions=["test"],
            resources=["*"],
            principals=["*"]
        )
        
        engine.add_policy(rule)
        engine.evaluate("test", {"action": "test", "resource": "x", "principal": "y"})
        
        assert len(engine.audit_log) >= 1
        assert engine.audit_log[-1]["action"] == "test"
    
    def test_check_convenience(self, engine):
        """Test convenience check method."""
        rule = PolicyRule(
            id="allow_read",
            effect=PolicyEffect.ALLOW,
            actions=["read"],
            resources=["memory/*"],
            principals=["user"]
        )
        
        engine.add_policy(rule)
        
        result = engine.check("user", "read", "memory/data")
        assert result == True
    
    def test_get_stats(self, engine):
        """Test getting engine statistics."""
        rule = PolicyRule(
            id="test",
            effect=PolicyEffect.ALLOW,
            actions=["test"],
            resources=["*"],
            principals=["*"]
        )
        
        engine.add_policy(rule)
        engine.evaluate("test", {"action": "test", "resource": "x", "principal": "y"})
        
        stats = engine.get_stats()
        assert stats["policies_loaded"] == 1
        assert stats["audit_log_size"] >= 1


class TestEvaluationEngine:
    """Test governance evaluation engine."""
    
    @pytest.fixture
    def eval_engine(self):
        return EvaluationEngine()
    
    def test_submit_proposal(self, eval_engine):
        """Test submitting a policy proposal."""
        proposal = eval_engine.submit_proposal(
            "prop1",
            "add",
            "policy_cost_limit",
            policy_rule={"action": "limit_cost", "effect": "allow"}
        )
        
        assert proposal.id == "prop1"
        assert proposal.change_type == "add"
        assert eval_engine.total_proposals == 1
    
    def test_evaluate_proposal(self, eval_engine):
        """Test evaluating a proposal."""
        proposal = eval_engine.submit_proposal(
            "prop1",
            "add",
            "new_policy",
            policy_rule={"action": "test", "effect": "allow"}
        )
        
        result = eval_engine.evaluate_proposal("prop1", None, [])
        
        assert result.proposal_id == "prop1"
        assert "confidence" in vars(result)
        assert "risk_score" in vars(result)
    
    def test_proposal_approval(self, eval_engine):
        """Test approving a proposal."""
        eval_engine.submit_proposal("prop1", "add", "policy1", policy_rule={})
        eval_engine.evaluate_proposal("prop1", None, [])
        
        result = eval_engine.approve_proposal("prop1")
        assert result == True
        assert len(eval_engine.approval_history) >= 1


class TestPolicyCatalog:
    """Test policy catalog."""
    
    @pytest.fixture
    def catalog(self):
        return PolicyCatalog()
    
    def test_add_policy(self, catalog):
        """Test adding policies."""
        policy = {"effect": "allow", "actions": ["test"]}
        catalog.add_policy("policy1", policy, "security")
        
        assert catalog.get_policy("policy1") == policy
    
    def test_get_by_category(self, catalog):
        """Test getting policies by category."""
        catalog.add_policy("p1", {}, "security")
        catalog.add_policy("p2", {}, "security")
        catalog.add_policy("p3", {}, "performance")
        
        security_policies = catalog.get_policies_by_category("security")
        assert len(security_policies) == 2
    
    def test_add_template(self, catalog):
        """Test adding templates."""
        template = PolicyTemplate(
            id="t1",
            name="Cost Limit",
            description="Limit daily costs",
            category="cost",
            template={"action": "limit_cost"},
            parameters={"max_daily": 100}
        )
        
        catalog.add_template("t1", template)
        
        retrieved = catalog.get_template("t1")
        assert retrieved.id == "t1"
    
    def test_create_from_template(self, catalog):
        """Test creating policy from template."""
        template = PolicyTemplate(
            id="t1",
            name="Test",
            description="Test template",
            category="general",
            template={"limit": "${max}"},
            parameters={"max": 100}
        )
        
        catalog.add_template("t1", template)
        
        # Create policy from template
        policy = catalog.create_policy_from_template(
            "p1", "t1", {"max": 200}
        )
        
        assert policy is not None
        assert "p1" in catalog.policies


class TestRiskRegistry:
    """Test risk registry."""
    
    @pytest.fixture
    def registry(self):
        return RiskRegistry()
    
    def test_register_risk(self, registry):
        """Test registering a risk."""
        risk = registry.register_risk(
            "r1",
            "Policy Conflict",
            "Conflicting policies may cause deadlock",
            RiskLevel.HIGH,
            "policy_conflict"
        )
        
        assert risk.id == "r1"
        assert risk.level == RiskLevel.HIGH
    
    def test_add_mitigation(self, registry):
        """Test adding mitigation strategies."""
        registry.register_risk("r1", "Risk", "Desc", RiskLevel.MEDIUM, "cat")
        
        registry.add_mitigation_strategy("r1", "Validate policies before loading")
        
        assert len(registry.risks["r1"].mitigation_strategies) == 1
    
    def test_record_occurrence(self, registry):
        """Test recording risk occurrences."""
        registry.register_risk("r1", "Risk", "Desc", RiskLevel.HIGH, "cat")
        
        registry.record_risk_occurrence("r1")
        assert registry.risks["r1"].occurrence_count == 1
    
    def test_policy_risk_association(self, registry):
        """Test associating policies with risks."""
        registry.register_risk("r1", "Risk", "Desc", RiskLevel.MEDIUM, "cat")
        
        registry.associate_policy_with_risk("p1", "r1")
        
        # Check that policy is in policies for risk
        assert "p1" in registry.get_policies_for_risk("r1")
        # Check that risk entries are in risks for policy
        risks_for_policy = registry.get_risks_for_policy("p1")
        assert len(risks_for_policy) == 1
        assert risks_for_policy[0].id == "r1"
    
    def test_risk_profile(self, registry):
        """Test assessing policy risk profile."""
        registry.register_risk("r1", "Risk1", "Desc", RiskLevel.HIGH, "cat")
        registry.register_risk("r2", "Risk2", "Desc", RiskLevel.LOW, "cat")
        
        registry.associate_policy_with_risk("p1", "r1")
        registry.associate_policy_with_risk("p1", "r2")
        
        profile = registry.assess_policy_risk_profile("p1")
        
        assert profile["policy_id"] == "p1"
        assert profile["associated_risks"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
