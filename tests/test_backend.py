from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_forecast():
    response = client.get("/forecast")
    assert response.status_code == 200
    data = response.json()
    assert "as_of" in data
    assert "horizon_days" in data
    assert data["horizon_days"] == 30
    assert "last_price" in data
    assert "point" in data
    assert "interval_80" in data
    assert "low" in data["interval_80"]
    assert "high" in data["interval_80"]
    assert "regime" in data
    assert "label" in data["regime"]
    assert "vol_pct" in data["regime"]
    assert "history" in data
    assert isinstance(data["history"], list)
    assert len(data["history"]) > 0
    assert "date" in data["history"][0]
    assert "close" in data["history"][0]


def test_scenario():
    response = client.get("/scenario")
    assert response.status_code == 200
    data = response.json()
    assert "as_of" in data
    assert "regime" in data
    assert "narrative" in data
    assert "source" in data
    assert data["source"] == "stub"


def test_model_card():
    response = client.get("/model-card")
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "horizon_days" in data
    assert data["horizon_days"] == 30
    assert "target" in data
    assert "features" in data
    assert isinstance(data["features"], list)
    assert "evaluation" in data
    assert "oos_period" in data["evaluation"]
    assert "rmse" in data["evaluation"]
    assert "skill_vs_rw" in data["evaluation"]
    assert "per_year_rmse" in data["evaluation"]
    assert "data_sources" in data
    assert "framing" in data
