"""
Comprehensive test suite for SRX Router components.

Tests classification engine, routing rules evaluator, and task router
with various scenarios and edge cases.
"""

import pytest
from sros.router.classification_engine import ClassificationEngine, TaskLabel, ClassificationResult
from sros.router.routing_rules_evaluator import (
    RoutingRulesEvaluator,
    BackendID,
    RoutingStrategy,
)
from sros.router.task_router import TaskRouter, RoutingResult


class TestClassificationEngine:
    """Test classification engine pattern matching and confidence scoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()

    def test_classify_code_refactor(self):
        """Test classification of code refactoring task."""
        result = self.engine.classify("Please refactor the adapter module for better separation of concerns")
        assert result.primary_label == TaskLabel.CODE
        assert result.confidence > 0.5
        assert len(result.matched_patterns) > 0

    def test_classify_unit_tests(self):
        """Test classification of unit test task."""
        result = self.engine.classify("Write pytest fixtures and unit tests for the memory backend")
        assert result.primary_label == TaskLabel.TESTS
        assert result.confidence > 0.5

    def test_classify_documentation(self):
        """Test classification of documentation task."""
        result = self.engine.classify("Update the README and API reference with new examples")
        assert result.primary_label == TaskLabel.DOCS
        assert result.confidence >= 0.5

    def test_classify_research(self):
        """Test classification of research task."""
        result = self.engine.classify("Survey the literature on multi-model routing strategies")
        assert result.primary_label == TaskLabel.RESEARCH
        assert result.confidence >= 0.5

    def test_classify_governance(self):
        """Test classification of governance task."""
        result = self.engine.classify("Implement safety guardrails and risk policies for model selection")
        assert result.primary_label == TaskLabel.GOVERNANCE
        assert result.confidence >= 0.5

    def test_classify_unclassified(self):
        """Test classification of unclassified task."""
        result = self.engine.classify("Tell me a joke about clouds")
        assert result.primary_label == TaskLabel.UNCLASSIFIED
        assert result.confidence < 0.3

    def test_classify_empty_text(self):
        """Test handling of empty input."""
        result = self.engine.classify("")
        assert result.primary_label == TaskLabel.UNCLASSIFIED
        assert result.confidence == 0.0

    def test_classify_multiple_patterns(self):
        """Test confidence increases with multiple pattern matches."""
        text_with_many_patterns = "Refactor and implement a new Python module with integration tests and coverage metrics"
        result = self.engine.classify(text_with_many_patterns)
        assert result.confidence > 0.7
        assert len(result.matched_patterns) >= 3

    def test_classify_secondary_labels(self):
        """Test identification of secondary labels."""
        text = "Implement pytest fixtures for integration testing and API documentation"
        result = self.engine.classify(text)
        assert result.primary_label in [TaskLabel.CODE, TaskLabel.TESTS]
        # Secondary label should be the other one
        if result.primary_label == TaskLabel.CODE:
            assert TaskLabel.TESTS in result.secondary_labels or TaskLabel.DOCS in result.secondary_labels

    def test_add_custom_pattern(self):
        """Test adding custom patterns."""
        self.engine.add_custom_pattern(TaskLabel.CODE, r"\bcustom_pattern\b")
        result = self.engine.classify("Please implement the custom_pattern feature")
        assert result.primary_label == TaskLabel.CODE
        assert r"\bcustom_pattern\b" in result.matched_patterns


class TestRoutingRulesEvaluator:
    """Test routing rules evaluation and decision logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = RoutingRulesEvaluator()

    def test_route_code_simple(self):
        """Test routing for simple code task."""
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"files_impacted": 1, "estimated_complexity": "low"},
        )
        assert decision.primary_backend == BackendID.GEMINI
        assert "Fast code generation" in decision.reason

    def test_route_code_complex(self):
        """Test routing for complex multi-file code task."""
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"files_impacted": 5, "estimated_complexity": "high"},
        )
        # When complexity is "high" but operator is ">=" we're checking high >= medium, which is true
        assert decision.primary_backend == BackendID.OPENAI

    def test_route_tests_simple(self):
        """Test routing for simple test generation."""
        decision = self.evaluator.evaluate(
            TaskLabel.TESTS,
            {"infra_sensitive": False},
        )
        assert decision.primary_backend == BackendID.GEMINI

    def test_route_tests_infra(self):
        """Test routing for infrastructure-sensitive tests."""
        decision = self.evaluator.evaluate(
            TaskLabel.TESTS,
            {"infra_sensitive": True},
        )
        assert decision.primary_backend == BackendID.OPENAI

    def test_route_docs(self):
        """Test routing for documentation tasks."""
        decision = self.evaluator.evaluate(TaskLabel.DOCS, {})
        assert decision.primary_backend == BackendID.CLAUDE
        assert "documentation" in decision.reason.lower()

    def test_route_governance(self):
        """Test routing for governance tasks."""
        decision = self.evaluator.evaluate(TaskLabel.GOVERNANCE, {})
        assert decision.primary_backend == BackendID.CLAUDE
        assert "reasoning" in decision.reason.lower() or "risk" in decision.reason.lower()

    def test_route_research(self):
        """Test routing for research tasks."""
        decision = self.evaluator.evaluate(TaskLabel.RESEARCH, {})
        assert decision.primary_backend == BackendID.CLAUDE
        assert "synthesis" in decision.reason.lower()

    def test_priority_hotfix(self):
        """Test hotfix priority overrides normal routing."""
        decision = self.evaluator.evaluate(
            TaskLabel.DOCS,
            {"urgency": "hotfix"},
        )
        assert decision.primary_backend == BackendID.OPENAI
        assert decision.max_depth == 1
        assert decision.priority_override == "hotfix"

    def test_priority_deep_refactor(self):
        """Test deep refactor priority enables multi-loop."""
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"urgency": "deep", "files_impacted": 10, "estimated_complexity": "high"},
        )
        assert decision.primary_backend == BackendID.OPENAI
        assert decision.secondary_backend == BackendID.CLAUDE
        assert decision.max_depth == 3
        assert decision.priority_override == "deep"

    def test_fallback_from_gemini(self):
        """Test fallback routing when primary backend unavailable."""
        fallback = self.evaluator.get_fallback_strategy(BackendID.GEMINI)
        assert fallback.primary_backend == BackendID.OPENAI
        assert fallback.strategy == RoutingStrategy.FALLBACK

    def test_fallback_from_openai(self):
        """Test fallback from OpenAI."""
        fallback = self.evaluator.get_fallback_strategy(BackendID.OPENAI)
        assert fallback.primary_backend == BackendID.GEMINI
        assert fallback.secondary_backend == BackendID.CLAUDE

    def test_condition_operators(self):
        """Test various condition operators."""
        # Test <= operator
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"files_impacted": 2, "estimated_complexity": "medium"},
        )
        assert decision.primary_backend == BackendID.GEMINI

        # Test > operator
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"files_impacted": 3, "estimated_complexity": "medium"},
        )
        assert decision.primary_backend == BackendID.OPENAI

    def test_add_custom_rule(self):
        """Test adding custom routing rules."""
        self.evaluator.add_custom_rule(
            "custom_rule",
            TaskLabel.CODE,
            BackendID.CLAUDE,
            conditions={"estimated_complexity": {"op": "=", "value": "custom"}},
            reason="Custom backend for special case",
        )
        decision = self.evaluator.evaluate(
            TaskLabel.CODE,
            {"estimated_complexity": "custom"},
        )
        assert decision.primary_backend == BackendID.CLAUDE


