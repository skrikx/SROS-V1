"""
Evaluation Engine

Evaluates proposed policy changes and governance evolution.
Core decision-maker for policy evolution loop.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyProposal:
    """Represents a proposed policy change."""
    id: str
    change_type: str  # "add", "modify", "remove"
    policy_id: str
    policy_rule: Optional[Dict[str, Any]] = None
    rationale: str = ""
    impact_estimate: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class EvaluationResult:
    """Result of proposal evaluation."""
    proposal_id: str
    approved: bool
    confidence: float  # 0.0 to 1.0
    risk_score: float  # 0.0 to 1.0 (higher = more risky)
    rationale: str
    conditions: List[str] = None  # Conditions for approval
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.conditions is None:
            self.conditions = []


class EvaluationEngine:
    """
    Evaluates policy proposals for evolution.
    
    Features:
    - Proposal evaluation with risk assessment
    - Impact analysis on system behavior
    - Conflict detection with existing policies
    - Approval workflow management
    - Historical tracking of evaluations
    """
    
    def __init__(self):
        """Initialize evaluation engine."""
        self.proposals: Dict[str, PolicyProposal] = {}
        self.evaluations: Dict[str, EvaluationResult] = {}
        self.approval_history: List[Dict[str, Any]] = []
        
        # Evaluation metrics
        self.total_proposals = 0
        self.approved_count = 0
        self.rejected_count = 0
    
    def submit_proposal(
        self,
        proposal_id: str,
        change_type: str,
        policy_id: str,
        policy_rule: Optional[Dict[str, Any]] = None,
        rationale: str = ""
    ) -> PolicyProposal:
        """
        Submit a policy change proposal.
        
        Args:
            proposal_id: Unique proposal ID
            change_type: "add", "modify", or "remove"
            policy_id: ID of policy being changed
            policy_rule: New/modified policy rule (for add/modify)
            rationale: Explanation for the change
        
        Returns:
            Submitted PolicyProposal
        """
        proposal = PolicyProposal(
            id=proposal_id,
            change_type=change_type,
            policy_id=policy_id,
            policy_rule=policy_rule,
            rationale=rationale
        )
        
        self.proposals[proposal_id] = proposal
        self.total_proposals += 1
        
        logger.info(f"Submitted proposal {proposal_id}: {change_type} {policy_id}")
        
        return proposal
    
    def evaluate_proposal(
        self,
        proposal_id: str,
        policy_engine,
        existing_policies: List[Any] = None
    ) -> EvaluationResult:
        """
        Evaluate a submitted proposal.
        
        Args:
            proposal_id: ID of proposal to evaluate
            policy_engine: Current PolicyEngine instance for conflict checking
            existing_policies: List of existing policies
        
        Returns:
            EvaluationResult with approval status
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = self.proposals[proposal_id]
        
        # Run evaluation checklist
        approval = True
        confidence = 0.9
        risk_score = 0.0
        conditions = []
        
        # Check 1: Validate proposal format
        if not self._validate_proposal_format(proposal):
            approval = False
            confidence = 0.1
            risk_score = 0.8
        
        # Check 2: Detect conflicts with existing policies
        conflicts = self._detect_policy_conflicts(proposal, existing_policies or [])
        if conflicts:
            risk_score += 0.2
            confidence -= 0.1
            conditions.append(f"Conflicts detected: {', '.join(conflicts)}")
        
        # Check 3: Assess impact
        impact = self._assess_impact(proposal, policy_engine)
        if impact.get("risk_level") == "high":
            risk_score += 0.3
            confidence -= 0.2
            conditions.append("High-impact change - requires review")
        
        # Check 4: Sanity checks
        if not self._sanity_checks(proposal):
            approval = False
            confidence = 0.0
            risk_score = 1.0
            conditions.append("Failed sanity checks")
        
        # Create evaluation result
        result = EvaluationResult(
            proposal_id=proposal_id,
            approved=approval,
            confidence=max(0.0, min(1.0, confidence)),
            risk_score=max(0.0, min(1.0, risk_score)),
            rationale=self._generate_rationale(proposal, conditions),
            conditions=conditions
        )
        
        self.evaluations[proposal_id] = result
        
        if approval:
            self.approved_count += 1
        else:
            self.rejected_count += 1
        
        logger.info(
            f"Evaluated proposal {proposal_id}: "
            f"approved={approval}, confidence={result.confidence:.2f}, "
            f"risk={result.risk_score:.2f}"
        )
        
        return result
    
    def _validate_proposal_format(self, proposal: PolicyProposal) -> bool:
        """Validate proposal has required fields."""
        if not proposal.id or not proposal.change_type:
            return False
        
        if proposal.change_type not in ["add", "modify", "remove"]:
            return False
        
        if proposal.change_type in ["add", "modify"] and not proposal.policy_rule:
            return False
        
        return True
    
    def _detect_policy_conflicts(
        self,
        proposal: PolicyProposal,
        existing_policies: List[Any]
    ) -> List[str]:
        """
        Detect conflicts between proposal and existing policies.
        
        Args:
            proposal: Policy proposal
            existing_policies: List of existing policies
        
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # If modifying/removing, check if policy exists
        if proposal.change_type in ["modify", "remove"]:
            exists = any(p.id == proposal.policy_id for p in existing_policies)
            if not exists:
                conflicts.append(f"Policy {proposal.policy_id} not found")
        
        # If adding, check for duplicates
        if proposal.change_type == "add":
            exists = any(p.id == proposal.policy_id for p in existing_policies)
            if exists:
                conflicts.append(f"Policy {proposal.policy_id} already exists")
        
        return conflicts
    
    def _assess_impact(
        self,
        proposal: PolicyProposal,
        policy_engine
    ) -> Dict[str, Any]:
        """
        Assess potential impact of proposal.
        
        Args:
            proposal: Policy proposal
            policy_engine: Current PolicyEngine
        
        Returns:
            Impact assessment dict
        """
        # Simplified impact assessment
        impact = {
            "risk_level": "low",
            "affected_agents": [],
            "affected_resources": []
        }
        
        if proposal.policy_rule:
            rule = proposal.policy_rule
            
            # Assess scope
            if "resource" in rule and "*" in str(rule.get("resource", "")):
                impact["risk_level"] = "high"
                impact["affected_resources"].append("*")
            
            # Assess if restrictive change (higher risk)
            if proposal.change_type == "add" and rule.get("effect") == "deny":
                impact["risk_level"] = "medium"
        
        return impact
    
    def _sanity_checks(self, proposal: PolicyProposal) -> bool:
        """Perform basic sanity checks on proposal."""
        if proposal.policy_rule is None and proposal.change_type != "remove":
            return False
        
        # More checks could go here
        return True
    
    def _generate_rationale(
        self,
        proposal: PolicyProposal,
        conditions: List[str]
    ) -> str:
        """Generate evaluation rationale."""
        parts = [f"Proposal: {proposal.change_type} {proposal.policy_id}"]
        
        if proposal.rationale:
            parts.append(f"Justification: {proposal.rationale}")
        
        if conditions:
            parts.append(f"Conditions: {'; '.join(conditions)}")
        
        return " | ".join(parts)
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """
        Approve a proposal for implementation.
        
        Args:
            proposal_id: ID of proposal to approve
        
        Returns:
            True if approved
        """
        if proposal_id not in self.evaluations:
            logger.warning(f"Evaluation not found for {proposal_id}")
            return False
        
        evaluation = self.evaluations[proposal_id]
        
        self.approval_history.append({
            "proposal_id": proposal_id,
            "approved": True,
            "timestamp": datetime.now(),
            "confidence": evaluation.confidence
        })
        
        logger.info(f"Approved proposal {proposal_id}")
        return True
    
    def reject_proposal(self, proposal_id: str) -> bool:
        """
        Reject a proposal.
        
        Args:
            proposal_id: ID of proposal to reject
        
        Returns:
            True if rejected
        """
        if proposal_id not in self.evaluations:
            logger.warning(f"Evaluation not found for {proposal_id}")
            return False
        
        self.approval_history.append({
            "proposal_id": proposal_id,
            "approved": False,
            "timestamp": datetime.now()
        })
        
        logger.info(f"Rejected proposal {proposal_id}")
        return True
    
    def get_proposal(self, proposal_id: str) -> Optional[PolicyProposal]:
        """Get proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def get_evaluation(self, proposal_id: str) -> Optional[EvaluationResult]:
        """Get evaluation result by proposal ID."""
        return self.evaluations.get(proposal_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get evaluation engine statistics."""
        return {
            "total_proposals": self.total_proposals,
            "approved": self.approved_count,
            "rejected": self.rejected_count,
            "pending": self.total_proposals - self.approved_count - self.rejected_count,
            "approval_rate": (
                self.approved_count / self.total_proposals
                if self.total_proposals > 0
                else 0.0
            )
        }
