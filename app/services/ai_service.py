"""
SIMULATED AI REQUEST ASSISTANT
-------------------------------------------------------------------------
This does NOT call Google Gemini or any external LLM. It performs
lightweight, deterministic keyword/regex parsing over the input text to
approximate what an AI extraction step would return, matching the
behavior of the frontend's mock `ai.service.ts` exactly so both layers
demo consistently.

To integrate a real AI backend later, replace the body of
`parse_blood_request` with a call to your provider of choice and keep
the same `AIExtractedRequest` return shape.
"""

import re

from fastapi import HTTPException, status

from app.models.enums import City
from app.schemas.ai import AIExtractedRequest

_HOSPITAL_KEYWORDS = [
    "Mayo Hospital",
    "Aga Khan Hospital",
    "PIMS Hospital",
    "Nishtar Hospital",
    "Jinnah Hospital",
    "Shaukat Khanum",
    "Services Hospital",
    "Civil Hospital",
    "Liaquat National Hospital",
    "Combined Military Hospital",
    "CMH",
]

_URGENT_PATTERN = re.compile(r"\burgent(ly)?\b|\bcritical\b|\bemergency\b|\basap\b|\bimmediately\b", re.IGNORECASE)
_SOON_PATTERN = re.compile(r"\bsoon\b|\btoday\b|\bwithin hours\b", re.IGNORECASE)
_BLOOD_GROUP_PATTERN = re.compile(r"\b(A|B|AB|O)\s?([+-])(?=[\s,.!?)]|$)", re.IGNORECASE)
_VALID_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
_HOSPITAL_FALLBACK_PATTERN = re.compile(r"at\s+([A-Z][\w'&]*(?:\s+[A-Z][\w'&]*)*\s+Hospital)")


def _extract_blood_group(text: str) -> str:
    match = _BLOOD_GROUP_PATTERN.search(text)
    if not match:
        return ""
    candidate = f"{match.group(1).upper()}{match.group(2)}"
    return candidate if candidate in _VALID_GROUPS else ""


def _extract_city(text: str) -> str:
    for city in City:
        if re.search(rf"\b{re.escape(city.value)}\b", text, re.IGNORECASE):
            return city.value
    return ""


def _extract_hospital(text: str) -> str:
    lowered = text.lower()
    for hospital in _HOSPITAL_KEYWORDS:
        if hospital.lower() in lowered:
            return "Combined Military Hospital" if hospital == "CMH" else hospital
    fallback = _HOSPITAL_FALLBACK_PATTERN.search(text)
    return fallback.group(1) if fallback else ""


def _extract_urgency(text: str) -> str:
    if _URGENT_PATTERN.search(text):
        return "Critical"
    if _SOON_PATTERN.search(text):
        return "Urgent"
    return "Normal"


def parse_blood_request(text: str) -> AIExtractedRequest:
    trimmed = text.strip()
    if not trimmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please describe the emergency first.")
    if len(trimmed) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not understand the request. Please add a few more details.",
        )

    blood_group = _extract_blood_group(trimmed)
    city = _extract_city(trimmed)
    hospital = _extract_hospital(trimmed)
    urgency = _extract_urgency(trimmed)

    if not blood_group and not city and not hospital:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="AI could not extract any details from that description. Try including the blood group, hospital, and city.",
        )

    return AIExtractedRequest(blood_group=blood_group, hospital=hospital, city=city, urgency=urgency)
