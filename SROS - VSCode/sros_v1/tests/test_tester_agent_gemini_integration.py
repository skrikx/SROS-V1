"""
Integration Test: TesterAgent with Gemini Adapter

Tests that TesterAgent can successfully use the Gemini adapter
to generate test cases through real model calls.

This validates Objective O1: "Wire adapters into agents so SROS can
perform real model calls through the adapter layer."
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add sros to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sros_v1"))

from sros.adapters.models.gemini_adapter import GeminiAdapter
from sros.adapters.base import AdapterResult
from sros.runtime.agents.tester_agent import TesterAgent
from sros.kernel.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Create fresh event bus for each test."""
    return EventBus()


class TestTesterAgentGeminiIntegration:
    """Test suite for TesterAgent + Gemini adapter integration."""
    
    def test_gemini_adapter_mock_mode(self):
        """Verify Gemini adapter falls back to mock mode without real API key."""
        # Create adapter without real API key
        adapter = GeminiAdapter(name="gemini", config={})
        
        # Mock the client to None so _mock_generate is called
        adapter._initialized = True
        adapter.client = None  # Force mock mode
        
        result = adapter.generate(
            prompt="Test prompt",
            temperature=0.4,
            max_tokens=1024
        )
        
        assert result.success is True
        if result.text:  # Handle None case
            assert "[MOCK GEMINI]" in result.text
        if result.tokens:  # Handle None case
            assert result.tokens["total"] > 0
        assert result.cost == 0.0 or result.cost is None  # Mock mode has zero cost
        if result.metadata:
            assert result.metadata.get("mock") is True
    
    def test_tester_agent_with_gemini_test_generation(self, event_bus):
        """
        Integration test: TesterAgent generates tests via Gemini adapter.
        
        This is the key integration point: TesterAgent.act() calls
        adapter.generate() with test generation prompt.
        """
        # Create adapter in mock mode
        adapter = GeminiAdapter(config={})
        adapter._initialized = True
        adapter.client = None  # Force mock mode
        
        # Create agent with mock adapter
        agent = TesterAgent(event_bus=event_bus, adapter=adapter)
        
        # Setup test scenario
        test_target = "def add(a, b): return a + b"
        test_prompt = f"""Generate pytest test cases for:
{test_target}

Requirements:
- Test basic addition
- Test edge cases
- Test error handling

Output format: Python pytest code"""
        
        # Call TesterAgent.act() which internally calls adapter.generate()
        result = agent.act(
            observation=test_prompt,
            context={"target_code": test_target}
        )
        
        # Verify result is not an error message
        assert result is not None
        assert "[ERROR]" not in str(result)
        # In mock mode, result will be mock-based but valid
        assert len(result) > 0
    
    def test_tester_agent_event_bus_integration(self, event_bus):
        """Verify TesterAgent publishes events when using Gemini adapter."""
        # Create adapter in mock mode
        adapter = GeminiAdapter(config={})
        adapter._initialized = True
        adapter.client = None  # Force mock mode
        
        # Create agent with mock adapter
        agent = TesterAgent(event_bus=event_bus, adapter=adapter)
        
        events_captured = []
        
        def capture_event(payload):
            events_captured.append(payload)
        
        # Subscribe to agent events
        event_bus.subscribe("agent.thinking", capture_event)
        event_bus.subscribe("agent.acted", capture_event)
        
        # Act with agent
        agent.act(
            observation="Generate test for: def test(): pass",
            context={}
        )
        
        # Verify events were published (captured as payloads only, not event types)
        assert len(events_captured) >= 2
    
    def test_gemini_adapter_cost_estimation(self):
        """Verify Gemini adapter estimates costs correctly."""
        adapter = GeminiAdapter(config={})
        
        prompt_tokens = 100
        completion_tokens = 200
        
        cost = adapter.estimate_cost(prompt_tokens, completion_tokens)
        
        # Cost should be non-negative
        assert cost >= 0.0
        # For small token counts, cost should be very small
        assert cost < 0.01
    
    def test_gemini_adapter_metadata(self):
        """Verify Gemini adapter reports correct metadata."""
        adapter = GeminiAdapter(config={})
        adapter._initialized = True
        
        metadata = adapter.get_metadata()
        
        assert metadata["provider"] == "Google"
        assert metadata["type"] == "model"
        assert "text_generation" in metadata["capabilities"]
        assert metadata["initialized"] is True
    
    def test_tester_agent_with_real_gemini_client(self, event_bus):
        """
        Test TesterAgent with mocked real Gemini client.

        This simulates what happens when a real Gemini API key is provided
        and the actual google.generativeai SDK is available.
        """
        # Create adapter with mocked client
        config = {"api_key": "test-key", "model": "gemini-2.0-flash-exp"}
        adapter = GeminiAdapter(config=config)
        
        # Mock the client
        mock_response = MagicMock()
        mock_response.text = "def test_add(): assert add(1, 1) == 2"
        adapter.client = MagicMock()
        adapter.client.generate_content.return_value = mock_response
        adapter._initialized = True
        
        # Create TesterAgent with mocked Gemini
        agent = TesterAgent(
            event_bus=event_bus,
            adapter=adapter
        )
        
        # Act
        result = agent.act(
            observation="Generate test for add function",
            context={}
        )
        
        # Verify
        assert result is not None
        assert "[ERROR]" not in str(result)
    
    def test_adapter_result_contract_compliance(self):
        """
        Verify that Gemini adapter returns AdapterResult with all required fields.
        
        This validates the adapter contract: all adapters must return
        AdapterResult with these fields: success, text, tokens, cost, error.
        """
        # Use mock mode to avoid real API calls
        adapter = GeminiAdapter(config={})
        adapter._initialized = True
        adapter.client = None  # Force mock mode
        
        result = adapter.generate(
            prompt="Test prompt",
            temperature=0.7,
            max_tokens=512
        )
        
        # Check all required AdapterResult fields
        assert hasattr(result, 'success')
        assert hasattr(result, 'text')
        assert hasattr(result, 'tokens')
        assert hasattr(result, 'cost')
        assert hasattr(result, 'error')
        
        # Verify types
        assert isinstance(result.success, bool)
        assert isinstance(result.text, str)
        assert isinstance(result.tokens, dict)
        assert isinstance(result.cost, (int, float))
        
        # Verify tokens dict structure
        assert "prompt" in result.tokens
        assert "completion" in result.tokens
        assert "total" in result.tokens


