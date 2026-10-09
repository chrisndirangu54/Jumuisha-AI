import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from app.main import app
import app.secure_drafts as storage

def test_private_storage_fails_closed_when_unconfigured(monkeypatch):
    monkeypatch.delenv("JUMUISHA_FERNET_KEY", raising=False)
    monkeypatch.delenv("JUMUISHA_PILOT_BEARER_TOKEN", raising=False)
    assert TestClient(app).get("/v1/private/drafts").status_code == 503

def test_encrypted_draft_roundtrip_and_deletion(monkeypatch, tmp_path):
    monkeypatch.setenv("JUMUISHA_FERNET_KEY", Fernet.generate_key().decode())
    monkeypatch.setenv("JUMUISHA_ENABLE_PILOT_AUTH", "true")
    monkeypatch.delenv("JUMUISHA_OIDC_ISSUER",raising=False)
    monkeypatch.setenv("JUMUISHA_PILOT_BEARER_TOKEN", "pilot-token-for-test-only")
    monkeypatch.setattr(storage, "DB", str(tmp_path / "pilot.sqlite3"))
    c = TestClient(app)
    auth={"Authorization":"Bearer pilot-token-for-test-only"}
    assert c.post("/v1/private/drafts", json={"service_id":"ecitizen","note":"test only","consent":False},headers=auth).status_code==422
    create=c.post("/v1/private/drafts",json={"service_id":"ecitizen","note":"test only","consent":True},headers=auth)
    assert create.status_code==200
    draft_id=create.json()["draft_id"]
    assert c.get("/v1/private/drafts",headers=auth).json()[0]["draft_id"]==draft_id
    assert c.get(f"/v1/private/drafts/{draft_id}",headers=auth).json()["note"]=="test only"
    with open(storage.DB,"rb") as f: assert b"test only" not in f.read()
    assert c.delete(f"/v1/private/drafts/{draft_id}",headers=auth).status_code==200
    assert c.get(f"/v1/private/drafts/{draft_id}",headers=auth).status_code==404
    assert c.get("/v1/private/drafts").status_code==401

def test_government_submission_remains_disabled():
    assert TestClient(app).post("/submit/ecitizen").status_code==501
