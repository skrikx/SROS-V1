"""
Long-Term Memory
================

Persistent semantic storage for Skrikx.
Designed to store facts, learnings, and successful patterns.
"""
import json
import os
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    Long-term semantic memory.
    
    Current Implementation: JSON-based persistent store with keyword search.
    Future Upgrade: Vector Database (Chroma/Pinecone) with embeddings.
    """
    def __init__(self, persistence_path: str = "sros/knowledge/long_term_memory.json"):
        self.persistence_path = persistence_path
        self.store: List[Dict[str, Any]] = []
        self._load()

    def add(self, content: str, tags: List[str] = None, metadata: Dict[str, Any] = None):
        """
        Add a memory to long-term storage.
        """
        entry = {
            "id": str(time.time()), # Simple ID
            "content": content,
            "tags": tags or [],
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        self.store.append(entry)
        self._save()
        logger.info(f"Added to LongTermMemory: {content[:50]}...")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search (Simulated via keyword matching for now).
        """
        query_terms = query.lower().split()
        results = []
        
        for entry in self.store:
            score = 0
            content_lower = entry["content"].lower()
            tags_lower = [t.lower() for t in entry.get("tags", [])]
            
            # Simple scoring
            for term in query_terms:
                if term in content_lower:
                    score += 1
                if term in tags_lower:
                    score += 2 # Tags weigh more
            
            if score > 0:
                results.append((score, entry))
        
        # Sort by score desc
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

    def _save(self):
        """Persist to disk."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.persistence_path)), exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(self.store, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save LongTermMemory: {e}")

    def _load(self):
        """Load from disk."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
            except Exception:
                self.store = []
