"""
SRX Router Module
================

Multi-model task routing engine that classifies intents and routes them to
Gemini, OpenAI, or Claude based on task characteristics, complexity, and context.

Implements SRX.SROS.MultiModel.TaskRouter.V1 schema.
"""

from .task_router import TaskRouter
from .classification_engine import ClassificationEngine
from .routing_rules_evaluator import RoutingRulesEvaluator

__all__ = ["TaskRouter", "ClassificationEngine", "RoutingRulesEvaluator"]
