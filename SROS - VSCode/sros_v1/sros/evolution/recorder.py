"""
Evolution Recorder

Adapter that connects the Ouroboros Loop to MirrorOS Witness.
Records the entire evolution cycle as a trace for audit and replay.
"""
import logging
import time
from typing import Dict, Any
from sros.evolution.types import EvolutionProposal
from sros.mirroros.witness import Witness

logger = logging.getLogger(__name__)

class EvolutionRecorder:
    def __init__(self, witness: Witness):
        self.witness = witness

    def record(self, proposal: EvolutionProposal):
        """
        Record the final state of a proposal to MirrorOS.
        """
        logger.info(f"Recording proposal trace: {proposal.id}")
        
        trace_payload = {
            "proposal_id": proposal.id,
            "title": proposal.title,
            "stage": proposal.stage.value,
            "approved": proposal.approved,
            "reviewer": proposal.reviewer,
            "created_at": proposal.created_at,
            "recorded_at": time.time(),
            "metadata": proposal.metadata
        }
        
        self.witness.record("evolution.cycle_complete", trace_payload)
