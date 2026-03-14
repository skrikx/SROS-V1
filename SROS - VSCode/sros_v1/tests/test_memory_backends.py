"""
Memory Backend Tests

Comprehensive tests for SQLite and vector backends.
"""
import pytest
import os
import tempfile
import json
from sros.memory.backends.sqlite_backend import SQLiteBackend
from sros.memory.backends.vector_backend import VectorBackend


class TestSQLiteBackend:
    """Test SQLite persistent storage."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield db_path
    
    def test_sqlite_init(self, temp_db):
        """Test SQLite backend initialization."""
        backend = SQLiteBackend(temp_db)
        assert os.path.exists(temp_db)
    
    def test_sqlite_put_get(self, temp_db):
        """Test put/get operations."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("test_key", {"value": "test_value"})
        retrieved = backend.get("test_key")
        
        assert retrieved == {"value": "test_value"}
    
    def test_sqlite_put_string(self, temp_db):
        """Test storing string values."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("string_key", "simple_string")
        retrieved = backend.get("string_key")
        
        assert retrieved == "simple_string"
    
    def test_sqlite_get_nonexistent(self, temp_db):
        """Test getting nonexistent key."""
        backend = SQLiteBackend(temp_db)
        
        retrieved = backend.get("nonexistent")
        assert retrieved is None
    
    def test_sqlite_delete(self, temp_db):
        """Test delete operation."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("delete_key", {"data": "to_delete"})
        backend.delete("delete_key")
        
        retrieved = backend.get("delete_key")
        assert retrieved is None
    
    def test_sqlite_list_keys(self, temp_db):
        """Test list_keys operation."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("prefix:key1", {"v": 1})
        backend.put("prefix:key2", {"v": 2})
        backend.put("other:key3", {"v": 3})
        
        keys = backend.list_keys("prefix:")
        assert "prefix:key1" in keys
        assert "prefix:key2" in keys
        assert "other:key3" not in keys
    
    def test_sqlite_ttl(self, temp_db):
        """Test TTL functionality."""
        backend = SQLiteBackend(temp_db)
        
        # Store with TTL (not implemented in query, but should store)
        backend.put("ttl_key", {"data": "value"}, ttl_seconds=3600)
        retrieved = backend.get("ttl_key")
        
        assert retrieved == {"data": "value"}
    
    def test_sqlite_query(self, temp_db):
        """Test custom query functionality."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("agent:tester:1", {"type": "test"})
        backend.put("agent:architect:1", {"type": "design"})
        backend.put("other:key", {"type": "other"})
        
        results = backend.query("key LIKE ?", ("agent:%",))
        
        assert len(results) == 2
        assert all(r["key"].startswith("agent:") for r in results)
    
    def test_sqlite_clear(self, temp_db):
        """Test clear operation."""
        backend = SQLiteBackend(temp_db)
        
        backend.put("key1", {"v": 1})
        backend.put("key2", {"v": 2})
        
        backend.clear()
        
        assert backend.get("key1") is None
        assert backend.get("key2") is None


