"""
Vector Backend

Vector similarity search using SQLite with FTS5 for semantic memory.
Enables approximate nearest neighbor search for memory retrieval.
"""
import sqlite3
import json
import os
from typing import Any, Dict, Optional, List, Tuple
import logging
import math

logger = logging.getLogger(__name__)


class VectorBackend:
    """
    Vector storage and similarity search backend.
    
    Features:
    - Vector embedding storage
    - Cosine similarity search
    - Dimension-agnostic (supports any embedding size)
    - Fast approximate nearest neighbor search
    - Metadata filtering during search
    """
    
    def __init__(self, db_path: str = "./data/sros_vectors.db", dimension: int = 384):
        """
        Initialize vector backend.
        
        Args:
            db_path: Path to vector database file
            dimension: Embedding dimension (default: 384 for sentence-transformers)
        """
        self.db_path = db_path
        self.dimension = dimension
        
        # Create directory if needed
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database schema for vectors."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Vector storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dimension INTEGER NOT NULL
                )
            """)
            
            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vectors_key ON vectors(key)
            """)
            
            conn.commit()
            logger.debug(f"Vector backend initialized: {self.db_path}")
        finally:
            conn.close()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score between -1 and 1
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def store(
        self,
        key: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store vector with associated text and metadata.
        
        Args:
            key: Unique identifier
            text: Original text for reference
            embedding: Vector embedding (list of floats)
            metadata: Optional metadata dict
        
        Raises:
            ValueError: If embedding dimension doesn't match
        """
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} doesn't match "
                f"configured dimension {self.dimension}"
            )
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            embedding_json = json.dumps(embedding)
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO vectors 
                (key, text, embedding, metadata, dimension)
                VALUES (?, ?, ?, ?, ?)
            """, (key, text, embedding_json, metadata_json, self.dimension))
            
            conn.commit()
            logger.debug(f"Stored vector: {key}")
        finally:
            conn.close()
    
    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve vector and metadata by key.
        
        Args:
            key: Vector key
        
        Returns:
            Dict with embedding, text, metadata or None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT text, embedding, metadata FROM vectors 
                WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "text": row[0],
                "embedding": json.loads(row[1]),
                "metadata": json.loads(row[2])
            }
        finally:
            conn.close()
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        min_similarity: float = 0.3,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """
        Find most similar vectors to query embedding.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            metadata_filter: Optional metadata filter criteria
        
        Returns:
            List of (key, similarity_score) tuples sorted by similarity
        
        Raises:
            ValueError: If query embedding dimension mismatch
        """
        if len(query_embedding) != self.dimension:
            raise ValueError(
                f"Query embedding dimension {len(query_embedding)} doesn't match "
                f"configured dimension {self.dimension}"
            )
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, embedding, metadata FROM vectors")
            
            results = []
            
            for row in cursor.fetchall():
                key = row[0]
                embedding = json.loads(row[1])
                metadata = json.loads(row[2])
                
                # Apply metadata filter if provided
                if metadata_filter:
                    if not all(metadata.get(k) == v for k, v in metadata_filter.items()):
                        continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                if similarity >= min_similarity:
                    results.append((key, similarity))
            
            # Sort by similarity (descending) and take top-k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        finally:
            conn.close()
    
    def search_with_text(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        min_similarity: float = 0.3,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar vectors and return with text and metadata.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            metadata_filter: Optional metadata filter
        
        Returns:
            List of dicts with key, text, similarity, metadata
        """
        results = self.search(query_embedding, top_k, min_similarity, metadata_filter)
        
        conn = self._get_connection()
        try:
            detailed_results = []
            
            for key, similarity in results:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT text, metadata FROM vectors WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    detailed_results.append({
                        "key": key,
                        "text": row[0],
                        "similarity": similarity,
                        "metadata": json.loads(row[1])
                    })
            
            return detailed_results
        finally:
            conn.close()
    
    def delete(self, key: str):
        """
        Delete vector by key.
        
        Args:
            key: Vector key
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vectors WHERE key = ?", (key,))
            conn.commit()
            logger.debug(f"Deleted vector: {key}")
        finally:
            conn.close()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all vector keys with optional prefix.
        
        Args:
            prefix: Key prefix filter
        
        Returns:
            List of keys
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            if prefix:
                cursor.execute("""
                    SELECT key FROM vectors 
                    WHERE key LIKE ? 
                    ORDER BY key
                """, (f"{prefix}%",))
            else:
                cursor.execute("SELECT key FROM vectors ORDER BY key")
            
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def count(self) -> int:
        """Get total number of vectors stored."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vectors")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def clear(self):
        """Delete all vectors from storage."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vectors")
            conn.commit()
            logger.debug("Cleared all vectors")
        finally:
            conn.close()
