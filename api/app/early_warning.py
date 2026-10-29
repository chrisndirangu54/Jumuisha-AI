"""Public early warnings: read-only public feed and authenticated official ingestion.

No sample emergency is ever surfaced as live. Production needs a durable store,
audited publisher identities, approved official sources and delivery providers.
"""
from __future__ import annotations
import hmac
import os
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter(prefix="/v1/early-warning", tags=["public early warning"])
Hazard = Literal["flood", "landslide", "drought", "wildfire", "severe_weather",
                 "earthquake", "epidemic", "industrial", "other"]
Severity = Literal["minor", "moderate", "severe", "extreme"]
Status = Literal["actual", "exercise", "test"]

class Warning(BaseModel):
    id: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9._:-]+$")
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=3, max_length=4000)
    hazard: Hazard
    severity: Severity
    status: Status = "actual"
    county: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    issued_at: datetime
    expires_at: datetime
    source_name: str = Field(min_length=3, max_length=150)
    source_url: HttpUrl
    instructions: list[str] = Field(min_length=1, max_length=12)
    language: str = Field(default="en", pattern=r"^(en|sw)$")
    verified: bool = False

    def live(self, now: datetime) -> bool:
        return (self.verified and self.status == "actual"
                and self.issued_at <= now < self.expires_at)

# Explicitly ephemeral until a transactionally safe and audited database exists.
# Worker restarts clear all warnings; never represent this as a production feed.
_warnings: dict[str, Warning] = {}

def _now() -> datetime:
    return datetime.now(timezone.utc)

@router.get("/status")
def system_status():
    return {"live_feed_connected": False, "durable_storage": False,
            "public_push_enabled": False, "message":
            "Pilot API only. No approved live agency feed, SMS or push connection."}

@router.get("/alerts", response_model=list[Warning])
def alerts(county: str | None = Query(default=None, max_length=100),
           hazard: Hazard | None = None):
    now = _now()
    result = [a for a in _warnings.values() if a.live(now)]
    if county:
        result = [a for a in result if a.county.casefold() in (county.casefold(), "national", "all")]
    if hazard:
        result = [a for a in result if a.hazard == hazard]
    return sorted(result, key=lambda x: x.issued_at, reverse=True)

@router.post("/internal/alerts", status_code=201)
def publish(alert: Warning, x_warning_ingest_key: str | None = Header(default=None)):
    configured = os.getenv("JUMUISHA_WARNING_INGEST_KEY", "")
    if not configured or not x_warning_ingest_key or not hmac.compare_digest(configured, x_warning_ingest_key):
        raise HTTPException(403, "Official alert ingestion is not configured or authorized")
    if not alert.verified or alert.status != "actual":
        raise HTTPException(422, "Only verified actual warnings may be published")
    now = _now()
    if alert.issued_at > now or alert.expires_at <= now or alert.expires_at <= alert.issued_at:
        raise HTTPException(422, "Invalid alert validity interval")
    allowlist = [s.strip().casefold() for s in os.getenv("JUMUISHA_APPROVED_WARNING_SOURCES", "").split(",") if s.strip()]
    if alert.source_name.casefold() not in allowlist:
        raise HTTPException(403, "Publisher is not on the explicitly approved source list")
    _warnings[alert.id] = alert
    return {"id": alert.id, "status": "stored_ephemerally", "delivery_enabled": False}

@router.delete("/internal/alerts/{alert_id}")
def retract(alert_id: str, x_warning_ingest_key: str | None = Header(default=None)):
    configured = os.getenv("JUMUISHA_WARNING_INGEST_KEY", "")
    if not configured or not x_warning_ingest_key or not hmac.compare_digest(configured, x_warning_ingest_key):
        raise HTTPException(403, "Unauthorized")
    _warnings.pop(alert_id, None)
    return {"id": alert_id, "retracted": True}
