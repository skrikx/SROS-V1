"""
Memory Daemon

Manages memory layer lifecycle and garbage collection.
Coordinates between short-term, long-term, and codex layers.
"""
import time
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryDaemon:
    """
    Memory Daemon - Manage memory layer operations.
    
    Features:
    - Automatic short-term to long-term migration
    - Memory cleanup and garbage collection
    - Persistence checkpoint management
    - Cache coherency across layers
    - Event bus integration for observability
    """
    
    def __init__(self, event_bus, memory_router=None, check_interval: float = 60.0):
        """
        Initialize memory daemon.
        
        Args:
            event_bus: Event bus for publishing events
            memory_router: Memory router instance for layer access
            check_interval: How often to run cleanup (seconds)
        """
        self.event_bus = event_bus
        self.memory_router = memory_router
        self.check_interval = check_interval
        self.running = False
        self._thread = None
        self._lock = threading.RLock()
        
        # Statistics
        self.migrations_count = 0
        self.cleanup_runs = 0
        self.last_cleanup = None
    
    def start(self):
        """Start memory daemon."""
        if self.running:
            logger.warning("Memory daemon already running")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        logger.info("Memory daemon started")
        self.event_bus.publish("memory_daemon", "memory.daemon.started", {
            "timestamp": datetime.now().isoformat()
        })
    
    def stop(self):
        """Stop memory daemon."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        
        logger.info("Memory daemon stopped")
        self.event_bus.publish("memory_daemon", "memory.daemon.stopped", {
            "timestamp": datetime.now().isoformat()
        })
    
    def _run(self):
        """Main daemon loop."""
        logger.info(f"Memory daemon loop started (check_interval={self.check_interval}s)")
        
        while self.running:
            try:
                self._perform_cleanup()
                self._migrate_old_entries()
                self.last_cleanup = datetime.now()
            except Exception as e:
                logger.error(f"Error in memory daemon: {e}")
                self.event_bus.publish("memory_daemon", "memory.daemon.error", {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Sleep but check running status frequently
            for _ in range(int(self.check_interval * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
    
    def _perform_cleanup(self):
        """Run memory cleanup operations."""
        with self._lock:
            self.cleanup_runs += 1
            
            if not self.memory_router:
                return
            
            # Clean up expired entries
            persistent_keys = self.memory_router.get_persistent_keys()
            cleanup_count = 0
            
            for key in persistent_keys[:100]:  # Limit per run
                entry = self.memory_router.retrieve_persistent(key)
                if entry and self._is_expired(entry):
                    self.memory_router.clear_persistent(key)
                    cleanup_count += 1
            
            if cleanup_count > 0:
                logger.debug(f"Cleaned up {cleanup_count} expired entries")
                self.event_bus.publish("memory_daemon", "memory.cleanup", {
                    "cleaned_count": cleanup_count,
                    "timestamp": datetime.now().isoformat()
                })
    
    def _migrate_old_entries(self):
        """Migrate old short-term entries to long-term storage."""
        with self._lock:
            if not self.memory_router:
                return
            
            # This is a placeholder for more sophisticated migration logic
            # In production, would track access patterns and promote frequently-used entries
            migration_count = 0
            
            if migration_count > 0:
                self.migrations_count += migration_count
                logger.debug(f"Migrated {migration_count} entries to long-term")
                self.event_bus.publish("memory_daemon", "memory.migration", {
                    "migrated_count": migration_count,
                    "total_migrations": self.migrations_count,
                    "timestamp": datetime.now().isoformat()
                })
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if entry is expired."""
        if not entry:
            return False
        
        metadata = entry.get("metadata", {})
        if not metadata.get("ttl_seconds"):
            return False
        
        created_at = metadata.get("created_at", time.time())
        age = time.time() - created_at
        
        return age > metadata["ttl_seconds"]
    
    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        return {
            "running": self.running,
            "cleanup_runs": self.cleanup_runs,
            "migrations_count": self.migrations_count,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "check_interval": self.check_interval
        }
