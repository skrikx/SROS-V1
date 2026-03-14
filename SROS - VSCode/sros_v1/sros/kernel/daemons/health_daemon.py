"""
Health Daemon

Monitors the health of all kernel planes and publishes status.
Periodically checks plane readiness and reports metrics.
"""
import time
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthStatus:
    """Represents health status of a component."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    
    @staticmethod
    def validate(status: str) -> bool:
        """Validate status string."""
        return status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
            HealthStatus.UNKNOWN
        ]


class HealthDaemon:
    """
    Health Daemon - Monitor kernel plane health.
    
    Features:
    - Register plane health checks
    - Periodic health monitoring
    - Publish health status to event bus
    - Track health history
    - Alert on health degradation
    """
    
    def __init__(self, event_bus, check_interval: float = 5.0):
        """
        Initialize health daemon.
        
        Args:
            event_bus: Event bus for publishing events
            check_interval: How often to check plane health (seconds)
        """
        self.event_bus = event_bus
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        
        # Store health check callbacks
        self.health_checks: Dict[str, callable] = {}
        
        # Track health status history
        self.last_status: Dict[str, str] = {}
        self.status_history: Dict[str, list] = {}
        
        self._lock = threading.RLock()
    
    def register_health_check(
        self,
        plane_name: str,
        check_callback: callable
    ) -> bool:
        """
        Register a health check for a plane.
        
        Args:
            plane_name: Name of the plane (e.g., "kernel", "runtime", "governance")
            check_callback: Callable that returns (is_healthy: bool, metrics: dict)
        
        Returns:
            True if registered, False if already exists
        """
        with self._lock:
            if plane_name in self.health_checks:
                logger.warning(f"Health check for '{plane_name}' already registered")
                return False
            
            self.health_checks[plane_name] = check_callback
            self.last_status[plane_name] = HealthStatus.UNKNOWN
            self.status_history[plane_name] = []
            
            logger.info(f"Registered health check for plane '{plane_name}'")
            self.event_bus.publish(
                "kernel",
                "health.check_registered",
                {"plane": plane_name}
            )
            return True
    
    def unregister_health_check(self, plane_name: str) -> bool:
        """
        Unregister a health check.
        
        Args:
            plane_name: Name of the plane
        
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if plane_name not in self.health_checks:
                logger.warning(f"Health check for '{plane_name}' not found")
                return False
            
            del self.health_checks[plane_name]
            logger.info(f"Unregistered health check for plane '{plane_name}'")
            return True
    
    def get_plane_status(self, plane_name: str) -> Optional[Dict[str, Any]]:
        """Get current health status of a plane."""
        with self._lock:
            if plane_name not in self.last_status:
                return None
            
            return {
                "plane": plane_name,
                "status": self.last_status[plane_name],
                "timestamp": datetime.now().isoformat(),
                "history_size": len(self.status_history.get(plane_name, []))
            }
    
    def get_all_planes_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current health status of all planes."""
        with self._lock:
            return {
                plane: {
                    "plane": plane,
                    "status": self.last_status[plane],
                    "timestamp": datetime.now().isoformat()
                }
                for plane in self.health_checks.keys()
            }
    
    def start(self):
        """Start the health daemon."""
        if self.running:
            logger.warning("Health daemon already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        
        logger.info("Health daemon started")
        self.event_bus.publish(
            "kernel",
            "health.started",
            {"planes_monitored": len(self.health_checks)}
        )
    
    def stop(self):
        """Stop the health daemon."""
        if not self.running:
            return
        
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        
        logger.info("Health daemon stopped")
        self.event_bus.publish(
            "kernel",
            "health.stopped",
            {"planes_checked": len(self.health_checks)}
        )
    
    def _loop(self):
        """Main health monitoring loop."""
        while self.running:
            try:
                self._check_all_planes()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health daemon loop: {e}")
                self.event_bus.publish(
                    "kernel",
                    "health.error",
                    {"error": str(e)}
                )
    
    def _check_all_planes(self):
        """Check health of all registered planes."""
        with self._lock:
            checks_to_run = dict(self.health_checks)
        
        for plane_name, check_callback in checks_to_run.items():
            try:
                # Call the health check
                is_healthy = check_callback()
                
                # Determine status
                status = (
                    HealthStatus.HEALTHY if is_healthy
                    else HealthStatus.UNHEALTHY
                )
                
                # Track status change
                old_status = self.last_status.get(plane_name, HealthStatus.UNKNOWN)
                
                with self._lock:
                    self.last_status[plane_name] = status
                    self.status_history[plane_name].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": status
                    })
                    
                    # Keep history to last 100 entries
                    if len(self.status_history[plane_name]) > 100:
                        self.status_history[plane_name] = self.status_history[plane_name][-100:]
                
                # Publish status
                self.event_bus.publish(
                    "kernel",
                    "health.status",
                    {
                        "plane": plane_name,
                        "status": status,
                        "changed": old_status != status
                    }
                )
                
                # Alert on state change
                if old_status != status and old_status != HealthStatus.UNKNOWN:
                    event_type = (
                        "health.recovered"
                        if status == HealthStatus.HEALTHY
                        else "health.degraded"
                    )
                    
                    self.event_bus.publish(
                        "kernel",
                        event_type,
                        {
                            "plane": plane_name,
                            "previous_status": old_status,
                            "new_status": status
                        }
                    )
                    
                    logger.warning(
                        f"Plane '{plane_name}' health changed: {old_status} → {status}"
                    )
                
                logger.debug(f"Plane '{plane_name}' health: {status}")
                
            except Exception as e:
                logger.error(f"Error checking health of plane '{plane_name}': {e}")
                
                with self._lock:
                    self.last_status[plane_name] = HealthStatus.UNHEALTHY
                
                self.event_bus.publish(
                    "kernel",
                    "health.check_error",
                    {"plane": plane_name, "error": str(e)}
                )
