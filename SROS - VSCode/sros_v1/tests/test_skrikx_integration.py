import sys
from unittest.mock import MagicMock, patch

# Mock boot BEFORE importing server to prevent real kernel boot
with patch("sros.kernel.kernel_bootstrap.boot") as mock_boot:
    mock_boot.return_value = MagicMock()
    from sros.nexus.api.server import app

import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def mock_kernel():
    """Mock the SROS Kernel for testing."""
    kernel = MagicMock()
    kernel.memory = MagicMock()
    kernel.memory.codex = MagicMock()
    kernel.memory.short_term = MagicMock()
    
    # Mock Codex return
    kernel.memory.codex.get_pack.return_value = "<srx_system>Mock Prompt</srx_system>"
    
    # Mock Short Term read
    kernel.memory.read.return_value = [{"role": "user", "content": "Hello"}]
    
    return kernel

@patch("sros.runtime.agents.skrikx_agent.chat")
def test_skrikx_chat_endpoint(mock_chat, mock_kernel):
    """Test the /api/skrikx/chat endpoint."""
    # Inject mock kernel into app state
    app.state.kernel = mock_kernel
    
    # Mock Model Response
    mock_chat.return_value = {
        "text": "I am Skrikx.",
        "backend": "gemini"
    }
    
    response = client.post("/api/skrikx/chat", json={
        "message": "Who are you?",
        "context": {"session_id": "test_session"}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["response"]["text"] == "I am Skrikx."
    
    # Verify Memory Write
    assert mock_kernel.memory.write.call_count == 2
    # 1. User message
    mock_kernel.memory.write.assert_any_call(
        {"role": "user", "content": "Who are you?"},
        layer="short",
        key="chat_history"
    )
    # 2. Agent response
    mock_kernel.memory.write.assert_any_call(
        {"role": "model", "content": "I am Skrikx."},
        layer="short",
        key="chat_history"
    )
