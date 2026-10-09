from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)

def test_unreviewed_information_not_passed_as_official():
    r=c.get("/v1/trust/services/kra-gavaconnect").json()
    assert r["verification"]=="not_reviewed"
    assert r["summary"] is None

def test_nonexistent_content():
    assert c.get("/v1/trust/services/not-a-service").status_code==404

def test_ksl_requires_approval():
    assert c.get("/v1/trust/ksl/unknown").json()["available"] is False

def test_release_never_marked_ready():
    d=c.get("/v1/trust/readiness").json()
    assert d["release_approved"] is False
    assert d["official_submissions"] is False
