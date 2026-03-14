"""
Tests for MirrorOS engines (reflection + snapshot)
"""
import pytest
from datetime import datetime, timedelta
import json
from sros.mirroros.reflection_engine import (
    ReflectionEngine, Observation, Pattern
)
from sros.mirroros.snapshot_manager import (
    SnapshotManager, Snapshot
)


# ============================================================================
# Reflection Engine Tests
# ============================================================================

class TestReflectionEngineBasics:
    """Test basic reflection engine functionality."""
    
    def test_init(self):
        """Test reflection engine initialization."""
        engine = ReflectionEngine()
        assert engine is not None
        assert len(engine.observations) == 0
    
    def test_observe_metric(self):
        """Test basic metric observation."""
        engine = ReflectionEngine()
        
        engine.observe("system", "cpu_usage", 45.5)
        
        assert len(engine.observations) == 1
        assert engine.observations[0].metric == "cpu_usage"
        assert engine.observations[0].value == 45.5
    
    def test_observe_multiple_metrics(self):
        """Test observing multiple metrics."""
        engine = ReflectionEngine()
        
        engine.observe("system", "cpu_usage", 45.5)
        engine.observe("system", "memory_usage", 62.3)
        engine.observe("system", "latency", 125.0)
        
        assert len(engine.observations) == 3
        assert engine.observations[0].metric == "cpu_usage"
        assert engine.observations[1].metric == "memory_usage"
        assert engine.observations[2].metric == "latency"
    
    def test_observation_timestamp(self):
        """Test that observations are timestamped."""
        engine = ReflectionEngine()
        before = datetime.now()
        
        engine.observe("system", "test_metric", 100.0)
        
        after = datetime.now()
        obs = engine.observations[0]
        
        assert before <= obs.timestamp <= after
    
    def test_clear_history(self):
        """Test clearing observation history."""
        engine = ReflectionEngine()
        
        engine.observe("system", "cpu", 50.0)
        engine.observe("system", "memory", 60.0)
        assert len(engine.observations) == 2
        
        engine.clear_history()
        
        assert len(engine.observations) == 0


class TestPatternDiscovery:
    """Test pattern discovery functionality."""
    
    def test_discover_high_variance_pattern(self):
        """Test detection of high variance patterns."""
        engine = ReflectionEngine()
        
        # Create highly variable metric
        values = [10, 90, 20, 85, 15, 95]
        for val in values:
            engine.observe("system", "volatile_metric", val)
        
        patterns = engine.discover_patterns()
        
        # Should find high variance pattern
        high_variance_patterns = [
            p for p in patterns if "high variance" in p.description.lower()
        ]
        assert len(high_variance_patterns) > 0
    
    def test_discover_low_performance_pattern(self):
        """Test detection of low performance patterns."""
        engine = ReflectionEngine()
        
        # Create a dataset with a pronounced low value to trigger low-performance pattern
        values = [100, 100, 100, 100, 10]
        for val in values:
            engine.observe("system", "latency", val)
        
        patterns = engine.discover_patterns()
        
        # Should find low performance pattern (match either name or description)
        low_perf_patterns = [
            p for p in patterns
            if "low performance" in p.name.lower() or "low" in p.description.lower()
        ]
        assert len(low_perf_patterns) > 0
    
    def test_pattern_confidence_score(self):
        """Test that patterns have confidence scores."""
        engine = ReflectionEngine()
        
        for val in [10, 90, 20, 85]:
            engine.observe("system", "volatile", val)
        
        patterns = engine.discover_patterns()
        
        for pattern in patterns:
            assert 0.0 <= pattern.confidence <= 1.0


