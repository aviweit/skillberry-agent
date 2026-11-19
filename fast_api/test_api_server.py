import pytest
from fastapi.testclient import TestClient
import logging

from fast_api.api_server import api_server, ChatRequest, ChatMessage, redacted_headers


@pytest.fixture
def client():
    """Fixture to create a test client for the FastAPI app."""
    return TestClient(api_server)


def test_api_prompt_endpoint(client):
    """Test the /prompt endpoint."""
    response = client.post("/prompt", params={"user_prompt": "test prompt"})
    assert response.status_code == 200


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_redacted_headers_masks_credentials_only():
    """Credential headers are masked; skillberry-context-* headers are kept as received."""
    out = redacted_headers({"Authorization": "Bearer secret", "x-api-key": "k", "Cookie": "c",
                            "skillberry-context-env_id": "env-1", "content-type": "application/json"})
    assert out["Authorization"] == "<redacted>"
    assert out["x-api-key"] == "<redacted>" and out["Cookie"] == "<redacted>"
    assert out["skillberry-context-env_id"] == "env-1"
    assert out["content-type"] == "application/json"


def test_disconnect_logs_request_headers_at_info(client, caplog):
    """The incoming request's headers are logged at INFO, credentials masked."""
    with caplog.at_level(logging.INFO):
        client.post("/disconnect", json={}, headers={"skillberry-context-env_id": "env-log-1",
                                                     "skillberry-context-plugin": "test",
                                                     "Authorization": "Bearer secret"})
    lines = [r for r in caplog.records if "[REQUEST HEADERS]" in r.getMessage()]
    assert lines and all(r.levelno == logging.INFO for r in lines)
    msg = lines[0].getMessage()
    assert "POST /disconnect" in msg and "env-log-1" in msg
    assert "secret" not in msg and "<redacted>" in msg
