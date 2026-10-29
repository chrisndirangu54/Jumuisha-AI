"""Independent incident evidence intake and regulator-gated review pilot.

Search results, news articles, RSS items, manual reports and partner APIs are *leads*.
No report in this module is published as a public emergency warning.
All state is in memory; do not use for production incident management.
"""
from __future__ import annotations
import hmac
import os
from datetime import datetime, timezone
from threading import RLock
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter(prefix="/v1/incident-intelligence", tags=["incident intelligence"])
Category = Literal["disease", "fire", "road_accident", "industrial_accident", "other_accident"]
Channel = Literal["manual", "licensed_api", "permitted_web", "official_bulletin"]
Decision = Literal["approved", "rejected"]

class EvidenceLead(BaseModel):
    category: Category
    channel: Channel
    title: str = Field(min_length=5, max_length=180)
    summary: str = Field(min_length=10, max_length=3000)
    county: str = Field(min_length=2, max_length=100)
    source_name: str = Field(min_length=2, max_length=160)
    source_url: HttpUrl
    observed_at: datetime
    submitted_by: str = Field(min_length=2, max_length=120)
    # No names, patient data, photos of casualties, identification numbers or contacts.
    no_personal_data_confirmed: bool = False

class Review(BaseModel):
    decision: Decision
    authority_name: str = Field(min_length=3, max_length=160)
    authority_reference: str = Field(min_length=3, max_length=160)
    reviewer: str = Field(min_length=3, max_length=160)
    rationale: str = Field(min_length=10, max_length=1500)
    # Documentary evidence must be verified out of band by the program operator.
    authorization_verified: bool = False

_lock = RLock()
_leads: dict[str, dict] = {}
_reviews: dict[str, dict] = {}

def _guard(supplied: str | None, env: str):
    expected = os.getenv(env, "")
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        raise HTTPException(403, "Configured service authorization required")

def _allowed_authority(category: str, authority_name: str) -> bool:
    # Fail closed: distinct authority allowlists per hazard category.
    prefix = "JUMUISHA_APPROVED_AUTHORITY_" + category.upper()
    return authority_name.casefold() in {
        value.strip().casefold() for value in os.getenv(prefix, "").split(",") if value.strip()
    }

@router.get("/status")
def status():
    return {"lead_sources_connected": False, "web_scraper_enabled": False,
            "approved_regulatory_partnerships_verified": False,
            "public_warning_publication_enabled": False,
            "durable_store": False, "mode": "review_pilot"}

@router.post("/leads", status_code=202)
def submit_lead(payload: EvidenceLead, x_incident_intake_key: str | None = Header(default=None)):
    _guard(x_incident_intake_key, "JUMUISHA_INCIDENT_INTAKE_KEY")
    if not payload.no_personal_data_confirmed:
        raise HTTPException(422, "Remove personal or patient-identifying information before submission")
    if payload.observed_at.tzinfo is None or payload.observed_at > datetime.now(timezone.utc):
        raise HTTPException(422, "Observation must include a valid timezone and cannot be in the future")
    key = str(uuid4())
    record = {"id": key, "lead": payload.model_dump(mode="json"),
              "state": "pending_review", "received_at": datetime.now(timezone.utc).isoformat()}
    with _lock:
        _leads[key] = record
    return {"id": key, "state": "pending_review", "public": False}

@router.get("/internal/leads")
def list_leads(x_incident_review_key: str | None = Header(default=None)):
    _guard(x_incident_review_key, "JUMUISHA_INCIDENT_REVIEW_KEY")
    with _lock:
        return list(_leads.values())

@router.post("/internal/leads/{lead_id}/review")
def review_lead(lead_id: str, payload: Review,
                x_incident_review_key: str | None = Header(default=None)):
    _guard(x_incident_review_key, "JUMUISHA_INCIDENT_REVIEW_KEY")
    with _lock:
        lead = _leads.get(lead_id)
        if lead is None:
            raise HTTPException(404, "Lead not found")
        if lead["state"] != "pending_review":
            raise HTTPException(409, "Lead already reviewed")
        if payload.decision == "approved":
            if not payload.authorization_verified:
                raise HTTPException(422, "Regulatory authorization must be independently verified")
            if not _allowed_authority(lead["lead"]["category"], payload.authority_name):
                raise HTTPException(403, "Regulatory body is not configured for this incident category")
        lead["state"] = "authority_review_recorded" if payload.decision == "approved" else "rejected"
        _reviews[lead_id] = {"decision": payload.decision, "authority": payload.authority_name,
                             "reference": payload.authority_reference,
                             "reviewer": payload.reviewer, "rationale": payload.rationale,
                             "reviewed_at": datetime.now(timezone.utc).isoformat()}
        return {"id": lead_id, "state": lead["state"], "public_warning_created": False}

@router.get("/internal/leads/{lead_id}/review")
def review_record(lead_id: str, x_incident_review_key: str | None = Header(default=None)):
    _guard(x_incident_review_key, "JUMUISHA_INCIDENT_REVIEW_KEY")
    with _lock:
        if lead_id not in _leads:
            raise HTTPException(404, "Lead not found")
        return _reviews.get(lead_id, {"state": "pending_review"})
