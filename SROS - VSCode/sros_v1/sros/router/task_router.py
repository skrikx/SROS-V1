"""
Task Router Orchestrator
========================

Main router that orchestrates classification, routing decision, and adapter dispatch.
Integrates with the adapter registry to execute tasks on the selected backend.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
import logging

from .classification_engine import ClassificationEngine, TaskLabel, ClassificationResult
from .routing_rules_evaluator import (
    RoutingRulesEvaluator,
    RoutingDecision,
    BackendID,
)

logger = logging.getLogger(__name__)


@dataclass
class TaskRequest:
    """Incoming task request to be routed."""
    intent_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tenant: str = "default"
    request_id: Optional[str] = None


@dataclass
class RoutingResult:
    """Result of routing decision and adapter selection."""
    request_id: str
    task_label: TaskLabel
    classification_confidence: float
    primary_backend: BackendID
    secondary_backend: Optional[BackendID]
    max_depth: int
    routing_reason: str
    routing_notes: str
    priority_override: Optional[str]
    adapters_available: List[str]
    fallback_chain: List[BackendID] = field(default_factory=list)


class TaskRouter:
    """
    SRX Multi-Model Task Router.
    
    Classifies incoming intents and routes them to Gemini, OpenAI, or Claude
    based on task type, complexity, context needs, and availability.
    
    Integration points:
    - ClassificationEngine: Pattern-based intent classification
    - RoutingRulesEvaluator: Rule evaluation and backend selection
    - Adapter Registry: Backend availability and capability discovery
    - Event Bus: Publishing routing decisions for observability
    """

    def __init__(
        self,
        adapter_registry: Optional[Dict[str, Any]] = None,
        event_bus: Optional[Any] = None,
    ):
        """
        Initialize task router.
        
        Args:
            adapter_registry: Adapter registry for backend availability checks
            event_bus: Event bus for publishing routing events
        """
        self.classifier = ClassificationEngine()
        self.evaluator = RoutingRulesEvaluator()
        self.adapter_registry = adapter_registry or {}
        self.event_bus = event_bus
        self.request_counter = 0
        
        logger.info("TaskRouter initialized (SRX.SROS.MultiModel.TaskRouter.V1)")

    def route(
        self,
        intent_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        tenant: str = "default",
        request_id: Optional[str] = None,
    ) -> RoutingResult:
        """
        Route a task request to the appropriate backend.
        
        Pipeline:
        1. Classify intent using pattern matching
        2. Evaluate routing rules based on classification and metadata
        3. Check backend availability
        4. Build fallback chain
        5. Publish routing decision to event bus
        
        Args:
            intent_text: The task intent/request
            metadata: Optional metadata (complexity, urgency, files_impacted, etc.)
            tenant: Tenant ID for multi-tenancy
            request_id: Optional request ID for tracing
            
        Returns:
            RoutingResult with backend routing and decision details
        """
        self.request_counter += 1
        request_id = request_id or f"ROUTE-{self.request_counter:06d}"
        metadata = metadata or {}
        
        logger.debug(f"[{request_id}] Routing request for tenant={tenant}")
        logger.debug(f"[{request_id}] Intent: {intent_text[:100]}...")
        
        # Step 1: Classify intent
        classification = self.classifier.classify(intent_text)
        logger.info(
            f"[{request_id}] Classification: {classification.primary_label.value} "
            f"(confidence={classification.confidence:.2f})"
        )
        
        # Step 2: Evaluate routing rules
        routing_decision = self.evaluator.evaluate(
            classification.primary_label, metadata
        )
        logger.info(
            f"[{request_id}] Routing decision: {routing_decision.primary_backend.value} "
            f"(reason: {routing_decision.reason})"
        )
        
        # Step 3: Check backend availability and build fallback chain
        primary_available = self._is_backend_available(routing_decision.primary_backend)
        secondary_available = (
            routing_decision.secondary_backend
            and self._is_backend_available(routing_decision.secondary_backend)
        )
        
        fallback_chain = [routing_decision.primary_backend]
        if routing_decision.secondary_backend:
            fallback_chain.append(routing_decision.secondary_backend)
        
        # Add automatic fallback if primary unavailable
        if not primary_available:
            logger.warning(
                f"[{request_id}] Primary backend {routing_decision.primary_backend.value} unavailable"
            )
            fallback_decision = self.evaluator.get_fallback_strategy(
                routing_decision.primary_backend,
                f"Primary {routing_decision.primary_backend.value} unavailable",
            )
            if fallback_decision.primary_backend not in fallback_chain:
                fallback_chain.insert(0, fallback_decision.primary_backend)
            if (
                fallback_decision.secondary_backend
                and fallback_decision.secondary_backend not in fallback_chain
            ):
                fallback_chain.append(fallback_decision.secondary_backend)
        
        # Step 4: Get available adapters
        available_adapters = self._get_available_adapters(fallback_chain)
        
        # Step 5: Build and publish routing result
        result = RoutingResult(
            request_id=request_id,
            task_label=classification.primary_label,
            classification_confidence=classification.confidence,
            primary_backend=routing_decision.primary_backend,
            secondary_backend=routing_decision.secondary_backend,
            max_depth=routing_decision.max_depth,
            routing_reason=routing_decision.reason,
            routing_notes=routing_decision.notes,
            priority_override=routing_decision.priority_override,
            adapters_available=available_adapters,
            fallback_chain=fallback_chain,
        )
        
        self._publish_routing_event(result, classification)
        
        logger.info(f"[{request_id}] Routing complete. Primary: {result.primary_backend.value}")
        
        return result

    def _is_backend_available(self, backend: BackendID) -> bool:
        """Check if a backend is available in the adapter registry."""
        adapter_key = f"{backend.value}_adapter"
        
        if not self.adapter_registry:
            # Assume all backends available if no registry
            return True
        
        adapter = self.adapter_registry.get(adapter_key)
        if not adapter:
            return False
        
        # Check if adapter has a health check method
        if hasattr(adapter, "is_healthy"):
            return adapter.is_healthy()
        
        # If no health check, assume available
        return True

    def _get_available_adapters(self, fallback_chain: List[BackendID]) -> List[str]:
        """Get list of adapter names for backends in fallback chain."""
        available = []
        for backend in fallback_chain:
            adapter_key = f"{backend.value}_adapter"
            if self._is_backend_available(backend):
                available.append(adapter_key)
        return available

    def _publish_routing_event(
        self, result: RoutingResult, classification: ClassificationResult
    ) -> None:
        """Publish routing decision to event bus."""
        if not self.event_bus:
            return
        
        event = {
            "type": "routing_decision",
            "request_id": result.request_id,
            "task_label": result.task_label.value,
            "classification_confidence": result.classification_confidence,
            "primary_backend": result.primary_backend.value,
            "secondary_backend": result.secondary_backend.value if result.secondary_backend else None,
            "max_depth": result.max_depth,
            "routing_reason": result.routing_reason,
            "fallback_chain": [b.value for b in result.fallback_chain],
            "adapters_available": result.adapters_available,
        }
        
        try:
            self.event_bus.publish("routing", event)
            logger.debug(f"[{result.request_id}] Published routing event")
        except Exception as e:
            logger.error(f"Failed to publish routing event: {e}")

    def get_router_contract(self) -> Dict[str, Any]:
        """Return the router contract (input/output schema)."""
        return {
            "id": "SRX.SROS.MultiModel.TaskRouter.V1",
            "version": "1.0.0",
            "input": {
                "intent_text": "string (required)",
                "metadata": {
                    "description": "Task metadata for routing decisions",
                    "fields": {
                        "files_impacted": "integer (default: 1)",
                        "estimated_complexity": "string [low|medium|high] (default: medium)",
                        "urgency": "string [hotfix|deep|normal] (default: normal)",
                        "infra_sensitive": "boolean (default: false)",
                        "tenant": "string (default: default)",
                    },
                },
            },
            "output": {
                "request_id": "string",
                "task_label": "string [code|tests|docs|research|governance|unclassified]",
                "classification_confidence": "float [0.0-1.0]",
                "primary_backend": "string [gemini|openai|claude]",
                "secondary_backend": "string|null",
                "max_depth": "integer",
                "routing_reason": "string",
                "fallback_chain": "list[string]",
                "adapters_available": "list[string]",
            },
            "backends": {
                "gemini": "Fast code generation, lower latency",
                "openai": "Multi-file refactoring, structured reasoning",
                "claude": "Long-context, deep synthesis, governance",
            },
            "labels": {
                "code": "Refactor, implement, fix bug, adapters, modules",
                "tests": "Unit tests, integration tests, pytest, coverage",
                "docs": "README, documentation, docstrings, guides",
                "research": "Research, compare, survey, literature",
                "governance": "Safety, risk, policy, governance, security",
            },
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            "requests_processed": self.request_counter,
            "classifier_patterns": {
                label.value: len(patterns)
                for label, patterns in self.classifier.PATTERNS.items()
            },
            "routing_rules": len(self.evaluator.rules),
            "adapters_registered": len(self.adapter_registry),
        }