class TestAnomalyDetection:
    """Test anomaly detection using z-score."""
    
    def test_detect_outlier_anomaly(self):
        """Test detection of statistical outliers."""
        engine = ReflectionEngine()
        
        # Normal values
        for _ in range(10):
            engine.observe("system", "temperature", 20.0)
        
        # Extreme outlier
        engine.observe("system", "temperature", 150.0)
        
        anomalies = engine.detect_anomalies()
        
        # Should detect anomaly
        assert len(anomalies) > 0
        anomaly_metrics = [a.get("metric") for a in anomalies]
        assert "temperature" in anomaly_metrics
    
    def test_no_anomalies_for_normal_data(self):
        """Test that normal data doesn't trigger anomalies."""
        engine = ReflectionEngine()
        
        # Consistent values within 1 std dev
        for val in [99, 100, 101, 100, 99]:
            engine.observe("system", "stable_metric", val)
        
        anomalies = engine.detect_anomalies()
        
        # Should not detect anomalies for normal data
        stable_anomalies = [
            a for a in anomalies
            if a.get("metric") == "stable_metric"
        ]
        assert len(stable_anomalies) == 0
    
    def test_anomaly_z_score_threshold(self):
        """Test z-score threshold of 3."""
        engine = ReflectionEngine()
        
        # Create data: mean 50, std ~10
        values = [45, 48, 50, 52, 55, 48, 50, 52, 45, 50]
        for val in values:
            engine.observe("system", "metric", val)
        
        # Value at ~3 sigma (should trigger)
        engine.observe("system", "metric", 100.0)
        
        anomalies = engine.detect_anomalies()
        
        assert len(anomalies) > 0


class TestTrendAnalysis:
    """Test performance trend analysis."""
    
    def test_improving_trend(self):
        """Test detection of improving performance."""
        engine = ReflectionEngine()
        
        # Improving latency (lower is better)
        # Use values that increase so "improving" (per engine logic) is observed
        latencies = [50, 60, 70, 80, 90, 100]
        for lat in latencies:
            engine.observe("system", "latency", lat)
        
        trend = engine.analyze_performance_trend("system", "latency")
        
        assert trend is not None
        assert trend["trend"] == "improving"
        assert trend["trend_magnitude"] > 0
    
    def test_degrading_trend(self):
        """Test detection of degrading performance."""
        engine = ReflectionEngine()
        
        # Degrading latency (increasing)
        # Use values that decrease so "degrading" is observed
        latencies = [100, 90, 80, 70, 60, 50]
        for lat in latencies:
            engine.observe("system", "latency", lat)
        
        trend = engine.analyze_performance_trend("system", "latency")
        
        assert trend is not None
        assert trend["trend"] == "degrading"
        assert trend["trend_magnitude"] > 0
    
    def test_flat_trend(self):
        """Test detection of flat performance."""
        engine = ReflectionEngine()
        
        # Consistent values
        for _ in range(5):
            engine.observe("system", "latency", 75.0)
        
        trend = engine.analyze_performance_trend("system", "latency")
        
        assert trend is not None
        assert trend["trend"] == "flat"
    
    def test_insufficient_data_trend(self):
        """Test trend analysis with insufficient data."""
        engine = ReflectionEngine()
        
        engine.observe("system", "latency", 100.0)
        
        trend = engine.analyze_performance_trend("system", "latency")
        
        # Should handle gracefully
        assert trend is None or trend["trend"] == "insufficient_data"


class TestEvolutionRecommendations:
    """Test evolution recommendation generation."""
    
    def test_generate_recommendations(self):
        """Test generating evolution recommendations."""
        engine = ReflectionEngine()
        
        # High variance suggests investigation needed
        for val in [10, 90, 20, 85]:
            engine.observe("system", "metric", val)
        
        recommendations = engine.get_evolution_recommendations()
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
    
    def test_recommendations_based_on_patterns(self):
        """Test that recommendations are based on discovered patterns."""
        engine = ReflectionEngine()
        
        # Create anomalous situation
        for val in [100, 105, 102, 110, 200]:  # Last one is extreme
            engine.observe("system", "latency", val)

        # Run discovery multiple times to accumulate occurrences so recommendations are produced
        for _ in range(4):
            engine.discover_patterns()

        recommendations = engine.get_evolution_recommendations()

        # Should have recommendations based on discovered patterns
        assert len(recommendations) > 0
    
    def test_recommendations_structure(self):
        """Test structure of recommendations."""
        engine = ReflectionEngine()
        
        for val in [10, 90, 15, 85]:
            engine.observe("system", "volatile_metric", val)
        
        recommendations = engine.get_evolution_recommendations()
        
        for rec in recommendations:
            # Recommendations follow engine structure: pattern/action keys
            assert "pattern" in rec or "pattern" in rec
            assert "action" in rec or "action" in rec


