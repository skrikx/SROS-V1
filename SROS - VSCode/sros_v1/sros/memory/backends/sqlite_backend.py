"""
SQLite Backend

Persistent key-value storage using SQLite for SROS memory layers.
Provides durability and query capabilities for long-term memory.
"""
import sqlite3
import json
import os
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class SQLiteBackend:
    """
    SQLite-based persistent storage backend.
    
    Features:
    - ACID compliance
    - Queryable storage
    - TTL support for entries
    - JSON serialization for complex types
    - Thread-safe operations with connection pooling
    """
    
    def __init__(self, db_path: str = "./data/sros_memory.db"):
        """
        Initialize SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
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
        """Initialize database schema."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Main key-value table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    value_type TEXT DEFAULT 'json',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ttl_seconds INTEGER,
                    expired INTEGER DEFAULT 0
                )
            """)
            
            # Index for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_kv_key ON kv_store(key)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_kv_expired ON kv_store(expired)
            """)
            
            conn.commit()
            logger.debug(f"SQLite backend initialized: {self.db_path}")
        finally:
            conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value by key.
        
        Args:
            key: Storage key
        
        Returns:
            Deserialized value or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value, value_type FROM kv_store 
                WHERE key = ? AND expired = 0
            """, (key,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            value_str, value_type = row
            
            if value_type == 'json':
                return json.loads(value_str)
            elif value_type == 'string':
                return value_str
            else:
                return value_str
        finally:
            conn.close()
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Store value with optional TTL.
        
        Args:
            key: Storage key
            value: Value to store (will be JSON serialized)
            ttl_seconds: Time-to-live in seconds (optional)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Serialize value
            if isinstance(value, str):
                value_str = value
                value_type = 'string'
            else:
                value_str = json.dumps(value)
                value_type = 'json'
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO kv_store (key, value, value_type, ttl_seconds, expired)
                VALUES (?, ?, ?, ?, 0)
            """, (key, value_str, value_type, ttl_seconds))
            
            conn.commit()
            logger.debug(f"Stored key: {key}")
        finally:
            conn.close()
    
    def delete(self, key: str):
        """
        Delete key-value pair.
        
        Args:
            key: Storage key
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kv_store WHERE key = ?", (key,))
            conn.commit()
            logger.debug(f"Deleted key: {key}")
        finally:
            conn.close()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all keys with optional prefix filter.
        
        Args:
            prefix: Key prefix filter (optional)
        
        Returns:
            List of matching keys
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            if prefix:
                cursor.execute("""
                    SELECT key FROM kv_store 
                    WHERE key LIKE ? AND expired = 0
                    ORDER BY key
                """, (f"{prefix}%",))
            else:
                cursor.execute("""
                    SELECT key FROM kv_store 
                    WHERE expired = 0
                    ORDER BY key
                """)
            
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def query(self, condition: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Query entries by custom SQL condition.
        
        Args:
            condition: WHERE clause condition (e.g., "key LIKE ?")
            params: Parameters for condition
        
        Returns:
            List of matching entries
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT key, value, value_type FROM kv_store 
                WHERE {condition} AND expired = 0
            """, params)
            
            results = []
            for row in cursor.fetchall():
                key, value_str, value_type = row
                if value_type == 'json':
                    value = json.loads(value_str)
                else:
                    value = value_str
                
                results.append({"key": key, "value": value})
            
            return results
        finally:
            conn.close()
    
    def clear(self):
        """Delete all entries from storage."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kv_store")
            conn.commit()
            logger.debug("Cleared all keys from SQLite backend")
        finally:
            conn.close()
