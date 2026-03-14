"""
Model Router Tests
==================

Test model router backend availability, routing logic, and default behavior.
"""

import pytest
import os
from sros.models.model_router import ModelRouter, get_router


class TestModelRouter:
    """Test model router initialization and backend management."""
    
    def test_router_initialization(self):
        """Test router initializes and checks backend availability."""
        router = ModelRouter()
        
        # Router should always be created
        assert router is not None
        assert isinstance(router._backend_status, dict)
    
    def test_gemini_backend_available(self):
        """Test Gemini backend availability (should be true with GEMINI_API_KEY set)."""
        router = ModelRouter()
        
        # Gemini should be available if GEMINI_API_KEY is set
        is_available = router.is_backend_available("gemini")
        has_key = bool(os.environ.get("GEMINI_API_KEY"))
        
        assert is_available == has_key
    
    def test_get_primary_backend(self):
        """Test that primary backend is always Gemini."""
        router = ModelRouter()
        
        assert router.get_primary_backend() == "gemini"
    
    def test_get_available_backends(self):
        """Test getting list of available backends."""
        router = ModelRouter()
        
        available = router.get_available_backends()
        assert isinstance(available, list)
        
        # Should have at least Gemini if API key is set
        if os.environ.get("GEMINI_API_KEY"):
            assert "gemini" in available
    
    def test_is_backend_available_unknown(self):
        """Test checking unknown backend returns False."""
        router = ModelRouter()
        
        assert router.is_backend_available("unknown_backend") is False
    
    def test_chat_gemini_default_backend(self):
        """Test that chat() defaults to Gemini backend."""
        router = ModelRouter()
        
        # If Gemini is not available, this should fail gracefully
        if not router.is_backend_available("gemini"):
            pytest.skip("Gemini API key not configured")
        
        result = router.chat("Test prompt")
        
        # Should return dict with expected keys
        assert isinstance(result, dict)
        assert "success" in result
        assert "backend" in result
        assert result["backend"] == "gemini"
    
    def test_chat_unknown_backend(self):
        """Test that unknown backend returns error."""
        router = ModelRouter()
        
        result = router.chat("Test", backend="unknown")
        
        assert result["success"] is False
        assert result["error"] is not None
        assert "Unknown backend" in result["error"]
    
    def test_chat_unavailable_backend(self):
        """Test that unavailable backend returns error."""
        router = ModelRouter()
        
        # OpenAI is likely not configured in test env
        result = router.chat("Test", backend="openai")
        
        # Should fail gracefully if not configured
        if not router.is_backend_available("openai"):
            assert result["success"] is False
            assert result["error"] is not None
    
    def test_chat_response_format(self):
        """Test that chat response has required fields."""
        router = ModelRouter()
        
        # Skip if no backends available
        available = router.get_available_backends()
        if not available:
            pytest.skip("No backends available")
        
        backend = available[0]
        result = router.chat("Hello", backend=backend, max_tokens=100)
        
        # Should always return dict with these keys
        assert isinstance(result, dict)
        assert "success" in result
        assert "text" in result
        assert "backend" in result
        assert "error" in result
    
    def test_global_router_singleton(self):
        """Test that get_router() returns singleton instance."""
        router1 = get_router()
        router2 = get_router()
        
        assert router1 is router2


class TestModelRouterIntegration:
    """Integration tests for model router."""
    
    def test_chat_with_temperature_parameter(self):
        """Test chat accepts temperature parameter."""
        router = ModelRouter()
        
        if not router.is_backend_available("gemini"):
            pytest.skip("Gemini not available")
        
        result = router.chat("Test", temperature=0.5, max_tokens=100)
        
        # Should succeed or fail gracefully
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_chat_with_max_tokens_parameter(self):
        """Test chat accepts max_tokens parameter."""
        router = ModelRouter()
        
        if not router.is_backend_available("gemini"):
            pytest.skip("Gemini not available")
        
        result = router.chat("Test", max_tokens=50)
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_backend_case_insensitive(self):
        """Test backend names are case-insensitive."""
        router = ModelRouter()
        
        if not router.is_backend_available("gemini"):
            pytest.skip("Gemini not available")
        
        # Both should work
        result1 = router.chat("Test", backend="gemini")
        result2 = router.chat("Test", backend="GEMINI")
        
        assert result1["backend"].lower() == result2["backend"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
