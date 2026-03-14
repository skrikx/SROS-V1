"""
Reflection Engine

Enables self-observation and learning from system behavior.
Core of MirrorOS for autonomous evolution.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class Observation:
    """Represents a system observation."""
    id: str
    timestamp: datetime
    component: str  # e.g., "agent/tester", "daemon/scheduler"
    metric: str  # e.g., "success_rate", "response_time"
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def age_seconds(self) -> float:
        """Get observation age in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class Pattern:
    """Represents discovered pattern in observations."""
    id: str
    name: str
    description: str
    condition: str  # Pattern condition (e.g., "success_rate < 0.8")
    impact: str  # Impact assessment
    confidence: float  # 0.0 to 1.0
    discovered_at: datetime = None
    occurrences: int = 0
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()


class ReflectionEngine:
    """
    Enables self-observation and pattern discovery.
    
    Features:
    - Real-time metric collection
    - Pattern detection in system behavior
    - Anomaly identification
    - Performance trend analysis
    - Learning from execution traces
    - Evolution opportunity identification
    """
    
    def __init__(self, history_window: int = 3600):
        """
        Initialize reflection engine.
        
        Args:
            history_window: How many seconds of history to maintain
        """
        self.history_window = history_window
        self.observations: List[Observation] = []
        self.patterns: Dict[str, Pattern] = {}
        self.anomalies: List[Dict[str, Any]] = []
        self.learning_cache: Dict[str, Any] = {}
    
    def observe(
        self,
        component: str,
        metric: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Observation:
        """
        Record an observation.
        
        Args:
            component: Component name
            metric: Metric name
            value: Metric value
            metadata: Optional metadata
        
        Returns:
            Created Observation
        """
        import uuid
        observation = Observation(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            component=component,
            metric=metric,
            value=value,
            metadata=metadata or {}
        )
        
        self.observations.append(observation)
        
        # Trim old observations
        cutoff = datetime.now() - timedelta(seconds=self.history_window)
        self.observations = [o for o in self.observations if o.timestamp > cutoff]
        
        logger.debug(f"Observed: {component}/{metric} = {value}")
        
        return observation
    
    def discover_patterns(self) -> List[Pattern]:
        """
        Analyze observations to discover patterns.
        
        Returns:
            List of discovered patterns
        """
        discovered = []
        
        # Group observations by component/metric
        component_metrics: Dict[str, List[Observation]] = {}
        
        for obs in self.observations:
            key = f"{obs.component}/{obs.metric}"
            if key not in component_metrics:
                component_metrics[key] = []
            component_metrics[key].append(obs)
        
        # Analyze each component/metric pair
        for key, observations in component_metrics.items():
            if len(observations) < 3:
                continue
            
            values = [o.value for o in observations]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            # Detect patterns
            if max_val > avg * 1.5:
                # High variance pattern
                pattern = Pattern(
                    id=f"pattern_variance_{key}",
                    name=f"High Variance: {key}",
                    description=f"Metric {key} shows high variance",
                    condition=f"max({key}) > 1.5 * avg({key})",
                    impact="Potential instability in component",
                    confidence=0.7
                )
                
                if pattern.id not in self.patterns:
                    self.patterns[pattern.id] = pattern
                    discovered.append(pattern)
                else:
                    self.patterns[pattern.id].occurrences += 1
            
            if min_val < avg * 0.5:
                # Low performance pattern
                pattern = Pattern(
                    id=f"pattern_low_perf_{key}",
                    name=f"Low Performance: {key}",
                    description=f"Metric {key} has low values",
                    condition=f"min({key}) < 0.5 * avg({key})",
                    impact="Component underperforming",
                    confidence=0.6
                )
                
                if pattern.id not in self.patterns:
                    self.patterns[pattern.id] = pattern
                    discovered.append(pattern)
                else:
                    self.patterns[pattern.id].occurrences += 1
        
        logger.info(f"Discovered {len(discovered)} patterns")
        return discovered
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalous observations.
        
        Returns:
            List of anomalies
        """
        anomalies = []
        
        # Group by component/metric
        component_metrics: Dict[str, List[float]] = {}
        
        for obs in self.observations:
            key = f"{obs.component}/{obs.metric}"
            if key not in component_metrics:
                component_metrics[key] = []
            component_metrics[key].append(obs.value)
        
        # Detect outliers using simple statistical method
        for key, values in component_metrics.items():
            if len(values) < 3:
                continue
            
            avg = sum(values) / len(values)
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            std_dev = variance ** 0.5
            
            # Values > 3 std devs are anomalies
            for i, obs in enumerate(self.observations):
                if f"{obs.component}/{obs.metric}" == key:
                    z_score = abs((obs.value - avg) / (std_dev + 0.0001))
                    if z_score > 3:
                        anomaly = {
                            "observation_id": obs.id,
                            "component": obs.component,
                            "metric": obs.metric,
                            "value": obs.value,
                            "expected_avg": avg,
                            "z_score": z_score,
                            "timestamp": obs.timestamp
                        }
                        anomalies.append(anomaly)
                        logger.warning(f"Anomaly detected: {key} = {obs.value} (z-score: {z_score:.2f})")
        
        self.anomalies = anomalies
        return anomalies
    
    def analyze_performance_trend(self, component: str, metric: str) -> Dict[str, Any]:
        """
        Analyze performance trend for a metric.
        
        Args:
            component: Component name
            metric: Metric name
        
        Returns:
            Trend analysis
        """
        key = f"{component}/{metric}"
        relevant_obs = [
            o for o in self.observations
            if f"{o.component}/{o.metric}" == key
        ]
        
        if len(relevant_obs) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        relevant_obs.sort(key=lambda o: o.timestamp)
        
        # Calculate trend
        values = [o.value for o in relevant_obs]
        
        if len(values) >= 2:
            # Simple linear trend: last vs first
            if values[-1] > values[0]:
                trend_direction = "improving"
            elif values[-1] < values[0]:
                trend_direction = "degrading"
            else:
                trend_direction = "flat"

            trend_magnitude = abs(values[-1] - values[0]) / (abs(values[0]) + 0.0001)
        else:
            trend_direction = "insufficient_data"
            trend_magnitude = 0.0
        
        return {
            "component": component,
            "metric": metric,
            "observations": len(values),
            "current_value": values[-1],
            "average_value": sum(values) / len(values),
            "min_value": min(values),
            "max_value": max(values),
            "trend": trend_direction,
            "trend_magnitude": trend_magnitude
        }
    
    def get_evolution_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for system evolution.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze patterns for opportunities
        for pattern in self.patterns.values():
            if pattern.occurrences > 2:
                recommendation = {
                    "pattern": pattern.name,
                    "issue": pattern.description,
                    "action": f"Investigate and mitigate: {pattern.impact}",
                    "priority": "high" if pattern.confidence > 0.8 else "medium",
                    "confidence": pattern.confidence
                }
                recommendations.append(recommendation)
        
        # Analyze anomalies
        if len(self.anomalies) > 0:
            recommendations.append({
                "pattern": "Anomalous Behavior",
                "issue": f"{len(self.anomalies)} anomalies detected in system",
                "action": "Review and adjust tolerances or investigate root cause",
                "priority": "high",
                "confidence": 0.9
            })
        
        logger.info(f"Generated {len(recommendations)} evolution recommendations")
        return recommendations
    
    def get_observation_summary(self) -> Dict[str, Any]:
        """Get summary of observations."""
        if not self.observations:
            return {"total_observations": 0}
        
        components = set(o.component for o in self.observations)
        metrics = set(o.metric for o in self.observations)
        
        return {
            "total_observations": len(self.observations),
            "components": list(components),
            "metrics": list(metrics),
            "patterns_discovered": len(self.patterns),
            "anomalies_detected": len(self.anomalies),
            "oldest_observation": min(o.timestamp for o in self.observations).isoformat(),
            "newest_observation": max(o.timestamp for o in self.observations).isoformat()
        }
    
    def clear_history(self):
        """Clear observation history."""
        self.observations = []
        self.patterns = {}
        self.anomalies = []
        logger.info("Cleared reflection engine history")
