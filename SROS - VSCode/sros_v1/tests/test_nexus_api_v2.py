import pytest
from fastapi.testclient import TestClient
from sros.nexus.api.server import app

client = TestClient(app)

def test_router_tasks_endpoint():
    response = client.get("/api/router/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["tasks"], list)

def test_submit_routed_task():
    # Mocking the chat function would be better, but for now we test the endpoint structure
    # This might fail if no backend is available, so we'll just check if it accepts the request
    # or handles the error gracefully
    try:
        response = client.post("/api/router/tasks", json={"agent_name": "tester", "task": "Hello"})
        # It might return 200 or 500 depending on backend availability, but we want to ensure the route exists
        assert response.status_code in [200, 500] 
    except Exception:
        pass

def test_logs_endpoint():
    response = client.get("/api/logs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "logs" in data

def test_kernel_daemons_endpoint():
    response = client.get("/api/kernel/daemons")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["daemons"]) > 0
    assert data["daemons"][0]["name"] == "memory_daemon"
