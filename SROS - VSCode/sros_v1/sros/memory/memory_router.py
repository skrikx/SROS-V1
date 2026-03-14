"""
Enhanced Memory Router

Routes memory operations across short-term, long-term, and codex layers.
Integrates persistent (SQLite) and vector backends for full memory fabric.
"""
from typing import Any, Dict, List, Optional
import logging
from .backends.sqlite_backend import SQLiteBackend
from .backends.vector_backend import VectorBackend

logger = logging.getLogger(__name__)


class MemoryRouter:
    """
    Routes memory operations across multiple layers.
    
    Layers:
    - short: Session memory (fast, temporary)
    - long: Persistent memory (slow, permanent)
    - codex: Knowledge packs (structured, versioned)
    - vector: Semantic search on embeddings
    """
    
    def __init__(self):
        self.short_term = None
        self.long_term = None
        self.codex = None
        self.vector_store = None
        
        # Persistent backends
        self.sqlite_backend = None
        self.vector_backend = None
        
        # Legacy in-memory store for backward compatibility
        self.memory_store: Dict[str, Any] = {}
    
    def initialize_layers(self, short_term, long_term, codex, vector_store=None, 
                         use_sqlite=True, use_vectors=True):
        """
        Initialize memory layers and backends.
        
        Args:
            short_term: Short-term memory layer
            long_term: Long-term memory layer
            codex: Knowledge codex layer
            vector_store: Optional vector store layer
            use_sqlite: Enable SQLite backend (default True)
            use_vectors: Enable vector backend (default True)
        """
        self.short_term = short_term
        self.long_term = long_term
        self.codex = codex
        self.vector_store = vector_store
        
        # Initialize persistent backends
        if use_sqlite:
            self.sqlite_backend = SQLiteBackend()
            logger.info("SQLite backend initialized for persistent memory")
        
        if use_vectors:
            self.vector_backend = VectorBackend(dimension=384)
            logger.info("Vector backend initialized for semantic search")
        
        logger.info("Memory layers initialized with backends")
    
    def read(self, query: str = None, layer: str = "short", key: str = None) -> list:
        """
        Read from memory layer.
        
        Args:
            query: Text query for search
            layer: Memory layer (short, long, codex)
            key: Specific key to retrieve
        
        Returns:
            List of matching items
        """
        if layer == "short" and self.short_term:
            if query:
                return self.short_term.search(query)
            else:
                return self.short_term.get_recent(10)
        
        elif layer == "long" and self.long_term:
            if key:
                item = self.long_term.get(key)
                return [item] if item else []
            elif query:
                return self.long_term.search(query)
            else:
                return []
        
        elif layer == "codex" and self.codex:
            if query:
                packs = self.codex.search_packs(query)
                return [p.to_dict() for p in packs]
            else:
                return []
        
        else:
            # Fallback to legacy store
            results = []
            for k, v in self.memory_store.items():
                if k.startswith(f"{layer}:"):
                    if query and query in v.get('content', ''):
                        results.append(v)
                    elif key and k == f"{layer}:{key}":
                        results.append(v)
            return results
    
    def write(self, content: Any, layer: str = "short", key: str = None, metadata: dict = None):
        """
        Write to memory layer.
        
        Args:
            content: Content to store
            layer: Memory layer
            key: Optional key
            metadata: Optional metadata
        """
        if layer == "short" and self.short_term:
            self.short_term.add(content, metadata)
        
        elif layer == "long" and self.long_term:
            if not key:
                import uuid
                key = str(uuid.uuid4())
            self.long_term.add(key, content, metadata)
            
            # Also add to vector store if available
            if self.vector_store:
                self.vector_store.add(key, str(content), metadata)
        
        elif layer == "codex" and self.codex:
            # Codex requires structured knowledge packs
            logger.warning("Use codex.add_pack() for codex layer")
        
        else:
            # Fallback to legacy store
            if key is None:
                key = str(len(self.memory_store))
            full_key = f"{layer}:{key}"
            self.memory_store[full_key] = {
                'content': content,
                'metadata': metadata or {}
            }
    
    def persist(self, key: str, content: Any, metadata: Optional[Dict[str, Any]] = None):
        """
        Persist content to SQLite backend for long-term storage.
        
        Args:
            key: Storage key
            content: Content to persist
            metadata: Optional metadata
        """
        if not self.sqlite_backend:
            logger.warning("SQLite backend not initialized; cannot persist")
            return
        
        self.sqlite_backend.put(key, {"content": content, "metadata": metadata or {}})
        logger.debug(f"Persisted {key} to SQLite backend")
    
    def retrieve_persistent(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve content from SQLite backend.
        
        Args:
            key: Storage key
        
        Returns:
            Content dict or None
        """
        if not self.sqlite_backend:
            return None
        
        return self.sqlite_backend.get(key)
    
    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search memory by semantic similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of matching items with scores
        """
        if not self.vector_backend:
            logger.warning("Vector backend not initialized; cannot search")
            return []
        
        return self.vector_backend.search_with_text(
            query_embedding, top_k, min_similarity
        )
    
    def store_vector(
        self,
        key: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store vector embedding for semantic search.
        
        Args:
            key: Unique identifier
            text: Original text
            embedding: Vector embedding (384-dim for default config)
            metadata: Optional metadata
        """
        if not self.vector_backend:
            logger.warning("Vector backend not initialized; cannot store vector")
            return
        
        self.vector_backend.store(key, text, embedding, metadata)
        logger.debug(f"Stored vector embedding for {key}")
    
    def get_persistent_keys(self, prefix: str = "") -> List[str]:
        """
        List persistent storage keys.
        
        Args:
            prefix: Optional key prefix filter
        
        Returns:
            List of keys in persistent storage
        """
        if not self.sqlite_backend:
            return []
        
        return self.sqlite_backend.list_keys(prefix)
    
    def clear_persistent(self, key: str = None):
        """
        Clear persistent storage (entire store or by key).
        
        Args:
            key: Optional specific key to delete; if None, clears all
        """
        if not self.sqlite_backend:
            return
        
        if key:
            self.sqlite_backend.delete(key)
            logger.debug(f"Deleted persistent key: {key}")
        else:
            self.sqlite_backend.clear()
            logger.debug("Cleared all persistent memory")
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search across all layers using vector store.
        """
        if self.vector_store:
            return self.vector_store.search(query, limit)
        else:
            # Fallback to text search
            results = []
            if self.short_term:
                results.extend(self.short_term.search(query))
            if self.long_term:
                results.extend(self.long_term.search(query, limit))
            return results[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all memory layers."""
        stats = {}
        if self.short_term:
            stats["short_term"] = self.short_term.get_stats()
        if self.long_term:
            stats["long_term"] = self.long_term.get_stats()
        if self.codex:
            stats["codex"] = self.codex.get_stats()
        if self.vector_store:
            stats["vector_store"] = self.vector_store.get_stats()
        return stats
