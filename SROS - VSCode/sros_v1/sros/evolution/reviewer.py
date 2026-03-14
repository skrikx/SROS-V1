"""
Evolution Reviewer

Handles the human-in-the-loop review process.
Generates a "Change Dossier" and requests approval.
"""
import logging
from typing import Dict, Any
from sros.evolution.types import EvolutionProposal

logger = logging.getLogger(__name__)

class EvolutionReviewer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.auto_approve = self.config.get("auto_approve", False)

    def request_approval(self, proposal: EvolutionProposal):
        """
        Generate Change Dossier and request approval.
        """
        dossier = self._generate_dossier(proposal)
        logger.info(f"\n{'='*40}\nCHANGE DOSSIER: {proposal.id}\n{'='*40}\n{dossier}\n{'='*40}")
        
        if self.auto_approve:
            logger.warning(f"Auto-approving proposal {proposal.id} (Configured)")
            proposal.approved = True
            proposal.reviewer = "auto_policy"
            proposal.review_notes = "Auto-approved by policy."
        else:
            # In a real CLI/UI, this would block or send a notification
            logger.info(f"Proposal {proposal.id} waiting for manual approval.")
            proposal.approved = False # Default to false
            proposal.reviewer = "pending"

    def _generate_dossier(self, proposal: EvolutionProposal) -> str:
        """Generate a markdown formatted dossier."""
        return f"""
## Title: {proposal.title}
**ID**: {proposal.id}
**Type**: {proposal.metadata.get('pain_point_type', 'generic')}
**Priority**: {proposal.metadata.get('priority', 'unknown')}

### Description
{proposal.description}

### Rationale
{proposal.rationale}

### Targets
Files: {', '.join(proposal.target_files)}
Modules: {', '.join(proposal.target_modules)}

### Simulation Results
Status: {proposal.simulation_results.get('status') if proposal.simulation_results else 'Not Run'}
Impact: {proposal.simulation_results.get('simulated_impact') if proposal.simulation_results else 'Unknown'}

### Validation
Tests Passed: {proposal.test_results is not None}
"""
