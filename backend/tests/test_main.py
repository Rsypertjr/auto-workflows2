# backend/tests/test_main.py
import numbers

from fastapi.testclient import TestClient
from pytest_schema import schema

import app.main


def test_automated_health_check(monkeypatch):
    async def mock_verify_database_connected():
        return True

    monkeypatch.setattr(
        app.main, "verify_database_connected", mock_verify_database_connected
    )

    # Expected structure for the system metrics
    expected_schema = {
        "cpu_usage_percent": float,
        "memory_usage_percent": float,
        "memory_used_gb": float,
    }

    with TestClient(app.main.app) as client:
        response = client.get("/health")
        json_data = response.json()

        assert response.status_code == 200
        assert json_data["status"] == "healthy"
        assert json_data["database"] == "connected"
        assert isinstance(json_data["db_latency_ms"], numbers.Number)
        assert schema(expected_schema) == json_data["system_metrics"]


def test_automated_health_check_when_database_is_disconnected(monkeypatch):
    async def mock_verify_database_connected():
        return False

    monkeypatch.setattr(
        app.main, "verify_database_connected", mock_verify_database_connected
    )

    with TestClient(app.main.app) as client:
        response = client.get("/health")
        json_data = response.json()

        assert response.status_code == 503
        assert json_data["status"] == "unhealthy"
        assert json_data["database"] == "disconnected"
