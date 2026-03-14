"""
Risk Registry

Maintains registry of known risks and mitigation strategies.
Enables risk-aware policy evolution.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskEntry:
    """Represents a known risk."""
    id: str
    name: str
    description: str
    level: RiskLevel
    category: str  # e.g., "security", "performance", "data_loss", "policy_conflict"
    mitigation_strategies: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    occurrence_count: int = 0
    last_triggered: Optional[datetime] = None
    active: bool = True
    
    def __post_init__(self):
        if isinstance(self.level, str):
            self.level = RiskLevel(self.level)


@dataclass
class Mitigation:
    """Risk mitigation action."""
    id: str
    risk_id: str
    strategy: str
    status: str  # "proposed", "approved", "implemented", "verified"
    cost: float = 0.0
    effectiveness_estimate: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RiskRegistry:
    """
    Registry of known risks and mitigations.
    
    Features:
    - Risk database with severity levels
    - Mitigation strategy tracking
    - Risk activation/deactivation
    - Occurrence monitoring
    - Policy-risk association
    """
    
    def __init__(self):
        """Initialize risk registry."""
        self.risks: Dict[str, RiskEntry] = {}
        self.mitigations: Dict[str, Mitigation] = {}
        self.risk_policies: Dict[str, List[str]] = {}  # risk_id -> policy_ids
        self.policy_risks: Dict[str, List[str]] = {}  # policy_id -> risk_ids
    
    def register_risk(
        self,
        risk_id: str,
        name: str,
        description: str,
        level: RiskLevel,
        category: str,
        affected_components: List[str] = None
    ) -> RiskEntry:
        """
        Register a known risk.
        
        Args:
            risk_id: Unique risk ID
            name: Risk name
            description: Risk description
            level: Risk severity level
            category: Risk category
            affected_components: Components affected by this risk
        
        Returns:
            Created RiskEntry
        """
        risk = RiskEntry(
            id=risk_id,
            name=name,
            description=description,
            level=level if isinstance(level, RiskLevel) else RiskLevel(level),
            category=category,
            affected_components=affected_components or []
        )
        
        self.risks[risk_id] = risk
        self.risk_policies[risk_id] = []
        
        logger.info(f"Registered risk {risk_id} ({level.value}): {name}")
        return risk
    
    def add_mitigation_strategy(
        self,
        risk_id: str,
        strategy: str
    ) -> bool:
        """
        Add mitigation strategy to a risk.
        
        Args:
            risk_id: Risk ID
            strategy: Mitigation strategy description
        
        Returns:
            True if added
        """
        if risk_id not in self.risks:
            logger.warning(f"Risk {risk_id} not found")
            return False
        
        risk = self.risks[risk_id]
        if strategy not in risk.mitigation_strategies:
            risk.mitigation_strategies.append(strategy)
            logger.debug(f"Added mitigation strategy to {risk_id}")
        
        return True
    
    def create_mitigation(
        self,
        mitigation_id: str,
        risk_id: str,
        strategy: str,
        cost: float = 0.0,
        effectiveness: float = 0.5
    ) -> Mitigation:
        """
        Create a mitigation action for a risk.
        
        Args:
            mitigation_id: Unique mitigation ID
            risk_id: Risk being mitigated
            strategy: Strategy used
            cost: Estimated cost
            effectiveness: Estimated effectiveness (0-1)
        
        Returns:
            Created Mitigation
        """
        mitigation = Mitigation(
            id=mitigation_id,
            risk_id=risk_id,
            strategy=strategy,
            status="proposed",
            cost=cost,
            effectiveness_estimate=effectiveness
        )
        
        self.mitigations[mitigation_id] = mitigation
        logger.info(f"Created mitigation {mitigation_id} for risk {risk_id}")
        
        return mitigation
    
    def approve_mitigation(self, mitigation_id: str) -> bool:
        """Approve a mitigation."""
        if mitigation_id not in self.mitigations:
            return False
        
        self.mitigations[mitigation_id].status = "approved"
        logger.info(f"Approved mitigation {mitigation_id}")
        return True
    
    def implement_mitigation(self, mitigation_id: str) -> bool:
        """Mark mitigation as implemented."""
        if mitigation_id not in self.mitigations:
            return False
        
        self.mitigations[mitigation_id].status = "implemented"
        logger.info(f"Implemented mitigation {mitigation_id}")
        return True
    
    def associate_policy_with_risk(
        self,
        policy_id: str,
        risk_id: str
    ) -> bool:
        """
        Associate a policy with a risk (policy addresses this risk).
        
        Args:
            policy_id: Policy ID
            risk_id: Risk ID
        
        Returns:
            True if associated
        """
        if risk_id not in self.risks:
            logger.warning(f"Risk {risk_id} not found")
            return False
        
        if risk_id not in self.risk_policies:
            self.risk_policies[risk_id] = []
        
        if policy_id not in self.risk_policies[risk_id]:
            self.risk_policies[risk_id].append(policy_id)
        
        if policy_id not in self.policy_risks:
            self.policy_risks[policy_id] = []
        
        if risk_id not in self.policy_risks[policy_id]:
            self.policy_risks[policy_id].append(risk_id)
        
        logger.debug(f"Associated policy {policy_id} with risk {risk_id}")
        return True
    
    def record_risk_occurrence(self, risk_id: str) -> bool:
        """
        Record an occurrence of a known risk.
        
        Args:
            risk_id: Risk ID
        
        Returns:
            True if recorded
        """
        if risk_id not in self.risks:
            logger.warning(f"Risk {risk_id} not found")
            return False
        
        risk = self.risks[risk_id]
        risk.occurrence_count += 1
        risk.last_triggered = datetime.now()
        
        logger.warning(
            f"Risk occurrence recorded: {risk.name} "
            f"(count: {risk.occurrence_count})"
        )
        
        return True
    
    def get_risks_by_level(self, level: RiskLevel) -> List[RiskEntry]:
        """Get all risks at a specific level."""
        return [
            r for r in self.risks.values()
            if r.level == level and r.active
        ]
    
    def get_active_risks(self) -> List[RiskEntry]:
        """Get all active risks."""
        return [r for r in self.risks.values() if r.active]
    
    def get_risks_for_policy(self, policy_id: str) -> List[RiskEntry]:
        """Get risks associated with a policy."""
        risk_ids = self.policy_risks.get(policy_id, [])
        return [self.risks[rid] for rid in risk_ids if rid in self.risks]
    
    def get_policies_for_risk(self, risk_id: str) -> List[str]:
        """Get policies addressing a risk."""
        return self.risk_policies.get(risk_id, [])
    
    def assess_policy_risk_profile(self, policy_id: str) -> Dict[str, Any]:
        """
        Assess overall risk profile for a policy.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            Risk profile assessment
        """
        associated_risks = self.get_risks_for_policy(policy_id)
        
        risk_scores = {
            RiskLevel.CRITICAL: 1.0,
            RiskLevel.HIGH: 0.75,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.25
        }
        
        total_risk = sum(
            risk_scores.get(r.level, 0.0)
            for r in associated_risks
        )
        
        avg_risk = total_risk / len(associated_risks) if associated_risks else 0.0
        
        return {
            "policy_id": policy_id,
            "associated_risks": len(associated_risks),
            "risk_levels": {level.value: len(self.get_risks_by_level(level)) for level in RiskLevel},
            "total_risk_score": total_risk,
            "average_risk_score": avg_risk,
            "risk_level": (
                "critical" if avg_risk >= 0.75 else
                "high" if avg_risk >= 0.5 else
                "medium" if avg_risk >= 0.25 else
                "low"
            )
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        active_risks = self.get_active_risks()
        
        return {
            "total_risks": len(self.risks),
            "active_risks": len(active_risks),
            "total_mitigations": len(self.mitigations),
            "policy_associations": len(self.policy_risks),
            "risks_by_level": {
                level.value: len(self.get_risks_by_level(level))
                for level in RiskLevel
            },
            "total_occurrences": sum(r.occurrence_count for r in self.risks.values())
        }
