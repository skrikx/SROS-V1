"""
Short-Term Memory
=================

Session-based memory for temporary context.
Persists to JSON file for session recovery.
"""
from typing import Dict, Any, List, Optional
import time
import logging
import json
import os

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    Short-term memory for session context.
    
    Characteristics:
    - Fast access
    - Limited capacity
    - Automatic expiration
    - In-memory storage with JSON persistence
    """
    
    def __init__(self, capacity: int = 100, ttl_seconds: int = 3600, persistence_path: str = "sros/memory/short_term.json"):
        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self.persistence_path = persistence_path
        self.store: List[Dict[str, Any]] = []
        self._load()
    
    def add(self, content: Any, metadata: Dict[str, Any] = None):
        """Add item to short-term memory."""
        item = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self.store.append(item)
        
        # Enforce capacity
        if len(self.store) > self.capacity:
            self.store.pop(0)
        
        # Clean expired items
        self._clean_expired()
        self._save()
    
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent items."""
        self._clean_expired()
        return self.store[-count:]
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Simple text search in memory."""
        self._clean_expired()
        results = []
        
        for item in self.store:
            content_str = str(item["content"])
            if query.lower() in content_str.lower():
                results.append(item)
        
        return results
    
    def clear(self):
        """Clear all short-term memory."""
        self.store.clear()
        self._save()
        logger.info("Short-term memory cleared")
    
    def _clean_expired(self):
        """Remove expired items."""
        current_time = time.time()
        self.store = [
            item for item in self.store
            if current_time - item["timestamp"] < self.ttl_seconds
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "count": len(self.store),
            "capacity": self.capacity,
            "ttl_seconds": self.ttl_seconds
        }

    def _save(self):
        """Persist memory to disk."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.persistence_path)), exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(self.store, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def _load(self):
        """Load memory from disk."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
            except Exception:
                self.store = []
