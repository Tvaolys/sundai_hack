from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)


def test_health_returns_ok_true():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
