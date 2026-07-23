# backend/tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app
import httpx
import pytest
import numbers
from pytest_schema import schema, exact_schema

def test_automated_health_check():  
    
    #Expected structure for the system metrics
    expected_schema = {
        "cpu_usage_percent": float,
        "memory_usage_percent": float,
        "memory_used_gb": float        
    }
    
    with TestClient(app) as client:
        response = client.get("/health")
        #assert response.status_code == 200
        json_data = response.json()
        print(json_data)
        assert isinstance(json_data['db_latency_ms'], numbers.Number)
        assert schema(expected_schema) == json_data['system_metrics']
    