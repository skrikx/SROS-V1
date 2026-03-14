"""
SRX Router Demonstration
========================

Live examples of the multi-model task router in action.
Shows classification, routing decisions, and backend selection.
"""

import json
from sros.router.task_router import TaskRouter
from sros.router.classification_engine import TaskLabel
from sros.router.routing_rules_evaluator import BackendID


def demo_router():
    """Demonstrate the SRX router with various task types."""
    
    router = TaskRouter()
    
    # Example tasks covering all classifications
    tasks = [
        {
            "description": "Simple code refactoring",
            "intent": "Refactor the memory_daemon.py module to improve error handling",
            "metadata": {"files_impacted": 1, "estimated_complexity": "low"},
        },
        {
            "description": "Complex multi-file implementation",
            "intent": (
                "Implement a new persistence layer with SQLite backend, "
                "vector search capabilities, and comprehensive error recovery. "
                "This will span kernel, memory, and adapters subsystems."
            ),
            "metadata": {
                "files_impacted": 8,
                "estimated_complexity": "high",
                "urgency": "deep",
            },
        },
        {
            "description": "Unit test generation",
            "intent": "Create comprehensive pytest fixtures and unit tests for the vector backend",
            "metadata": {"infra_sensitive": False},
        },
        {
            "description": "Infrastructure-sensitive tests",
            "intent": "Write integration tests for the kernel bootstrap and daemon lifecycle",
            "metadata": {"infra_sensitive": True},
        },
        {
            "description": "Documentation and API reference",
            "intent": "Update README.md and create comprehensive API documentation with examples",
            "metadata": {},
        },
        {
            "description": "Governance and risk analysis",
            "intent": (
                "Design a comprehensive safety policy framework including risk assessment, "
                "mitigation strategies, and compliance auditing for multi-model deployment"
            ),
            "metadata": {},
        },
        {
            "description": "Research and literature review",
            "intent": "Survey the literature on multi-model routing strategies and agent design patterns",
            "metadata": {},
        },
        {
            "description": "Hotfix - urgent code issue",
            "intent": "Fix critical bug in adapter registry fallback logic",
            "metadata": {"urgency": "hotfix"},
        },
    ]
    
    print("\n" + "="*80)
    print("SRX MULTI-MODEL TASK ROUTER - LIVE DEMONSTRATION")
    print("="*80)
    print(f"\nRouter Contract: {router.get_router_contract()['id']} v{router.get_router_contract()['version']}")
    print(f"Tenant: PlatXP")
    print("\n" + "-"*80)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n[Task {i}] {task['description']}")
        print(f"Intent: {task['intent'][:70]}...")
        
        # Route the task
        result = router.route(
            intent_text=task["intent"],
            metadata=task["metadata"],
            tenant="PlatXP",
        )
        
        # Display routing decision
        print(f"\n  [*] Classification:")
        print(f"    - Label: {result.task_label.value.upper()}")
        print(f"    - Confidence: {result.classification_confidence:.1%}")
        
        print(f"\n  [*] Routing Decision:")
        print(f"    - Primary Backend: {result.primary_backend.value.upper()}")
        if result.secondary_backend:
            print(f"    - Secondary Backend: {result.secondary_backend.value.upper()}")
        print(f"    - Reason: {result.routing_reason}")
        if result.priority_override:
            print(f"    - Priority Override: {result.priority_override.upper()}")
        
        print(f"\n  [*] Execution Parameters:")
        print(f"    - Max Depth: {result.max_depth}")
        print(f"    - Fallback Chain: {' -> '.join(b.value.upper() for b in result.fallback_chain)}")
        print(f"    - Available Adapters: {', '.join(result.adapters_available)}")
        
        print("\n" + "-"*80)
    
    # Print router statistics
    stats = router.get_stats()
    print(f"\n[Router Statistics]")
    print(f"  - Requests Processed: {stats['requests_processed']}")
    print(f"  - Classifier Patterns: {stats['classifier_patterns']}")
    print(f"  - Routing Rules: {stats['routing_rules']}")
    print(f"  - Adapters Registered: {stats['adapters_registered']}")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


def demo_router_contract():
    """Display the complete router contract."""
    router = TaskRouter()
    contract = router.get_router_contract()
    
    print("\n" + "="*80)
    print("SRX ROUTER CONTRACT")
    print("="*80)
    print(json.dumps(contract, indent=2, default=str))
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_router()
    demo_router_contract()
