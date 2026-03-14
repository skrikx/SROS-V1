"""
Snapshot Manager

Manages system state snapshots for time-travel debugging and recovery.
Enables rollback and historical analysis.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Snapshot:
    """Represents a system state snapshot."""
    id: str
    timestamp: datetime
    label: str  # e.g., "before_policy_change", "post_deployment"
    components: Dict[str, Any]  # component_name -> state
    metrics: Dict[str, float]  # metric_name -> value
    policies: List[str]  # Active policy IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def age_seconds(self) -> float:
        """Get snapshot age in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


class SnapshotManager:
    """
    Manages system state snapshots.
    
    Features:
    - Automatic snapshot creation at key events
    - Manual snapshot checkpoints
    - State comparison between snapshots
    - Recovery/rollback support
    - Time-series state analysis
    - Storage management and retention policies
    """
    
    def __init__(self, max_snapshots: int = 100, retention_days: int = 7):
        """
        Initialize snapshot manager.
        
        Args:
            max_snapshots: Maximum number of snapshots to retain
            retention_days: Retention period in days
        """
        self.snapshots: Dict[str, Snapshot] = {}
        self.max_snapshots = max_snapshots
        self.retention_days = retention_days
        self.snapshot_index: List[str] = []  # Ordered list of snapshot IDs
    
    def create_snapshot(
        self,
        snapshot_id: str,
        label: str,
        components: Dict[str, Any],
        metrics: Dict[str, float],
        policies: List[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Snapshot:
        """
        Create a system state snapshot.
        
        Args:
            snapshot_id: Unique snapshot ID
            label: Descriptive label
            components: Component states
            metrics: System metrics
            policies: Active policy IDs
            metadata: Optional metadata
        
        Returns:
            Created Snapshot
        """
        snapshot = Snapshot(
            id=snapshot_id,
            timestamp=datetime.now(),
            label=label,
            components=components.copy(),
            metrics=metrics.copy(),
            policies=policies or [],
            metadata=metadata or {}
        )
        
        self.snapshots[snapshot_id] = snapshot
        self.snapshot_index.append(snapshot_id)
        
        # Enforce retention policies
        self._enforce_retention()
        
        logger.info(f"Created snapshot {snapshot_id}: {label}")
        
        return snapshot
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get snapshot by ID."""
        return self.snapshots.get(snapshot_id)
    
    def list_snapshots(self, limit: int = None) -> List[Snapshot]:
        """
        List snapshots in reverse chronological order.
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of snapshots
        """
        # Get in reverse order (most recent first)
        ids = reversed(self.snapshot_index)
        
        snapshots = [self.snapshots[sid] for sid in ids if sid in self.snapshots]
        
        if limit:
            return snapshots[:limit]
        
        return snapshots
    
    def _enforce_retention(self):
        """Enforce retention policies (max snapshots and age)."""
        from datetime import timedelta
        
        # Remove old snapshots by age
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        to_remove = []
        for sid in self.snapshot_index:
            if sid in self.snapshots:
                if self.snapshots[sid].timestamp < cutoff:
                    to_remove.append(sid)
        
        for sid in to_remove:
            del self.snapshots[sid]
            self.snapshot_index.remove(sid)
            logger.debug(f"Removed old snapshot: {sid}")
        
        # Enforce max snapshot count
        while len(self.snapshots) > self.max_snapshots:
            # Remove oldest
            oldest_id = self.snapshot_index[0]
            del self.snapshots[oldest_id]
            self.snapshot_index.remove(oldest_id)
            logger.debug(f"Removed excess snapshot: {oldest_id}")
    
    def compare_snapshots(
        self,
        snapshot_id_1: str,
        snapshot_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two snapshots to identify changes.
        
        Args:
            snapshot_id_1: First snapshot ID
            snapshot_id_2: Second snapshot ID
        
        Returns:
            Comparison report
        """
        snap1 = self.get_snapshot(snapshot_id_1)
        snap2 = self.get_snapshot(snapshot_id_2)
        
        if not snap1 or not snap2:
            return {"error": "Snapshot not found"}
        
        changes = {
            "snapshot_1_id": snapshot_id_1,
            "snapshot_2_id": snapshot_id_2,
            "time_difference_seconds": (snap2.timestamp - snap1.timestamp).total_seconds(),
            "component_changes": {},
            "metric_changes": {},
            "policy_changes": {"added": [], "removed": []}
        }
        
        # Compare components
        all_components = set(snap1.components.keys()) | set(snap2.components.keys())
        for component in all_components:
            state1 = snap1.components.get(component)
            state2 = snap2.components.get(component)
            
            if state1 != state2:
                changes["component_changes"][component] = {
                    "before": state1,
                    "after": state2
                }
        
        # Compare metrics
        all_metrics = set(snap1.metrics.keys()) | set(snap2.metrics.keys())
        for metric in all_metrics:
            val1 = snap1.metrics.get(metric, 0.0)
            val2 = snap2.metrics.get(metric, 0.0)
            
            if val1 != val2:
                percent_change = ((val2 - val1) / (abs(val1) + 0.0001)) * 100
                changes["metric_changes"][metric] = {
                    "before": val1,
                    "after": val2,
                    "percent_change": percent_change
                }
        
        # Compare policies
        policies1 = set(snap1.policies)
        policies2 = set(snap2.policies)
        
        changes["policy_changes"]["added"] = list(policies2 - policies1)
        changes["policy_changes"]["removed"] = list(policies1 - policies2)
        
        logger.info(f"Compared snapshots {snapshot_id_1} and {snapshot_id_2}")
        
        return changes
    
    def get_metric_history(self, metric_name: str) -> List[Dict[str, Any]]:
        """
        Get historical values for a metric.
        
        Args:
            metric_name: Metric name
        
        Returns:
            List of (timestamp, value) pairs
        """
        history = []
        
        for snapshot in self.list_snapshots():
            if metric_name in snapshot.metrics:
                history.append({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "value": snapshot.metrics[metric_name],
                    "snapshot_id": snapshot.id,
                    "label": snapshot.label
                })
        
        return history
    
    def find_snapshot_by_label(self, label_pattern: str) -> List[Snapshot]:
        """
        Find snapshots by label pattern.
        
        Args:
            label_pattern: Label pattern to match
        
        Returns:
            List of matching snapshots
        """
        return [
            snap for snap in self.snapshots.values()
            if label_pattern.lower() in snap.label.lower()
        ]
    
    def tag_snapshot(self, snapshot_id: str, tag: str):
        """Add tag/label to existing snapshot."""
        if snapshot_id in self.snapshots:
            snapshot = self.snapshots[snapshot_id]
            if "tags" not in snapshot.metadata:
                snapshot.metadata["tags"] = []
            if tag not in snapshot.metadata["tags"]:
                snapshot.metadata["tags"].append(tag)
                logger.debug(f"Tagged snapshot {snapshot_id} with '{tag}'")
    
    def export_snapshot(self, snapshot_id: str) -> Optional[str]:
        """
        Export snapshot as JSON string.
        
        Args:
            snapshot_id: Snapshot ID
        
        Returns:
            JSON representation or None
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return None
        
        data = {
            "id": snapshot.id,
            "timestamp": snapshot.timestamp.isoformat(),
            "label": snapshot.label,
            "components": snapshot.components,
            "metrics": snapshot.metrics,
            "policies": snapshot.policies,
            "metadata": snapshot.metadata
        }
        
        return json.dumps(data, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "oldest_snapshot": None,
                "newest_snapshot": None
            }
        
        snapshots = self.list_snapshots()
        oldest = snapshots[-1] if snapshots else None
        newest = snapshots[0] if snapshots else None
        
        return {
            "total_snapshots": len(self.snapshots),
            "max_snapshots": self.max_snapshots,
            "retention_days": self.retention_days,
            "oldest_snapshot": {
                "id": oldest.id,
                "timestamp": oldest.timestamp.isoformat(),
                "age_seconds": oldest.age_seconds()
            } if oldest else None,
            "newest_snapshot": {
                "id": newest.id,
                "timestamp": newest.timestamp.isoformat(),
                "age_seconds": newest.age_seconds()
            } if newest else None
        }
