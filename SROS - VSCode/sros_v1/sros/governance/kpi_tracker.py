"""
KPI Tracker

Tracks Key Performance Indicators (KPIs) for SROS.
Metrics include: Latency, Success Rates, Cost Efficiency, Uptime.
Feeds into Governance Dashboard.
"""
import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class KPIEvent:
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)

class KPITracker:
    def __init__(self):
        self.events: List[KPIEvent] = []
        self.aggregates: Dict[str, Dict[str, float]] = {}

    def record(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a KPI metric."""
        event = KPIEvent(name=name, value=value, tags=tags or {})
        self.events.append(event)
        self._update_aggregate(name, value)
        logger.debug(f"KPI Recorded: {name}={value}")

    def get_metrics(self, name: str = None) -> Dict[str, Any]:
        """Get current metrics, optionally filtered by name."""
        if name:
            return self.aggregates.get(name, {})
        return self.aggregates

    def _update_aggregate(self, name: str, value: float):
        """Update running averages/stats."""
        if name not in self.aggregates:
            self.aggregates[name] = {"count": 0, "sum": 0.0, "avg": 0.0, "min": value, "max": value}
        
        agg = self.aggregates[name]
        agg["count"] += 1
        agg["sum"] += value
        agg["avg"] = agg["sum"] / agg["count"]
        agg["min"] = min(agg["min"], value)
        agg["max"] = max(agg["max"], value)
