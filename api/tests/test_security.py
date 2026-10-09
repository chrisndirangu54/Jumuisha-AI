from fastapi.testclient import TestClient
from app.main import app

def test_public_endpoints_hardened():
    response=TestClient(app).get("/services")
    assert response.headers["x-content-type-options"]=="nosniff"
    assert response.headers["x-frame-options"]=="DENY"

def test_oversize_rejected():
    r=TestClient(app).post("/drafts",data=b"x",headers={"content-length":"1048577"})
    assert r.status_code==413

def test_oidc_unconfigured_fails_closed(monkeypatch):
    from app.oidc import verify_user_token
    import fastapi
    monkeypatch.delenv("JUMUISHA_OIDC_ISSUER",raising=False)
    with __import__("pytest").raises(fastapi.HTTPException) as exc:
        verify_user_token("arbitrary")
    assert exc.value.status_code==503
