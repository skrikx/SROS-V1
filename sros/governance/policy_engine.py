"""Deterministic governance policy evaluation engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PolicyResult:
    allowed: bool
    reason: str = ""
    verdict: str = "deny"
    matched_policy_name: Optional[str] = None
    matched_rule_id: Optional[str] = None
    risk_level: Optional[str] = None
    conditions: List[str] = field(default_factory=list)


class PolicyEngine:
    """Evaluates actions against active policies."""

    def __init__(self, mode: str = "strict"):
        self.mode = mode
        self.policies: List[Dict[str, Any]] = []

    def load_policy(self, policy: Dict[str, Any]):
        """Load a policy into the engine."""
        self.policies.append(policy)

    def evaluate(self, action: str, context: Dict[str, Any]) -> PolicyResult:
        """Evaluate an action and context against all loaded policy rules."""
        context = context or {}
        matched: List[Dict[str, Any]] = []

        for policy_index, policy in enumerate(self.policies):
            policy_name = policy.get("name", f"policy_{policy_index + 1}")
            rules = policy.get("rules")
            if not isinstance(rules, list):
                continue

            for rule_index, rule in enumerate(rules):
                if not self._rule_matches(rule, action, context):
                    continue
                matched.append(
                    {
                        "policy_index": policy_index,
                        "rule_index": rule_index,
                        "policy_name": policy_name,
                        "rule": rule,
                    }
                )

        if not matched:
            return PolicyResult(
                allowed=False,
                verdict="deny",
                reason="No matching governance rule",
            )

        top_match = self._select_highest_priority_match(matched)
        rule = top_match["rule"]
        verdict = rule.get("effect", "deny")
        allowed = verdict in {"allow", "allow_with_conditions"}

        return PolicyResult(
            allowed=allowed,
            verdict=verdict,
            matched_policy_name=top_match["policy_name"],
            matched_rule_id=rule.get("id"),
            reason=rule.get("reason", "Matched governance rule"),
            risk_level=rule.get("risk_level"),
            conditions=list(rule.get("conditions", [])),
        )

    def check(self, subject: str, action: str, resource: str) -> bool:
        """Returns True if allowed, False if denied."""
        result = self.evaluate(
            action,
            {
                "subject": subject,
                "resource": resource,
            },
        )
        return result.allowed

    def _select_highest_priority_match(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        def sort_key(item: Dict[str, Any]):
            priority = item["rule"].get("priority", 1000)
            return (priority, item["policy_index"], item["rule_index"])

        return sorted(matches, key=sort_key)[0]

    def _rule_matches(self, rule: Dict[str, Any], action: str, context: Dict[str, Any]) -> bool:
        if rule.get("action") not in (None, "*", action):
            return False
        if not self._selector_matches(rule, "resource", context):
            return False
        if not self._selector_matches(rule, "tenant", context):
            return False
        if not self._selector_matches(rule, "step_id", context):
            return False

        required_fields = set(rule.get("requested_fields_all", []))
        if required_fields:
            incoming_fields = set(context.get("requested_fields", []))
            if not required_fields.issubset(incoming_fields):
                return False

        return True

    def _selector_matches(self, rule: Dict[str, Any], key: str, context: Dict[str, Any]) -> bool:
        expected = rule.get(key)
        if expected in (None, "*"):
            return True
        return context.get(key) == expected
