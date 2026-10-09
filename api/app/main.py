"""Accessible public-service navigation API. No live government submission is enabled."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Jumuisha AI", version="0.1.0", description="Accessibility-first public service navigator. Demonstration workflows only.")

class AccessMode(str, Enum):
    text = "text"
    voice = "voice"
    large_text = "large_text"
    screen_reader = "screen_reader"
    braille = "braille"
    ksl = "ksl"
    easy_read = "easy_read"
    switch = "switch"
    reduced_motion = "reduced_motion"

class Service(BaseModel):
    id: str
    name: str
    agency: str
    description: str
    status: Literal["information_only", "documented_api", "approval_required"]
    official_url: str
    online_submission_enabled: bool = False
    disclaimer: str = "Verify current eligibility, fees and requirements directly with the responsible agency."

SERVICES = [
    Service(id="kra-gavaconnect",name="KRA tax services",agency="Kenya Revenue Authority",description="Understand tax PIN verification and other supported services; approved integration required for transactions.",status="documented_api",official_url="https://www.kra.go.ke/"),
    Service(id="kra-etims",name="eTIMS invoicing",agency="Kenya Revenue Authority",description="Accessible electronic invoicing guidance; production integration requires official onboarding.",status="documented_api",official_url="https://www.kra.go.ke/"),
    Service(id="ecitizen",name="eCitizen services",agency="Government of Kenya",description="Find government services and access the official portal.",status="approval_required",official_url="https://www.ecitizen.go.ke/"),
    Service(id="ncpwd",name="Disability services",agency="National Council for Persons with Disabilities",description="Find official disability-services information; verify eligibility with the council.",status="information_only",official_url="https://ncpwd.go.ke/"),
    Service(id="brs",name="Business registration",agency="Business Registration Service",description="Registration information and official application guidance.",status="approval_required",official_url="https://brs.go.ke/"),
    Service(id="ntsa",name="Transport services",agency="NTSA",description="Vehicle and licensing service navigation.",status="approval_required",official_url="https://www.ntsa.go.ke/"),
    Service(id="sha",name="Health insurance information",agency="Social Health Authority",description="Official health coverage guidance; no eligibility or benefits guarantees.",status="approval_required",official_url="https://sha.go.ke/"),
    Service(id="knbs",name="Public statistics",agency="Kenya National Bureau of Statistics",description="Discover public statistics and data collections.",status="information_only",official_url="https://www.knbs.or.ke/"),
]
INDEX = {s.id:s for s in SERVICES}

class Preferences(BaseModel):
    modes: list[AccessMode] = Field(default_factory=lambda: [AccessMode.text])
    language: str = Field(default="sw", max_length=20)
    text_scale: float = Field(default=1.0,ge=1,le=3)
    captions: bool = True
    low_bandwidth: bool = False

class DraftRequest(BaseModel):
    service_id: str
    user_confirmed: bool = False
    consent_to_store: bool = False
    note: str = Field(default="",max_length=2000)

class DraftResponse(BaseModel):
    id: str
    status: str
    submission_enabled: bool = False
    warning: str

# Demonstration only. Store nothing sensitive in memory/logs; no real persistence.
@app.get("/health")
def health():
    return {"status":"ok","live_agency_submissions":False}

@app.get("/services",response_model=list[Service])
def services():
    return SERVICES

@app.get("/services/{service_id}",response_model=Service)
def service(service_id: str):
    if service_id not in INDEX:
        raise HTTPException(status_code=404,detail="Service not found")
    return INDEX[service_id]

@app.post("/preferences/preview")
def preview_preferences(preferences: Preferences):
    return {"preferences":preferences,"message":"Preferences preview only; no profile persisted."}

@app.get("/accessibility/ksl")
def ksl_manifest():
    return {"language":"ksl","content_state":"sample_only","assets":[],"fallback":"text_or_qualified_human_interpreter","synthetic_translation_enabled":False}

@app.get("/integrations")
def integrations():
    return [{"service_id":s.id,"status":s.status,"authorized":False,"submissions_enabled":False} for s in SERVICES]

@app.post("/drafts",response_model=DraftResponse)
def create_draft(payload: DraftRequest):
    if payload.service_id not in INDEX:
        raise HTTPException(status_code=404,detail="Service not found")
    if not payload.consent_to_store:
        raise HTTPException(status_code=422,detail="Explicit consent is required before storing a draft")
    return DraftResponse(id=str(uuid4()),status="preview_only_not_saved",warning="No data was stored or submitted. This is a demonstration draft receipt.")

@app.post("/submit/{service_id}")
def submit(service_id: str):
    if service_id not in INDEX:
        raise HTTPException(status_code=404,detail="Service not found")
    raise HTTPException(status_code=501,detail="Live government submission is unavailable until official integration and authorization are completed.")

# Read-only accessible navigation routes. Import after the catalogue is initialized.
from .experience import router as experience_router
app.include_router(experience_router)