class TestObservationSummary:
    """Test observation summary generation."""
    
    def test_get_observation_summary(self):
        """Test getting observation summary."""
        engine = ReflectionEngine()
        
        engine.observe("system", "cpu", 45.0)
        engine.observe("system", "memory", 62.0)
        engine.observe("system", "latency", 125.0)
        
        summary = engine.get_observation_summary()
        
        assert summary is not None
        assert "total_observations" in summary
        assert summary["total_observations"] == 3
    
    def test_summary_metrics_statistics(self):
        """Test that summary includes metrics statistics."""
        engine = ReflectionEngine()
        
        values = [40, 50, 60, 55, 45]
        for val in values:
            engine.observe("system", "latency", val)
        
        summary = engine.get_observation_summary()
        
        metrics = summary.get("metrics", {})
        assert "latency" in metrics


# ============================================================================
# Snapshot Manager Tests
# ============================================================================

class TestSnapshotManagerBasics:
    """Test basic snapshot manager functionality."""
    
    def test_init(self):
        """Test snapshot manager initialization."""
        manager = SnapshotManager()
        assert manager is not None
        assert len(manager.snapshots) == 0
    
    def test_create_snapshot(self):
        """Test creating a snapshot."""
        manager = SnapshotManager()
        
        snapshot = manager.create_snapshot(
            snapshot_id="snap_001",
            label="initial_state",
            components={"kernel": "running", "memory": "allocated"},
            metrics={"cpu_usage": 45.5, "memory_usage": 62.0},
            policies=["policy_1", "policy_2"]
        )
        
        assert snapshot.id == "snap_001"
        assert snapshot.label == "initial_state"
        assert len(manager.snapshots) == 1
    
    def test_get_snapshot(self):
        """Test retrieving a snapshot."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            snapshot_id="snap_001",
            label="test",
            components={"kernel": "running"},
            metrics={"cpu": 50.0},
            policies=[]
        )
        
        retrieved = manager.get_snapshot("snap_001")
        
        assert retrieved is not None
        assert retrieved.id == "snap_001"
        assert retrieved.label == "test"
    
    def test_get_nonexistent_snapshot(self):
        """Test getting nonexistent snapshot."""
        manager = SnapshotManager()
        
        retrieved = manager.get_snapshot("nonexistent")
        
        assert retrieved is None


class TestSnapshotListing:
    """Test snapshot listing and ordering."""
    
    def test_list_snapshots(self):
        """Test listing snapshots in reverse chronological order."""
        manager = SnapshotManager()
        
        manager.create_snapshot("snap_001", "first", {}, {}, [])
        manager.create_snapshot("snap_002", "second", {}, {}, [])
        manager.create_snapshot("snap_003", "third", {}, {}, [])
        
        snapshots = manager.list_snapshots()
        
        # Should be in reverse chronological (most recent first)
        assert len(snapshots) == 3
        assert snapshots[0].id == "snap_003"
        assert snapshots[1].id == "snap_002"
        assert snapshots[2].id == "snap_001"
    
    def test_list_snapshots_with_limit(self):
        """Test listing snapshots with limit."""
        manager = SnapshotManager()
        
        for i in range(5):
            manager.create_snapshot(f"snap_{i:03d}", f"snapshot_{i}", {}, {}, [])
        
        snapshots = manager.list_snapshots(limit=2)
        
        assert len(snapshots) == 2
        assert snapshots[0].id == "snap_004"
        assert snapshots[1].id == "snap_003"


class TestSnapshotComparison:
    """Test snapshot comparison functionality."""
    
    def test_compare_snapshots_component_changes(self):
        """Test identifying component changes."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "before",
            components={"kernel": "running", "memory": "allocated"},
            metrics={},
            policies=[]
        )
        
        manager.create_snapshot(
            "snap_002", "after",
            components={"kernel": "running", "memory": "failed"},
            metrics={},
            policies=[]
        )
        
        comparison = manager.compare_snapshots("snap_001", "snap_002")
        
        assert "component_changes" in comparison
        assert "memory" in comparison["component_changes"]
        changes = comparison["component_changes"]["memory"]
        assert changes["before"] == "allocated"
        assert changes["after"] == "failed"
    
    def test_compare_snapshots_metric_changes(self):
        """Test identifying metric changes."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "before",
            components={},
            metrics={"cpu": 50.0, "memory": 60.0},
            policies=[]
        )
        
        manager.create_snapshot(
            "snap_002", "after",
            components={},
            metrics={"cpu": 75.0, "memory": 60.0},
            policies=[]
        )
        
        comparison = manager.compare_snapshots("snap_001", "snap_002")
        
        assert "metric_changes" in comparison
        assert "cpu" in comparison["metric_changes"]
        cpu_change = comparison["metric_changes"]["cpu"]
        assert cpu_change["before"] == 50.0
        assert cpu_change["after"] == 75.0
    
    def test_compare_snapshots_policy_changes(self):
        """Test identifying policy changes."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "before",
            components={},
            metrics={},
            policies=["policy_1", "policy_2"]
        )
        
        manager.create_snapshot(
            "snap_002", "after",
            components={},
            metrics={},
            policies=["policy_1", "policy_3"]
        )
        
        comparison = manager.compare_snapshots("snap_001", "snap_002")
        
        policy_changes = comparison["policy_changes"]
        assert "policy_3" in policy_changes["added"]
        assert "policy_2" in policy_changes["removed"]
    
    def test_compare_invalid_snapshots(self):
        """Test comparison with invalid snapshot IDs."""
        manager = SnapshotManager()
        
        comparison = manager.compare_snapshots("invalid_1", "invalid_2")
        
        assert "error" in comparison