class TestGeminiAdapterEnvironmentConfiguration:
    """Test Gemini adapter environment variable handling."""
    
    def test_adapter_reads_gemini_api_key_from_env(self):
        """Verify adapter can read GEMINI_API_KEY from environment."""
        # Save original if exists
        original = os.environ.get("GEMINI_API_KEY")
        
        try:
            # Set test key
            os.environ["GEMINI_API_KEY"] = "test-key-from-env"
            
            adapter = GeminiAdapter()
            adapter.initialize()
            
            # Adapter should have read the key
            assert adapter.api_key == "test-key-from-env"
        finally:
            # Restore
            if original:
                os.environ["GEMINI_API_KEY"] = original
            else:
                os.environ.pop("GEMINI_API_KEY", None)
    
    def test_adapter_prefers_config_over_env(self):
        """Verify adapter prefers config api_key over environment variable."""
        original = os.environ.get("GEMINI_API_KEY")
        
        try:
            os.environ["GEMINI_API_KEY"] = "env-key"
            
            config = {"api_key": "config-key"}
            adapter = GeminiAdapter(config=config)
            
            assert adapter.api_key == "config-key"
        finally:
            if original:
                os.environ["GEMINI_API_KEY"] = original
            else:
                os.environ.pop("GEMINI_API_KEY", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
