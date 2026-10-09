"""Public-information accessibility workflows. Does not accept citizen identity data."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from urllib.parse import urlparse
from .main import SERVICES, INDEX

router = APIRouter(prefix="/v1", tags=["accessible experience"])

class NavigationRequest(BaseModel):
    query: str = Field(min_length=2, max_length=400)
    language: Literal["en","sw"] = "en"
    mode: Literal["text","voice","braille","ksl","easy_read","aac"] = "text"

@router.post("/navigate")
def navigate(req: NavigationRequest):
    # Deliberately deterministic: no unsafe LLM hallucination of government procedures.
    q=req.query.casefold()
    vocabulary={
        "kra-gavaconnect":["tax","pin","compliance","ushuru","kodi"],
        "kra-etims":["invoice","receipt","risiti","ankara"],
        "ecitizen":["passport","birth","certificate","cheti","citizen"],
        "ncpwd":["disability","wheelchair","ulemavu","assistive","mlemavu"],
        "brs":["business","company","biashara","kampuni"],
        "ntsa":["licence","license","vehicle","gari","driving"],
        "sha":["health","hospital","insurance","afya","matibabu"],
        "knbs":["statistics","data","takwimu"],
    }
    matched=[INDEX[k] for k,words in vocabulary.items() if any(word in q for word in words)]
    if not matched:
        return {"matches":[],"message":"I could not identify an official service. Choose a service from the catalogue." if req.language=="en" else "Sijapata huduma inayolingana. Chagua huduma kwenye orodha.","requires_confirmation":True}
    return {"matches":[s.model_dump() for s in matched],"message":"Review the official information before continuing." if req.language=="en" else "Kagua taarifa rasmi kabla ya kuendelea.","requires_confirmation":True}

class AssistanceRequest(BaseModel):
    service_id: str
    need: Literal["interpreter","accessible_kiosk","human_agent","legal_aid","braille","other"]
    preferred_language: Literal["en","sw","ksl"] = "en"

@router.post("/assistance/plan")
def assistance_plan(req: AssistanceRequest):
    if req.service_id not in INDEX:
        raise HTTPException(status_code=404,detail="Unknown service")
    return {"status":"self_service_guidance_only","request_not_sent":True,
            "service":req.service_id,"need":req.need,
            "message":"No live support-provider booking is configured. Contact the agency via its official site.",
            "official_url":INDEX[req.service_id].official_url}

@router.get("/accessibility/capabilities")
def capabilities():
    return {"validated_now":["text_scaling","contrast","reduced_motion","screen_reader_semantics","text_based_navigation"],
            "device_dependent":["system_tts","refreshable_braille_via_platform_accessibility","hardware_switch_access"],
            "requires_assets_or_provider":["kenyan_sign_language_human_reviewed_media","remote_interpreter","ivr","sms","ussd"],
            "experimental_not_enabled":["automatic_ksl_recognition","generative_signing","legal_or_medical_ai_decisions"]}

@router.get("/services/{service_id}/guide")
def service_guide(service_id: str):
    s=INDEX.get(service_id)
    if not s: raise HTTPException(status_code=404,detail="Unknown service")
    return {"service_id":s.id,"steps":[
       {"id":"review","label":"Read the latest agency instructions","requires_official_verification":True},
       {"id":"prepare","label":"Prepare only documents officially required by the agency","requires_official_verification":True},
       {"id":"open","label":"Continue securely on the agency's official portal","requires_official_verification":True}],
       "official_url":s.official_url,"fee_amount":None,"eligibility_decision":None,
       "submission_enabled":False,"human_assistance_available_in_app":False}

@router.get("/content/pictograms")
def pictograms():
    return {"icons":[{"key":"tax","icon":"receipt_long","text":"Tax"},{"key":"health","icon":"medical_services","text":"Health"},{"key":"help","icon":"support_agent","text":"Get help"},{"key":"transport","icon":"directions_car","text":"Transport"}],
            "status":"illustrative_symbols_not_aac_clinically_validated"}

@router.get("/integrations/health")
def integration_health():
    return {"government_api_live":False,"all_submissions_disabled":True,
            "discovery_only":[{"service":s.id,"official_url":s.official_url} for s in SERVICES]}