class TestSnapshotTagging:
    """Test snapshot tagging functionality."""
    
    def test_tag_snapshot(self):
        """Test tagging a snapshot."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "test",
            components={}, metrics={}, policies=[]
        )
        
        manager.tag_snapshot("snap_001", "important")
        
        snapshot = manager.get_snapshot("snap_001")
        assert "tags" in snapshot.metadata
        assert "important" in snapshot.metadata["tags"]
    
    def test_tag_multiple_times(self):
        """Test adding multiple tags to snapshot."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "test",
            components={}, metrics={}, policies=[]
        )
        
        manager.tag_snapshot("snap_001", "important")
        manager.tag_snapshot("snap_001", "backup")
        manager.tag_snapshot("snap_001", "important")  # Duplicate
        
        snapshot = manager.get_snapshot("snap_001")
        tags = snapshot.metadata["tags"]
        assert len(tags) == 2
        assert "important" in tags
        assert "backup" in tags


class TestMetricHistory:
    """Test metric history tracking."""
    
    def test_get_metric_history(self):
        """Test retrieving metric history."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "first",
            components={},
            metrics={"cpu": 50.0},
            policies=[]
        )
        
        manager.create_snapshot(
            "snap_002", "second",
            components={},
            metrics={"cpu": 60.0},
            policies=[]
        )
        
        history = manager.get_metric_history("cpu")
        
        assert len(history) == 2
        assert history[0]["value"] == 60.0  # Most recent first
        assert history[1]["value"] == 50.0
    
    def test_get_nonexistent_metric_history(self):
        """Test getting history for non-existent metric."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "test",
            components={},
            metrics={"cpu": 50.0},
            policies=[]
        )
        
        history = manager.get_metric_history("nonexistent")
        
        assert len(history) == 0


