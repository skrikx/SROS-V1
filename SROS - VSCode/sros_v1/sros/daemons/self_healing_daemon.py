"""
Self-Healing Daemon
===================

Monitors for crashes, exceptions, and auto-patches code.
"""
import logging
import threading
import time
import traceback
import sys
from io import StringIO

logger = logging.getLogger(__name__)

class SelfHealingDaemon:
    """
    The Immune System.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context
        self.event_bus = kernel_context.event_bus
        self.active = False
        self.thread = None
        self.last_exception = None

    def start(self):
        """Start monitoring."""
        if self.active: return
        self.active = True
        
        # Install global exception hook
        sys.excepthook = self._exception_hook
        
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Self-Healing Daemon Active.")
        self.event_bus.publish("system", "daemon.started", {"name": "self_healing"})

    def stop(self):
        """Stop monitoring."""
        self.active = False
        if self.thread:
            self.thread.join(timeout=2)

    def _exception_hook(self, exc_type, exc_value, exc_traceback):
        """Capture unhandled exceptions."""
        self.last_exception = {
            "type": str(exc_type),
            "value": str(exc_value),
            "traceback": "".join(traceback.format_tb(exc_traceback))
        }
        
        logger.error(f"CRASH DETECTED: {exc_type.__name__}: {exc_value}")
        self.event_bus.publish("governance", "crash.detected", self.last_exception)
        
        # Try to auto-heal
        self._attempt_heal()
        
        # Call default hook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.active:
            time.sleep(10)
            # Could add health checks here

    def _attempt_heal(self):
        """Attempt to patch the crash."""
        if not self.last_exception:
            return
        
        try:
            # Simplified: Log to event bus for now
            # In a real system, we'd use CognitiveArchitect to generate a patch
            self.event_bus.publish("governance", "heal.attempted", {
                "exception": self.last_exception,
                "status": "logged"
            })
        except Exception as e:
            logger.error(f"Heal attempt failed: {e}")
