"""
Policy Engine

Evaluates actions against active policies using Rego-like rule evaluation.
Core of governance system for SROS.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PolicyEffect(Enum):
    """Policy effects."""
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class PolicyRule:
    """Represents a single policy rule."""
    id: str
    effect: PolicyEffect
    actions: List[str]  # e.g., ["adapter.gemini.*", "workflow.execute"]
    resources: List[str]  # e.g., ["memory/*", "agent/*"]
    principals: List[str]  # e.g., ["tester", "architect"]
    conditions: Dict[str, Any] = None  # Custom conditions
    priority: int = 0  # Higher priority evaluated first


class PolicyResult:
    """Result of policy evaluation."""
    
    def __init__(self, allowed: bool, reason: str = "", rule_id: str = None):
        self.allowed = allowed
        self.reason = reason
        self.rule_id = rule_id
    
    def __repr__(self):
        return f"PolicyResult(allowed={self.allowed}, reason='{self.reason}', rule_id={self.rule_id})"


class PolicyEngine:
    """
    Evaluates actions against active policies.
    
    Features:
    - Rule-based policy evaluation
    - Priority-based rule ordering
    - Pattern matching for actions/resources
    - Audit logging of all policy decisions
    - Default-deny security posture
    """
    
    def __init__(self, mode: str = "strict", default_action: str = "deny"):
        """
        Initialize policy engine.
        
        Args:
            mode: Enforcement mode (strict, permissive, audit)
            default_action: Default action if no rule matches (allow, deny)
        """
        self.mode = mode
        self.default_action = default_action
        self.policies: List[PolicyRule] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.custom_evaluators: Dict[str, Callable] = {}
    
    def add_policy(self, policy: PolicyRule):
        """
        Add a policy rule to the engine.
        
        Args:
            policy: PolicyRule to add
        """
        self.policies.append(policy)
        # Sort by priority (highest first)
        self.policies.sort(key=lambda p: p.priority, reverse=True)
        logger.debug(f"Added policy rule: {policy.id}")
    
    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove a policy rule.
        
        Args:
            policy_id: ID of policy to remove
        
        Returns:
            True if removed, False if not found
        """
        before_len = len(self.policies)
        self.policies = [p for p in self.policies if p.id != policy_id]
        
        if len(self.policies) < before_len:
            logger.debug(f"Removed policy rule: {policy_id}")
            return True
        
        return False
    
    def register_custom_evaluator(self, condition_type: str, evaluator: Callable):
        """
        Register custom condition evaluator.
        
        Args:
            condition_type: Type of condition to evaluate
            evaluator: Callable(condition, context) -> bool
        """
        self.custom_evaluators[condition_type] = evaluator
        logger.debug(f"Registered custom evaluator: {condition_type}")
    
    def _pattern_match(self, pattern: str, value: str) -> bool:
        """
        Match value against pattern (supports wildcards).
        
        Args:
            pattern: Pattern with * wildcards (e.g., "adapter.*")
            value: Value to match
        
        Returns:
            True if pattern matches
        """
        if pattern == "*":
            return True
        
        if "*" not in pattern:
            return pattern == value
        
        # Convert pattern to regex-like matching
        parts = pattern.split("*")
        remaining = value
        
        for part in parts:
            if not part:
                continue
            
            if part not in remaining:
                return False
            
            # Move past this part
            idx = remaining.index(part) + len(part)
            remaining = remaining[idx:]
        
        return True
    
    def _evaluate_conditions(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        """
        Evaluate custom conditions for a rule.
        
        Args:
            rule: Policy rule
            context: Evaluation context
        
        Returns:
            True if all conditions pass
        """
        if not rule.conditions:
            return True
        
        for condition_type, condition_value in rule.conditions.items():
            if condition_type in self.custom_evaluators:
                evaluator = self.custom_evaluators[condition_type]
                if not evaluator(condition_value, context):
                    return False
            else:
                # Basic context matching
                context_value = context.get(condition_type)
                if context_value != condition_value:
                    return False
        
        return True
    
    def _matches_rule(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        """
        Check if context matches a rule.
        
        Args:
            rule: Policy rule to check
            context: Evaluation context with action, resource, principal
        
        Returns:
            True if all rule criteria match
        """
        action = context.get("action", "")
        resource = context.get("resource", "")
        principal = context.get("principal", "")
        
        # Check action
        action_match = any(self._pattern_match(p, action) for p in rule.actions)
        if not action_match:
            return False
        
        # Check resource
        resource_match = any(self._pattern_match(p, resource) for p in rule.resources)
        if not resource_match:
            return False
        
        # Check principal
        principal_match = any(self._pattern_match(p, principal) for p in rule.principals)
        if not principal_match:
            return False
        
        # Check custom conditions
        if not self._evaluate_conditions(rule, context):
            return False
        
        return True
    
    def evaluate(self, action: str, context: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate an action against loaded policies.
        
        Args:
            action: Action to evaluate
            context: Context dict with resource, principal, etc.
        
        Returns:
            PolicyResult indicating if action is allowed
        """
        # Ensure we have required context fields
        if "action" not in context:
            context["action"] = action
        
        # Evaluate policies in priority order
        for policy in self.policies:
            if self._matches_rule(policy, context):
                result = PolicyResult(
                    allowed=(policy.effect == PolicyEffect.ALLOW),
                    reason=f"Policy rule '{policy.id}' matched",
                    rule_id=policy.id
                )
                self._audit_decision(context, result)
                return result
        
        # No matching rule - use default
        allowed = self.default_action == "allow"
        result = PolicyResult(
            allowed=allowed,
            reason=f"No matching policy; using default: {self.default_action}",
            rule_id=None
        )
        self._audit_decision(context, result)
        return result
    
    def _audit_decision(self, context: Dict[str, Any], result: PolicyResult):
        """Log policy decision for audit trail."""
        entry = {
            "timestamp": __import__("time").time(),
            "action": context.get("action", "unknown"),
            "resource": context.get("resource", "unknown"),
            "principal": context.get("principal", "unknown"),
            "allowed": result.allowed,
            "reason": result.reason,
            "rule_id": result.rule_id
        }
        
        self.audit_log.append(entry)
        
        log_level = logging.INFO if result.allowed else logging.WARNING
        logger.log(log_level, f"Policy Decision: {result}")
    
    def check(self, subject: str, action: str, resource: str) -> bool:
        """
        Convenience method for simple policy checks.
        
        Args:
            subject: Subject performing action
            action: Action to perform
            resource: Resource being acted upon
        
        Returns:
            True if allowed, False if denied
        """
        context = {
            "principal": subject,
            "action": action,
            "resource": resource
        }
        
        result = self.evaluate(action, context)
        return result.allowed
    
    def get_audit_log(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of audit log entries
        """
        if limit:
            return self.audit_log[-limit:]
        
        return self.audit_log
    
    def get_stats(self) -> Dict[str, Any]:
        """Get policy engine statistics."""
        allowed_count = sum(1 for entry in self.audit_log if entry["allowed"])
        denied_count = len(self.audit_log) - allowed_count
        
        return {
            "policies_loaded": len(self.policies),
            "audit_log_size": len(self.audit_log),
            "decisions_allowed": allowed_count,
            "decisions_denied": denied_count,
            "default_action": self.default_action,
            "mode": self.mode
        }

