from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.early_warning import _warnings

client = TestClient(app)

def payload():
    now = datetime.now(timezone.utc)
    return {
        "id": "test-flood-1", "title": "Flood warning", "description": "Floodwater expected",
        "hazard": "flood", "severity": "severe", "status": "actual",
        "county": "Nairobi", "issued_at": (now - timedelta(minutes=2)).isoformat(),
        "expires_at": (now + timedelta(hours=2)).isoformat(),
        "source_name": "Approved Test Agency", "source_url": "https://example.org/alerts/1",
        "instructions": ["Move to higher ground"], "verified": True
    }

def test_no_claim_of_live_agency_feed():
    state = client.get("/v1/early-warning/status").json()
    assert state["live_feed_connected"] is False
    assert state["public_push_enabled"] is False

def test_public_alert_feed_empty_by_default():
    _warnings.clear()
    assert client.get("/v1/early-warning/alerts").json() == []

def test_publishing_requires_key_and_approved_source(monkeypatch):
    _warnings.clear()
    monkeypatch.delenv("JUMUISHA_WARNING_INGEST_KEY", raising=False)
    assert client.post("/v1/early-warning/internal/alerts", json=payload()).status_code == 403
    monkeypatch.setenv("JUMUISHA_WARNING_INGEST_KEY", "dev-test-secret")
    monkeypatch.delenv("JUMUISHA_APPROVED_WARNING_SOURCES", raising=False)
    headers = {"X-Warning-Ingest-Key": "dev-test-secret"}
    assert client.post("/v1/early-warning/internal/alerts", json=payload(), headers=headers).status_code == 403
    monkeypatch.setenv("JUMUISHA_APPROVED_WARNING_SOURCES", "Approved Test Agency")
    p = payload()
    p["verified"] = False
    assert client.post("/v1/early-warning/internal/alerts", json=p, headers=headers).status_code == 422
    p["verified"] = True
    assert client.post("/v1/early-warning/internal/alerts", json=p, headers=headers).status_code == 201
    assert len(client.get("/v1/early-warning/alerts?county=Nairobi").json()) == 1
    assert client.get("/v1/early-warning/alerts?county=Kisumu").json() == []
    assert client.delete("/v1/early-warning/internal/alerts/test-flood-1", headers=headers).status_code == 200
    assert client.get("/v1/early-warning/alerts").json() == []

def test_sequential_update_and_retraction_tombstone(monkeypatch):
    from app.early_warning import _retractions
    _warnings.clear()
    _retractions.clear()
    monkeypatch.setenv("JUMUISHA_WARNING_INGEST_KEY", "dev-test-secret")
    monkeypatch.setenv("JUMUISHA_APPROVED_WARNING_SOURCES", "Approved Test Agency")
    headers = {"X-Warning-Ingest-Key": "dev-test-secret"}
    first = payload()
    assert client.post("/v1/early-warning/internal/alerts", json=first, headers=headers).status_code == 201
    repeated = dict(first)
    assert client.post("/v1/early-warning/internal/alerts", json=repeated, headers=headers).status_code == 409
    changed = dict(first, revision=2, message_type="update", description="Updated flood warning")
    assert client.post("/v1/early-warning/internal/alerts", json=changed, headers=headers).status_code == 201
    active = client.get("/v1/early-warning/alerts?county=Nairobi").json()
    assert active[0]["revision"] == 2
    assert active[0]["description"] == "Updated flood warning"
    assert client.delete("/v1/early-warning/internal/alerts/test-flood-1", headers=headers).status_code == 200
    assert client.get("/v1/early-warning/alerts").json() == []
    assert any(r["id"] == "test-flood-1" for r in client.get("/v1/early-warning/retractions").json())
    assert client.post("/v1/early-warning/internal/alerts", json=first, headers=headers).status_code == 409
    _retractions.clear()

def test_reject_naive_timestamps(monkeypatch):
    _warnings.clear()
    monkeypatch.setenv("JUMUISHA_WARNING_INGEST_KEY", "dev-test-secret")
    monkeypatch.setenv("JUMUISHA_APPROVED_WARNING_SOURCES", "Approved Test Agency")
    p = payload()
    p["issued_at"] = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    response = client.post("/v1/early-warning/internal/alerts", json=p, headers={"X-Warning-Ingest-Key": "dev-test-secret"})
    assert response.status_code == 422
