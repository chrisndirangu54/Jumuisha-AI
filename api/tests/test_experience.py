from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_multilingual_routing():
    r=client.post("/v1/navigate",json={"query":"Nataka msaada wa ulemavu","language":"sw"})
    assert r.status_code == 200
    assert r.json()["matches"][0]["id"]=="ncpwd"

def test_unknown_does_not_invent():
    assert client.post("/v1/navigate",json={"query":"quantum teleporter"}).json()["matches"]==[]

def test_fees_not_invented():
    r=client.get("/v1/services/ecitizen/guide").json()
    assert r["fee_amount"] is None and not r["submission_enabled"]

def test_assistance_not_falsely_booked():
    r=client.post("/v1/assistance/plan",json={"service_id":"ntsa","need":"interpreter"}).json()
    assert r["request_not_sent"] is True

def test_integrations_not_live():
    assert client.get("/v1/integrations/health").json()["all_submissions_disabled"]
