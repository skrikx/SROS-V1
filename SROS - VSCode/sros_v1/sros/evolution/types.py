"""
Evolution Types

Shared data structures for the evolution module to prevent circular imports.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class LoopStage(Enum):
    """Stages of the self-evolution loop."""
    OBSERVE = "observe"
    ANALYZE = "analyze"
    PROPOSE = "propose"
    SIMULATE = "simulate"
    REVIEW = "review"
    RECORD = "record"

@dataclass
class EvolutionProposal:
    """
    A proposed change to SROS itself.
    """
    id: str
    title: str
    description: str
    rationale: str
    stage: LoopStage
    
    # Targets
    target_files: List[str] = field(default_factory=list)
    target_modules: List[str] = field(default_factory=list)
    
    # Changes
    code_diffs: Dict[str, str] = field(default_factory=dict)  # file -> diff
    new_files: Dict[str, str] = field(default_factory=dict)   # file -> content
    deleted_files: List[str] = field(default_factory=list)
    
    # Validation
    test_results: Optional[Dict[str, Any]] = None
    simulation_results: Optional[Dict[str, Any]] = None
    
    # Review
    approved: bool = False
    reviewer: Optional[str] = None
    review_notes: str = ""
    
    # Metadata
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
