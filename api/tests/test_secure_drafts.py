from fastapi.testclient import TestClient
from app.main import app
def test_private_storage_fails_closed_when_unconfigured(monkeypatch):
    monkeypatch.delenv("JUMUISHA_FERNET_KEY",raising=False)
    monkeypatch.delenv("JUMUISHA_PILOT_BEARER_TOKEN",raising=False)
    r=TestClient(app).get("/v1/private/drafts")
    # if configured in test environment, still requires authentication
    assert r.status_code in (401,503)
def test_no_live_government_submission():
    assert TestClient(app).post("/submit/ecitizen").status_code==501
