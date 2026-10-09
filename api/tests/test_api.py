from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health_is_not_live():
    assert client.get("/health").json()["live_agency_submissions"] is False

def test_catalogue():
    response=client.get("/services")
    assert response.status_code==200
    assert len(response.json()) >= 8
    assert all(not s["online_submission_enabled"] for s in response.json())

def test_missing_service():
    assert client.get("/services/nonexistent").status_code==404

def test_submission_blocked():
    assert client.post("/submit/kra-gavaconnect").status_code==501

def test_draft_requires_consent():
    assert client.post("/drafts",json={"service_id":"ecitizen"}).status_code==422

def test_ksl_never_fabricated():
    d=client.get("/accessibility/ksl").json()
    assert d["synthetic_translation_enabled"] is False
    assert not d["assets"]
