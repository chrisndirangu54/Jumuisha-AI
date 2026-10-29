"""Read-only public early-warning prototype.

No official feeds, alert dissemination or emergency dispatch is connected. The only
built-in item is demonstrative and is never presented as a current hazard.
"""
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/early-warning", tags=["public early warning"])
Hazard = Literal["flood", "severe_weather", "landslide", "drought", "wildfire", "health", "other"]
Status = Literal["actual", "exercise", "test"]
Severity = Literal["minor", "moderate", "severe", "extreme", "unknown"]

class Alert(BaseModel):
    id: str
    event: str
    hazard: Hazard
    status: Status
    severity: Severity
    source_name: str
    source_url: str
    source_verified: bool = False
    county: str | None = None
    subcounty: str | None = None
    issued_at: datetime
    expires_at: datetime
    headline_en: str = Field(min_length=1)
    headline_sw: str = Field(min_length=1)
    instruction_en: str = Field(min_length=1)
    instruction_sw: str = Field(min_length=1)
    ksl_reviewed_asset: str | None = None

# Demo fixtures do not represent current emergencies. Do NOT seed actual alerts.
_DEMO = [
    Alert(
        id="demo-flood-001", event="Flood preparedness exercise", hazard="flood",
        status="exercise", severity="moderate", source_name="Jumuisha AI demonstration",
        source_url="https://github.com/chrisndirangu54/Jumuisha-AI",
        source_verified=False, county="Nairobi",
        issued_at=datetime(2026, 10, 29, tzinfo=timezone.utc),
        expires_at=datetime(2027, 1, 1, tzinfo=timezone.utc),
        headline_en="EXERCISE ONLY: Flood preparedness", headline_sw="MAZOEZI PEKEE: Kujitayarisha kwa mafuriko",
        instruction_en="Practice identifying safer routes. For a real emergency, follow verified instructions from local authorities.",
        instruction_sw="Fanya mazoezi ya kutambua njia salama. Katika dharura halisi, fuata maelekezo rasmi ya mamlaka.",
    )
]

def _public_alerts(include_exercises: bool = False):
    now = datetime.now(timezone.utc)
    return [
        alert for alert in _DEMO
        if (include_exercises or alert.status == "actual")
        and alert.issued_at <= now < alert.expires_at
        and (alert.status != "actual" or alert.source_verified)
    ]

@router.get("/alerts", response_model=list[Alert])
def alerts(
    county: str | None = Query(default=None, max_length=100),
    hazard: Hazard | None = None,
    include_exercises: bool = False,
):
    items = _public_alerts(include_exercises)
    if county:
        items = [a for a in items if a.county is None or a.county.casefold() == county.strip().casefold()]
    if hazard:
        items = [a for a in items if a.hazard == hazard]
    return items

@router.get("/alerts/{alert_id}", response_model=Alert)
def alert_detail(alert_id: str, include_exercises: bool = False):
    match = next((a for a in _public_alerts(include_exercises) if a.id == alert_id), None)
    if match is None:
        raise HTTPException(404, "No active verified alert with that ID")
    return match

@router.get("/readiness")
def readiness():
    return {
        "mode": "demonstration_only",
        "live_official_feeds": False, "live_push_sms_ussd_ivr": False,
        "government_alert_authority": False, "automatic_ai_publication": False,
        "approved_ksl_alert_media": False,
        "actual_alerts": 0,
        "disclaimer": "No live emergency monitoring. Consult official disaster and weather authorities.",
    }
