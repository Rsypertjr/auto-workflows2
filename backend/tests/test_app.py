import pytest
from fastapi.testclient import TestClient
from app.app import app


def test_hello_endpoint():
    with TestClient(app) as client:
        response = client.get("/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