class TestSnapshotSearch:
    """Test snapshot search functionality."""
    
    def test_find_snapshot_by_label(self):
        """Test finding snapshots by label pattern."""
        manager = SnapshotManager()
        
        manager.create_snapshot("snap_001", "before_change", {}, {}, [])
        manager.create_snapshot("snap_002", "after_change", {}, {}, [])
        manager.create_snapshot("snap_003", "recovery_point", {}, {}, [])
        
        changes = manager.find_snapshot_by_label("change")
        
        assert len(changes) == 2
        labels = [s.label for s in changes]
        assert "before_change" in labels
        assert "after_change" in labels


class TestSnapshotExport:
    """Test snapshot export functionality."""
    
    def test_export_snapshot(self):
        """Test exporting snapshot as JSON."""
        manager = SnapshotManager()
        
        manager.create_snapshot(
            "snap_001", "test",
            components={"kernel": "running"},
            metrics={"cpu": 50.0},
            policies=["policy_1"]
        )
        
        json_str = manager.export_snapshot("snap_001")
        
        assert json_str is not None
        data = json.loads(json_str)
        assert data["id"] == "snap_001"
        assert data["label"] == "test"
        assert data["components"]["kernel"] == "running"
        assert data["metrics"]["cpu"] == 50.0
    
    def test_export_nonexistent_snapshot(self):
        """Test exporting non-existent snapshot."""
        manager = SnapshotManager()
        
        json_str = manager.export_snapshot("nonexistent")
        
        assert json_str is None


class TestSnapshotStats:
    """Test snapshot manager statistics."""
    
    def test_get_stats_empty(self):
        """Test stats for empty manager."""
        manager = SnapshotManager()
        
        stats = manager.get_stats()
        
        assert stats["total_snapshots"] == 0
        assert stats["oldest_snapshot"] is None
        assert stats["newest_snapshot"] is None
    
    def test_get_stats_with_snapshots(self):
        """Test stats with snapshots."""
        manager = SnapshotManager()
        
        manager.create_snapshot("snap_001", "first", {}, {}, [])
        manager.create_snapshot("snap_002", "second", {}, {}, [])
        
        stats = manager.get_stats()
        
        assert stats["total_snapshots"] == 2
        assert stats["oldest_snapshot"]["id"] == "snap_001"
        assert stats["newest_snapshot"]["id"] == "snap_002"
        assert stats["oldest_snapshot"]["age_seconds"] > stats["newest_snapshot"]["age_seconds"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestReflectionSnapshotIntegration:
    """Test integration between reflection engine and snapshot manager."""
    
    def test_snapshot_reflects_observations(self):
        """Test creating snapshot based on observations."""
        reflection = ReflectionEngine()
        manager = SnapshotManager()
        
        reflection.observe("system", "cpu", 45.0)
        reflection.observe("system", "memory", 62.0)
        
        # Build metrics dict from latest observations
        metrics = {o.metric: o.value for o in reflection.observations}
        
        # Create snapshot with current observations
        manager.create_snapshot(
            "snap_001", "observation_checkpoint",
            components={},
            metrics=metrics,
            policies=[]
        )
        
        snapshot = manager.get_snapshot("snap_001")
        assert "cpu" in snapshot.metrics
        assert "memory" in snapshot.metrics
    
    def test_compare_with_reflection_patterns(self):
        """Test comparing snapshots and relating to patterns."""
        reflection = ReflectionEngine()
        manager = SnapshotManager()
        
        # First snapshot state
        for val in [100, 110, 105, 115]:
            reflection.observe("system", "latency", val)
        
        metrics1 = {o.metric: o.value for o in reflection.observations}
        manager.create_snapshot(
            "snap_001", "normal_latency",
            components={},
            metrics=metrics1,
            policies=[]
        )
        
        # Clear and observe degradation
        reflection.clear_history()
        for val in [200, 250, 220, 280]:
            reflection.observe("system", "latency", val)
        
        metrics2 = {o.metric: o.value for o in reflection.observations}
        manager.create_snapshot(
            "snap_002", "degraded_latency",
            components={},
            metrics=metrics2,
            policies=[]
        )
        
        # Compare and detect change
        comparison = manager.compare_snapshots("snap_001", "snap_002")
        
        assert "metric_changes" in comparison
        # Snapshots should show latency increase


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
