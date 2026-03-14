"""
Routing Rules Evaluator
=======================

Evaluates routing rules from the SRX schema against task metadata and
determines primary/secondary backend routing and execution parameters.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .classification_engine import TaskLabel


class BackendID(Enum):
    """Available AI model backends."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


class RoutingStrategy(Enum):
    """Routing decision strategies."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"


@dataclass
class RoutingDecision:
    """Result of routing rules evaluation."""
    primary_backend: BackendID
    secondary_backend: Optional[BackendID] = None
    strategy: RoutingStrategy = RoutingStrategy.PRIMARY
    max_depth: int = 1
    reason: str = ""
    notes: str = ""
    priority_override: Optional[str] = None  # "hotfix", "deep", etc.


class RoutingRulesEvaluator:
    """
    Evaluates routing rules from SRX schema to determine backend routing.
    
    Rules are evaluated in order:
    1. Priority rules (hotfix, deep refactor)
    2. Label-based routing rules
    3. Fallback rules
    """

    def __init__(self):
        """Initialize routing rules evaluator."""
        self.rules: Dict[str, Dict[str, Any]] = self._init_rules()

    def _init_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize routing rules from SRX schema."""
        return {
            # Priority rules
            "hotfix": {
                "type": "priority",
                "when": {"urgency": "hotfix"},
                "action": {
                    "max_depth": 1,
                    "backend_preference": "openai",
                    "note": "Minimize recursion; produce precise patch fast.",
                },
            },
            "deep_refactor": {
                "type": "priority",
                "when": {"urgency": "deep"},
                "action": {
                    "max_depth": 3,
                    "backend_preference": "openai+claude",
                    "note": "Use openai for execution and claude for reflection; allow multiple loops.",
                },
            },
            # Code tasks
            "code_default": {
                "type": "label_rule",
                "label": TaskLabel.CODE,
                "conditions": {
                    "files_impacted": {"op": "<=", "value": 2},
                    "estimated_complexity": {"op": "<=", "value": "medium"},
                },
                "backend": BackendID.GEMINI,
                "reason": "Fast code generation and lower latency.",
            },
            "code_complex_cross_file": {
                "type": "label_rule",
                "label": TaskLabel.CODE,
                "conditions": {
                    "files_impacted": {"op": ">", "value": 2},
                    "estimated_complexity": {"op": ">=", "value": "medium"},
                },
                "backend": BackendID.OPENAI,
                "reason": "Better at multi-file refactor and structured patches.",
            },
            # Tests
            "tests_default": {
                "type": "label_rule",
                "label": TaskLabel.TESTS,
                "conditions": {
                    "infra_sensitive": {"op": "=", "value": False},
                },
                "backend": BackendID.GEMINI,
                "reason": "Generate unit tests and fixtures quickly.",
            },
            "tests_infra": {
                "type": "label_rule",
                "label": TaskLabel.TESTS,
                "conditions": {
                    "infra_sensitive": {"op": "=", "value": True},
                },
                "backend": BackendID.OPENAI,
                "reason": "Higher risk area, use more careful patching ability.",
            },
            # Docs and governance
            "docs_default": {
                "type": "label_rule",
                "label": TaskLabel.DOCS,
                "conditions": {},
                "backend": BackendID.CLAUDE,
                "reason": "Long-context documentation and explanation quality.",
            },
            "governance_default": {
                "type": "label_rule",
                "label": TaskLabel.GOVERNANCE,
                "conditions": {},
                "backend": BackendID.CLAUDE,
                "reason": "Deep reasoning, risk framing, safety narratives.",
            },
            # Research
            "research_default": {
                "type": "label_rule",
                "label": TaskLabel.RESEARCH,
                "conditions": {},
                "backend": BackendID.CLAUDE,
                "reason": "Better at broad synthesis; long context.",
            },
        }

    def evaluate(
        self,
        task_label: TaskLabel,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """
        Evaluate routing rules and produce routing decision.
        
        Args:
            task_label: The classified task label
            metadata: Task metadata (complexity, urgency, files_impacted, etc.)
            
        Returns:
            RoutingDecision with primary backend and execution parameters
        """
        metadata = metadata or {}
        
        # Step 1: Check priority rules
        priority_decision = self._evaluate_priority_rules(metadata)
        if priority_decision:
            return priority_decision
        
        # Step 2: Check label-based routing rules
        label_decision = self._evaluate_label_rules(task_label, metadata)
        if label_decision:
            return label_decision
        
        # Step 3: Fallback to OpenAI for unclassified
        return RoutingDecision(
            primary_backend=BackendID.OPENAI,
            strategy=RoutingStrategy.FALLBACK,
            reason="Unclassified task; use balanced reasoning and patching.",
            max_depth=1,
        )

    def _evaluate_priority_rules(
        self, metadata: Dict[str, Any]
    ) -> Optional[RoutingDecision]:
        """Evaluate priority rules (hotfix, deep refactor)."""
        urgency = metadata.get("urgency")
        
        if urgency == "hotfix":
            return RoutingDecision(
                primary_backend=BackendID.OPENAI,
                strategy=RoutingStrategy.PRIMARY,
                max_depth=1,
                reason="Hotfix priority: minimize recursion.",
                priority_override="hotfix",
            )
        
        if urgency == "deep":
            return RoutingDecision(
                primary_backend=BackendID.OPENAI,
                secondary_backend=BackendID.CLAUDE,
                strategy=RoutingStrategy.PRIMARY,
                max_depth=3,
                reason="Deep refactor priority: multi-loop with reflection.",
                priority_override="deep",
            )
        
        return None

    def _evaluate_label_rules(
        self, task_label: TaskLabel, metadata: Dict[str, Any]
    ) -> Optional[RoutingDecision]:
        """Evaluate label-based routing rules."""
        
        # Collect applicable rules for this label
        applicable_rules = [
            (rule_id, rule)
            for rule_id, rule in self.rules.items()
            if rule.get("type") == "label_rule" and rule.get("label") == task_label
        ]
        
        if not applicable_rules:
            return None
        
        # Evaluate conditions for each rule
        for rule_id, rule in applicable_rules:
            if self._evaluate_conditions(rule.get("conditions", {}), metadata):
                return RoutingDecision(
                    primary_backend=rule["backend"],
                    strategy=RoutingStrategy.PRIMARY,
                    reason=rule["reason"],
                    max_depth=1,  # Can be overridden by priority rules
                )
        
        # If no conditions match for code rules, check if there's a default rule
        # (rules with empty conditions are defaults)
        for rule_id, rule in applicable_rules:
            if not rule.get("conditions"):
                return RoutingDecision(
                    primary_backend=rule["backend"],
                    strategy=RoutingStrategy.PRIMARY,
                    reason=rule["reason"],
                    max_depth=1,
                )
        
        return None

    def _evaluate_conditions(
        self, conditions: Dict[str, Dict[str, Any]], metadata: Dict[str, Any]
    ) -> bool:
        """
        Evaluate all conditions against metadata.
        
        Supports operators: =, >, <, >=, <=, in, not_in
        """
        if not conditions:
            return True
        
        for key, condition_spec in conditions.items():
            value = metadata.get(key)
            op = condition_spec.get("op", "=")
            expected = condition_spec.get("value")
            
            if not self._evaluate_condition(value, op, expected):
                return False
        
        return True

    def _evaluate_condition(self, value: Any, op: str, expected: Any) -> bool:
        """Evaluate a single condition."""
        # Handle missing values (treat as condition not met)
        if value is None:
            return False
        
        if op == "=":
            return value == expected
        elif op == "<":
            return value < expected
        elif op == ">":
            return value > expected
        elif op == "<=":
            return value <= expected
        elif op == ">=":
            return value >= expected
        elif op == "in":
            return value in expected
        elif op == "not_in":
            return value not in expected
        else:
            # Unknown operator, assume true
            return True

    def get_fallback_strategy(
        self,
        primary_backend: BackendID,
        reason: str = "Primary backend unavailable",
    ) -> RoutingDecision:
        """
        Get fallback routing when primary backend is unavailable.
        
        Fallback hierarchy:
        - If primary is gemini/claude -> try openai
        - If primary is openai -> try gemini for simple tasks, claude for complex
        """
        if primary_backend in (BackendID.GEMINI, BackendID.CLAUDE):
            return RoutingDecision(
                primary_backend=BackendID.OPENAI,
                strategy=RoutingStrategy.FALLBACK,
                reason=reason,
                max_depth=1,
            )
        
        # Primary is openai, try gemini for simple tasks
        return RoutingDecision(
            primary_backend=BackendID.GEMINI,
            secondary_backend=BackendID.CLAUDE,
            strategy=RoutingStrategy.FALLBACK,
            reason=reason,
            max_depth=1,
        )

    def add_custom_rule(
        self, rule_id: str, label: TaskLabel, backend: BackendID,
        conditions: Optional[Dict[str, Dict[str, Any]]] = None,
        reason: str = ""
    ) -> None:
        """Add a custom routing rule."""
        self.rules[rule_id] = {
            "type": "label_rule",
            "label": label,
            "conditions": conditions or {},
            "backend": backend,
            "reason": reason,
        }
