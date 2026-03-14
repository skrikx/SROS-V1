"""
Ouroboros - SROS Self-Evolution Loop

The controlled self-improvement system where SROS analyzes its own code,
telemetry, and traces to propose improvements.

CRITICAL: This loop is powerful and dangerous. It must be:
- Sandboxed
- Governed by strict policies
- Subject to human approval gates
- Fully auditable via MirrorOS
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import logging
from enum import Enum

from .simulator import EvolutionSimulator
from .recorder import EvolutionRecorder
from .reviewer import EvolutionReviewer
from .types import EvolutionProposal, LoopStage
from sros.runtime.agents.srx_simulation_agent import SRXSimulationAgent
from sros.mirroros.witness import Witness

logger = logging.getLogger(__name__)

class OuroborosLoop:
    """
    The self-evolution loop orchestrator.
    
    Coordinates all stages from observation to recording.
    Enforces safety constraints and human approval gates.
    """
    
    def __init__(self, config: Dict[str, Any] = None, kernel_context=None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.max_concurrent_proposals = self.config.get("max_concurrent_proposals", 3)
        self.require_human_approval = self.config.get("require_human_approval", True)
        
        # Components (will be injected or initialized)
        self.observer = None
        self.analyzer = None
        self.proposer = None
        
        # Initialize new components if kernel context is available
        if kernel_context:
            # Simulator
            sim_agent = SRXSimulationAgent(kernel_context)
            self.simulator = EvolutionSimulator(sim_agent)
            
            # Recorder
            # Assuming kernel_context has access to witness or we create one
            # For now, we'll mock or assume it's passed. 
            # Ideally, Witness should be a singleton or service.
            # Here we create a dummy one if needed or use what's available.
            if hasattr(kernel_context, 'witness'):
                self.recorder = EvolutionRecorder(kernel_context.witness)
            else:
                 # Fallback/Mock for now if witness isn't readily available on context
                 # In a real system, this would be strictly wired.
                 pass 
        else:
            self.simulator = None
            self.recorder = None
            
        self.reviewer = EvolutionReviewer(config={"auto_approve": not self.require_human_approval})
        
        # State
        self.active_proposals: List[EvolutionProposal] = []
        self.proposal_history: List[EvolutionProposal] = []
        
        logger.info(f"Ouroboros Loop initialized (enabled={self.enabled})")
    
    def run_cycle(self) -> List[EvolutionProposal]:
        """
        Run one complete evolution cycle.
        
        Returns:
            List of proposals created/updated in this cycle
        """
        if not self.enabled:
            logger.warning("Ouroboros Loop is disabled")
            return []
        
        if not self._check_safety_constraints():
            logger.error("Safety constraints violated. Aborting cycle.")
            return []
        
        logger.info("Starting Ouroboros evolution cycle")
        
        # Stage 1: Observe
        observations = self._observe()
        
        # Stage 2: Analyze
        pain_points = self._analyze(observations)
        
        # Stage 3: Propose
        proposals = self._propose(pain_points)
        
        # Stage 4: Simulate
        for proposal in proposals:
            self._simulate(proposal)
        
        # Stage 5: Review
        for proposal in proposals:
            self._review(proposal)
        
        # Stage 6: Record
        for proposal in proposals:
            self._record(proposal)
        
        logger.info(f"Evolution cycle complete. {len(proposals)} proposals generated.")
        return proposals
    
    def _observe(self) -> Dict[str, Any]:
        """Stage 1: Collect observations."""
        if not self.observer:
            logger.warning("Observer not configured")
            return {}
        
        logger.info("[OBSERVE] Collecting telemetry, traces, and code signals")
        return self.observer.collect()
    
    def _analyze(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Stage 2: Analyze observations for improvement opportunities."""
        if not self.analyzer:
            logger.warning("Analyzer not configured")
            return []
        
        logger.info("[ANALYZE] Synthesizing pain points and opportunities")
        return self.analyzer.analyze(observations)
    
    def _propose(self, pain_points: List[Dict[str, Any]]) -> List[EvolutionProposal]:
        """Stage 3: Generate improvement proposals."""
        if not self.proposer:
            logger.warning("Proposer not configured")
            return []
        
        logger.info(f"[PROPOSE] Generating proposals for {len(pain_points)} pain points")
        proposals = self.proposer.generate_proposals(pain_points)
        
        # Add to active proposals
        self.active_proposals.extend(proposals)
        
        return proposals
    
    def _simulate(self, proposal: EvolutionProposal):
        """Stage 4: Simulate proposal in sandbox."""
        if not self.simulator:
            logger.warning("Simulator not configured")
            return
        
        logger.info(f"[SIMULATE] Testing proposal: {proposal.id}")
        proposal.simulation_results = self.simulator.run(proposal)
        proposal.stage = LoopStage.SIMULATE
    
    def _review(self, proposal: EvolutionProposal):
        """Stage 5: Human/governance review."""
        if not self.reviewer:
            logger.warning("Reviewer not configured")
            return
        
        logger.info(f"[REVIEW] Submitting proposal for review: {proposal.id}")
        
        if self.require_human_approval:
            # Create review dossier and wait for human approval
            self.reviewer.request_approval(proposal)
        else:
            # Auto-approve if configured (DANGEROUS)
            proposal.approved = True
            proposal.reviewer = "auto"
        
        proposal.stage = LoopStage.REVIEW
    
    def _record(self, proposal: EvolutionProposal):
        """Stage 6: Record to MirrorOS."""
        if not self.recorder:
            logger.warning("Recorder not configured")
            return
        
        logger.info(f"[RECORD] Recording proposal to MirrorOS: {proposal.id}")
        self.recorder.record(proposal)
        
        # Move to history
        self.proposal_history.append(proposal)
        if proposal in self.active_proposals:
            self.active_proposals.remove(proposal)
        
        proposal.stage = LoopStage.RECORD
    
    def _check_safety_constraints(self) -> bool:
        """
        Check safety constraints before running cycle.
        
        Returns:
            True if safe to proceed
        """
        # Check max concurrent proposals
        if len(self.active_proposals) >= self.max_concurrent_proposals:
            logger.warning(f"Max concurrent proposals reached: {len(self.active_proposals)}")
            return False
        
        # Check if loop is in emergency stop state
        if self.config.get("emergency_stop", False):
            logger.error("Emergency stop activated")
            return False
        
        return True
    
    def emergency_stop(self):
        """Immediately halt all evolution activities."""
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.enabled = False
        self.config["emergency_stop"] = True
        
        # Clear active proposals
        self.active_proposals.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status."""
        return {
            "enabled": self.enabled,
            "active_proposals": len(self.active_proposals),
            "total_proposals": len(self.proposal_history),
            "max_concurrent": self.max_concurrent_proposals,
            "require_approval": self.require_human_approval,
            "emergency_stop": self.config.get("emergency_stop", False)
        }
