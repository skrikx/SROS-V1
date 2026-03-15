"""
Metric Threshold Drift Detector

Detects metric-threshold drift and simple outlier anomalies in SROS operations.
"""
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects metric-threshold drift and basic statistical anomalies.

    This component does not provide semantic or cognitive drift intelligence.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics: List[Dict[str, Any]] = []
        self.baselines: Dict[str, float] = {}
        
        # Thresholds
        self.performance_threshold = self.config.get("performance_threshold", 0.20)  # 20% degradation
        self.error_rate_threshold = self.config.get("error_rate_threshold", 0.05)  # 5% error rate
    
    def record_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        metadata: Dict[str, Any] = None
    ):
        """
        Record a metric value.
        
        Args:
            component: Component name
            metric_name: Metric name
            value: Metric value
            metadata: Additional metadata
        """
        entry = {
            "timestamp": time.time(),
            "component": component,
            "metric": metric_name,
            "value": value,
            "metadata": metadata or {}
        }
        
        self.metrics.append(entry)
        
        # Check for drift
        self._check_drift(component, metric_name, value)
    
    def set_baseline(self, component: str, metric_name: str, value: float):
        """Set baseline value for a metric."""
        key = f"{component}.{metric_name}"
        self.baselines[key] = value
        logger.info(f"Baseline set: {key} = {value}")
    
    def _check_drift(self, component: str, metric_name: str, value: float):
        """Check if metric has drifted from baseline."""
        key = f"{component}.{metric_name}"
        
        if key not in self.baselines:
            # Set first value as baseline
            self.baselines[key] = value
            return
        
        baseline = self.baselines[key]
        
        # Calculate drift percentage
        if baseline > 0:
            drift = (value - baseline) / baseline
            
            if abs(drift) > self.performance_threshold:
                logger.warning(
                    "Metric threshold drift detected: %s = %s (baseline: %s, drift: %.1f%%)",
                    key,
                    value,
                    baseline,
                    drift * 100,
                )
    
    def detect_anomalies(self, component: str = None) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics.
        
        Args:
            component: Optional component filter
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Group metrics by component and name
        metric_groups = {}
        for entry in self.metrics:
            if component and entry["component"] != component:
                continue
            
            key = f"{entry['component']}.{entry['metric']}"
            if key not in metric_groups:
                metric_groups[key] = []
            metric_groups[key].append(entry["value"])
        
        # Simple anomaly detection: values outside 2 std deviations
        for key, values in metric_groups.items():
            if len(values) < 10:
                continue
            
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            for i, value in enumerate(values[-10:]):  # Check last 10 values
                if abs(value - mean) > 2 * std_dev:
                    anomalies.append({
                        "metric": key,
                        "value": value,
                        "mean": mean,
                        "std_dev": std_dev,
                        "severity": "high" if abs(value - mean) > 3 * std_dev else "medium"
                    })
        
        return anomalies
    
    def get_drift_report(self) -> Dict[str, Any]:
        """Generate a truthful metric-threshold drift report."""
        threshold_breaches = 0
        for entry in self.metrics:
            key = f"{entry['component']}.{entry['metric']}"
            baseline = self.baselines.get(key)
            if baseline and baseline > 0:
                drift_pct = abs((entry["value"] - baseline) / baseline)
                if drift_pct > self.performance_threshold:
                    threshold_breaches += 1

        report = {
            "detector_type": "metric_threshold",
            "total_metrics": len(self.metrics),
            "baselines": len(self.baselines),
            "threshold_breaches": threshold_breaches,
            "anomalies": len(self.detect_anomalies()),
            "performance_threshold": self.performance_threshold,
            "error_rate_threshold": self.error_rate_threshold,
        }

        return report
