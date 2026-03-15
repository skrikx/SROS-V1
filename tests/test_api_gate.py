import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from sros.nexus.api.server import app


def test_api_is_quarantined_for_public_v1():
    client = TestClient(app)

    status = client.get("/api/status")
    assert status.status_code == 200
    payload = status.json()
    assert payload["api"]["public_v1"] is False
    assert payload["api"]["surface"] == "quarantined"

    blocked = client.get("/api/agents")
    assert blocked.status_code == 503
    assert "quarantined" in blocked.json()["detail"]
