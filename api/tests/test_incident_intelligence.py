from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.incident_intelligence import _leads, _reviews

client = TestClient(app)

def lead():
    return {"category":"fire","channel":"manual","title":"Warehouse fire report",
            "summary":"A possible warehouse fire reported for analyst verification.",
            "county":"Nairobi","source_name":"Local source",
            "source_url":"https://example.org/source","observed_at":(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat(),
            "submitted_by":"Pilot partner","no_personal_data_confirmed":True}

def test_intake_is_private_and_requires_credentials(monkeypatch):
    _leads.clear()
    monkeypatch.delenv("JUMUISHA_INCIDENT_INTAKE_KEY",raising=False)
    assert client.post("/v1/incident-intelligence/leads",json=lead()).status_code==403
    assert client.get("/v1/incident-intelligence/internal/leads").status_code==403
    status=client.get("/v1/incident-intelligence/status").json()
    assert status["public_warning_publication_enabled"] is False

def test_authority_review_is_explicit_and_never_publishes(monkeypatch):
    _leads.clear()
    _reviews.clear()
    monkeypatch.setenv("JUMUISHA_INCIDENT_INTAKE_KEY","test-intake")
    monkeypatch.setenv("JUMUISHA_INCIDENT_REVIEW_KEY","test-review")
    monkeypatch.setenv("JUMUISHA_APPROVED_AUTHORITY_FIRE","County Fire Authority")
    intake={"X-Incident-Intake-Key":"test-intake"}
    review_header={"X-Incident-Review-Key":"test-review"}
    redacted=lead()
    redacted["no_personal_data_confirmed"]=False
    assert client.post("/v1/incident-intelligence/leads",json=redacted,headers=intake).status_code==422
    submitted=client.post("/v1/incident-intelligence/leads",json=lead(),headers=intake)
    assert submitted.status_code==202
    incident_id=submitted.json()["id"]
    assert submitted.json()["public"] is False
    approval={"decision":"approved","authority_name":"County Fire Authority",
        "authority_reference":"CASE-123","reviewer":"Pilot Reviewer",
        "rationale":"Authority permission documentation externally checked.",
        "authorization_verified":False}
    endpoint=f"/v1/incident-intelligence/internal/leads/{incident_id}/review"
    assert client.post(endpoint,json=approval,headers=review_header).status_code==422
    approval["authorization_verified"]=True
    approval["authority_name"]="Unlisted Organization"
    assert client.post(endpoint,json=approval,headers=review_header).status_code==403
    approval["authority_name"]="County Fire Authority"
    reviewed=client.post(endpoint,json=approval,headers=review_header)
    assert reviewed.status_code==200
    assert reviewed.json()["public_warning_created"] is False
    assert client.post(endpoint,json=approval,headers=review_header).status_code==409
    assert client.get("/v1/early-warning/alerts").status_code==200
