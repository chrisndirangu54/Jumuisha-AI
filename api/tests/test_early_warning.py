from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_default_never_exposes_exercise_as_live_alert():
    response = client.get("/v1/early-warning/alerts")
    assert response.status_code == 200
    assert response.json() == []

def test_exercise_explicitly_labeled_and_unverified():
    response = client.get("/v1/early-warning/alerts?include_exercises=true")
    assert response.status_code == 200
    alerts = response.json()
    assert alerts
    assert all(a["status"] == "exercise" and not a["source_verified"] for a in alerts)

def test_geographic_and_hazard_filter():
    yes = client.get("/v1/early-warning/alerts?include_exercises=true&county=Nairobi&hazard=flood")
    no = client.get("/v1/early-warning/alerts?include_exercises=true&county=Kisumu")
    assert len(yes.json()) == 1
    assert no.json() == []

def test_no_fake_operational_readiness():
    readiness = client.get("/v1/early-warning/readiness").json()
    assert readiness["mode"] == "demonstration_only"
    assert readiness["live_official_feeds"] is False
    assert readiness["automatic_ai_publication"] is False

def test_no_public_alert_submission_endpoint():
    assert client.post("/v1/early-warning/alerts", json={}).status_code == 405
