"""Safe public content publication and accessible alternate representations."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from .main import INDEX

router=APIRouter(prefix="/v1/trust",tags=["public-content-trust"])

class PublicContent(BaseModel):
    service_id: str
    locale: Literal["en","sw"]
    title: str
    summary: str
    official_url: str
    reviewed_at: datetime
    checksum: str

class SigningAsset(BaseModel):
    phrase_id: str
    media_url: str
    media_type: Literal["video/mp4","image/webp"]
    reviewer_id: str
    approved: bool
    captions: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

# Only public sample content: no user data or implied authoritative fee/eligibility rules.
_CONTENT = {}
_KSL = {}

def _safe_official_url(url: str, service_id: str) -> bool:
    expected=urlparse(INDEX[service_id].official_url)
    actual=urlparse(url)
    return actual.scheme == "https" and actual.hostname == expected.hostname and not actual.username and not actual.password

@router.get("/services/{service_id}")
def verified_content(service_id: str, locale: Literal["en","sw"]="en"):
    if service_id not in INDEX:
        raise HTTPException(404,"Unknown service")
    item=_CONTENT.get((service_id,locale))
    if item is None:
        return {"service_id":service_id,"locale":locale,"verification":"not_reviewed",
                "official_url":INDEX[service_id].official_url,"summary":None,
                "notice":"Use official agency information. No reviewed public content available."}
    return {"verification":"reviewed",**item.model_dump(mode="json")}

@router.get("/ksl/{phrase_id}")
def ksl_asset(phrase_id: str):
    item=_KSL.get(phrase_id)
    if item is None or not item.approved:
        return {"available":False,"fallback":"Text, captions or qualified interpreter","generative_signing":False}
    return {"available":True,**item.model_dump()}

@router.get("/readiness")
def readiness():
    return {"public_information_mode":True,"official_submissions":False,
            "verified_editorial_content_count":len(_CONTENT),
            "approved_ksl_asset_count":sum(1 for item in _KSL.values() if item.approved),
            "citizen_personal_data_collection_allowed":False,
            "field_accessibility_audit_passed":False,
            "release_approved":False}
