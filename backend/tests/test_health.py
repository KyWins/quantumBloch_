from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_reports_cache_stats():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "cache" in payload
    assert {"entries", "hits", "misses", "hit_rate"}.issubset(payload["cache"].keys())