class TestTaskRouter:
    """Test the main task router orchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.router = TaskRouter()

    def test_route_code_task(self):
        """Test complete routing pipeline for code task."""
        result = self.router.route(
            intent_text="Refactor the memory adapter for better performance",
            metadata={"files_impacted": 2, "estimated_complexity": "medium"},
        )
        assert result.task_label == TaskLabel.CODE
        assert result.primary_backend == BackendID.GEMINI
        assert result.request_id.startswith("ROUTE-")
        assert len(result.adapters_available) > 0

    def test_route_test_task(self):
        """Test routing for test generation."""
        result = self.router.route(
            intent_text="Write pytest fixtures for the vector backend",
            metadata={"infra_sensitive": False},
        )
        assert result.task_label == TaskLabel.TESTS
        assert result.primary_backend == BackendID.GEMINI

    def test_route_governance_task(self):
        """Test routing for governance task."""
        result = self.router.route(
            intent_text="Design safety policies and risk assessment framework",
        )
        assert result.task_label == TaskLabel.GOVERNANCE
        assert result.primary_backend == BackendID.CLAUDE

    def test_route_with_priority_hotfix(self):
        """Test routing with hotfix priority."""
        result = self.router.route(
            intent_text="Fix bug in adapter registry",
            metadata={"urgency": "hotfix"},
        )
        assert result.primary_backend == BackendID.OPENAI
        assert result.max_depth == 1
        assert result.priority_override == "hotfix"

    def test_route_with_priority_deep(self):
        """Test routing with deep refactor priority."""
        result = self.router.route(
            intent_text="Refactor entire kernel architecture",
            metadata={
                "urgency": "deep",
                "files_impacted": 15,
                "estimated_complexity": "high",
            },
        )
        assert result.primary_backend == BackendID.OPENAI
        assert result.secondary_backend == BackendID.CLAUDE
        assert result.max_depth == 3
        assert result.priority_override == "deep"

    def test_route_custom_request_id(self):
        """Test routing with custom request ID."""
        custom_id = "TEST-CUSTOM-001"
        result = self.router.route(
            intent_text="Implement new feature",
            request_id=custom_id,
        )
        assert result.request_id == custom_id

    def test_route_increments_counter(self):
        """Test that request counter increments."""
        initial_count = self.router.request_counter
        self.router.route("Task 1")
        self.router.route("Task 2")
        assert self.router.request_counter == initial_count + 2

    def test_router_contract(self):
        """Test router contract schema."""
        contract = self.router.get_router_contract()
        assert contract["id"] == "SRX.SROS.MultiModel.TaskRouter.V1"
        assert contract["version"] == "1.0.0"
        assert "input" in contract
        assert "output" in contract
        assert "backends" in contract
        assert "labels" in contract

    def test_router_stats(self):
        """Test router statistics."""
        self.router.route("Task 1")
        self.router.route("Task 2")
        stats = self.router.get_stats()
        assert stats["requests_processed"] >= 2
        assert stats["classifier_patterns"]["code"] > 0
        assert stats["routing_rules"] > 0

    def test_fallback_chain_building(self):
        """Test fallback chain construction."""
        result = self.router.route(
            intent_text="Complex refactoring task",
            metadata={
                "urgency": "deep",
                "files_impacted": 10,
                "estimated_complexity": "high",
            },
        )
        assert result.fallback_chain[0] == result.primary_backend
        if result.secondary_backend:
            assert result.secondary_backend in result.fallback_chain

    def test_multiple_classifications_tracked(self):
        """Test that classification confidence and secondary labels are tracked."""
        result = self.router.route(
            intent_text="Refactor Python module and write comprehensive unit tests with pytest and coverage metrics",
        )
        assert result.classification_confidence > 0.0
        assert result.task_label in [TaskLabel.CODE, TaskLabel.TESTS]

    def test_route_unclassified_task(self):
        """Test routing for unclassified task."""
        result = self.router.route(
            intent_text="Tell me about the weather in Paris",
        )
        # Unclassified should fall back to default
        assert result.primary_backend in [BackendID.OPENAI, BackendID.GEMINI, BackendID.CLAUDE]

    def test_router_with_event_bus(self):
        """Test router publishes to event bus."""
        events = []
        
        class MockEventBus:
            def publish(self, channel, event):
                events.append((channel, event))
        
        router_with_bus = TaskRouter(event_bus=MockEventBus())
        result = router_with_bus.route("Implement new feature")
        
        assert len(events) > 0
        assert events[0][0] == "routing"
        assert events[0][1]["type"] == "routing_decision"
        assert events[0][1]["request_id"] == result.request_id

    def test_router_with_adapter_registry(self):
        """Test router checks adapter availability."""
        class MockAdapter:
            def is_healthy(self):
                return True
        
        registry = {
            "gemini_adapter": MockAdapter(),
            "openai_adapter": MockAdapter(),
            "claude_adapter": MockAdapter(),
        }
        
        router_with_registry = TaskRouter(adapter_registry=registry)
        result = router_with_registry.route("Implement feature")
        
        # Check that adapters_available is populated from the fallback chain
        assert len(result.adapters_available) > 0
        # At minimum, the primary backend adapter should be available
        assert any("adapter" in adapter for adapter in result.adapters_available)


class TestRouterIntegration:
    """Integration tests for the complete routing pipeline."""

    def test_end_to_end_code_routing(self):
        """Test complete pipeline from intent to routing decision."""
        router = TaskRouter()
        
        intent = (
            "I need to refactor the adapter_daemon in sros/kernel/daemons/adapter_daemon.py "
            "to improve error handling and add circuit breaker pattern for better resilience"
        )
        
        result = router.route(
            intent_text=intent,
            metadata={
                "files_impacted": 2,
                "estimated_complexity": "medium",
            },
        )
        
        assert result.task_label == TaskLabel.CODE
        assert result.primary_backend == BackendID.GEMINI
        assert result.classification_confidence >= 0.2

    def test_end_to_end_governance_routing(self):
        """Test complete pipeline for governance task."""
        router = TaskRouter()
        
        intent = (
            "Design a comprehensive safety policy framework including risk assessment, "
            "mitigation strategies, and compliance auditing for multi-model deployment"
        )
        
        result = router.route(intent_text=intent)
        
        assert result.task_label == TaskLabel.GOVERNANCE
        assert result.primary_backend == BackendID.CLAUDE

    def test_end_to_end_with_priority_override(self):
        """Test that priority rules override label-based routing."""
        router = TaskRouter()
        
        result = router.route(
            intent_text="Create comprehensive documentation for the entire API",
            metadata={"urgency": "hotfix"},
        )
        
        # Should route to OpenAI despite being a docs task (normally Claude)
        assert result.primary_backend == BackendID.OPENAI
        assert result.priority_override == "hotfix"

    def test_complex_scenario_multi_priority(self):
        """Test complex scenario with multiple factors."""
        router = TaskRouter()
        
        result = router.route(
            intent_text=(
                "Refactor and implement new memory persistence layer with SQLite backend "
                "and comprehensive test coverage including integration tests"
            ),
            metadata={
                "urgency": "deep",
                "files_impacted": 8,
                "estimated_complexity": "high",
            },
        )
        
        # Should route to OpenAI due to deep priority and complexity
        assert result.primary_backend == BackendID.OPENAI
        assert result.max_depth == 3
        assert result.priority_override == "deep"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
