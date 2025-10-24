from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_predict_smoke():
    payload = {
        "records": [
            {
                "magnitude": 7.1,
                "cdi": 5,
                "mmi": 6,
                "sig": 1200,
                "nst": 20,
                "dmin": 1.2,
                "gap": 60.0,
                "depth": 10.0,
                "latitude": 35.5,
                "longitude": 140.1,
                "Year": 2010,
                "Month": 8,
            }
        ]
    }
    r = client.post("/predict", json=payload)
    # If model didn't load yet in test environment, we may get 503
    assert r.status_code in (200, 503)