class TestVectorBackend:
    """Test vector similarity search."""
    
    @pytest.fixture
    def temp_vec_db(self):
        """Create temporary vector database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "vectors.db")
            yield db_path
    
    @pytest.fixture
    def vector_backend(self, temp_vec_db):
        """Create vector backend instance."""
        return VectorBackend(temp_vec_db, dimension=384)
    
    def test_vector_init(self, vector_backend):
        """Test vector backend initialization."""
        assert vector_backend.dimension == 384
        assert vector_backend.count() == 0
    
    def test_vector_store(self, vector_backend):
        """Test storing vector."""
        embedding = [0.1] * 384
        vector_backend.store("test_vec", "test text", embedding)
        
        assert vector_backend.count() == 1
    
    def test_vector_retrieve(self, vector_backend):
        """Test retrieving vector."""
        embedding = [0.2] * 384
        metadata = {"type": "test"}
        vector_backend.store("retrieve_test", "some text", embedding, metadata)
        
        retrieved = vector_backend.retrieve("retrieve_test")
        
        assert retrieved is not None
        assert retrieved["text"] == "some text"
        assert retrieved["metadata"]["type"] == "test"
    
    def test_vector_dimension_check(self, vector_backend):
        """Test dimension validation."""
        wrong_embedding = [0.1] * 100  # Wrong dimension
        
        with pytest.raises(ValueError, match="dimension"):
            vector_backend.store("wrong_dim", "text", wrong_embedding)
    
    def test_vector_search(self, vector_backend):
        """Test similarity search."""
        # Create similar vectors
        query_vec = [0.9] + [0.1] * 383
        similar_vec1 = [0.85] + [0.15] * 383
        similar_vec2 = [0.8] + [0.2] * 383
        dissimilar_vec = [0.1] * 383 + [0.9]
        
        vector_backend.store("similar1", "text1", similar_vec1)
        vector_backend.store("similar2", "text2", similar_vec2)
        vector_backend.store("dissimilar", "text3", dissimilar_vec)
        
        results = vector_backend.search(query_vec, top_k=2, min_similarity=0.5)
        
        # Should find similar vectors
        assert len(results) >= 2
        assert results[0][0] in ["similar1", "similar2"]
    
    def test_vector_search_with_text(self, vector_backend):
        """Test search returning text and metadata."""
        embedding = [0.5] * 384
        metadata = {"agent": "tester", "version": "1.0"}
        vector_backend.store("test_vec", "test content", embedding, metadata)
        
        query_embedding = [0.51] * 384
        results = vector_backend.search_with_text(query_embedding, top_k=1)
        
        assert len(results) > 0
        assert results[0]["key"] == "test_vec"
        assert results[0]["text"] == "test content"
        assert results[0]["metadata"]["agent"] == "tester"
    
    def test_vector_metadata_filter(self, vector_backend):
        """Test search with metadata filtering."""
        embedding = [0.5] * 384
        
        vector_backend.store("agent:1", "agent1 text", embedding, {"type": "agent"})
        vector_backend.store("memory:1", "memory1 text", embedding, {"type": "memory"})
        
        query_embedding = [0.51] * 384
        
        # Filter for only agents
        results = vector_backend.search(
            query_embedding,
            top_k=10,
            metadata_filter={"type": "agent"}
        )
        
        assert len(results) >= 1
        assert all(
            vector_backend.retrieve(key)["metadata"]["type"] == "agent"
            for key, _ in results
        )
    
    def test_vector_delete(self, vector_backend):
        """Test deleting vector."""
        embedding = [0.5] * 384
        vector_backend.store("delete_vec", "text", embedding)
        
        assert vector_backend.count() == 1
        
        vector_backend.delete("delete_vec")
        
        assert vector_backend.count() == 0
        assert vector_backend.retrieve("delete_vec") is None
    
    def test_vector_list_keys(self, vector_backend):
        """Test listing vector keys."""
        embedding = [0.5] * 384
        
        vector_backend.store("agent:1", "text1", embedding)
        vector_backend.store("agent:2", "text2", embedding)
        vector_backend.store("memory:1", "text3", embedding)
        
        keys = vector_backend.list_keys("agent:")
        
        assert "agent:1" in keys
        assert "agent:2" in keys
        assert "memory:1" not in keys
    
    def test_vector_clear(self, vector_backend):
        """Test clearing all vectors."""
        embedding = [0.5] * 384
        
        vector_backend.store("vec1", "text1", embedding)
        vector_backend.store("vec2", "text2", embedding)
        
        assert vector_backend.count() == 2
        
        vector_backend.clear()
        
        assert vector_backend.count() == 0
    
    def test_vector_cosine_similarity(self, vector_backend):
        """Test cosine similarity calculation."""
        # Identical vectors should have similarity 1.0
        vec1 = [1.0] * 384
        vec2 = [1.0] * 384
        sim = vector_backend._cosine_similarity(vec1, vec2)
        
        assert abs(sim - 1.0) < 0.001
        
        # Orthogonal vectors should have similarity 0.0
        vec3 = [0.0] * 383 + [1.0]
        vec4 = [1.0] + [0.0] * 383
        sim2 = vector_backend._cosine_similarity(vec3, vec4)
        
        assert abs(sim2) < 0.001  # Should be ~0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
