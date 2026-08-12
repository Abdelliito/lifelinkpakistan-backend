"""
GOOGLE GEMINI AI REQUEST ASSISTANT
-------------------------------------------------------------------------
Extracts structured blood emergency details (blood group, city, hospital,
urgency level) from freeform text using Google Gemini AI, with automatic
deterministic fallback if API key is not configured or network calls fail.
"""

import os
import re

from fastapi import HTTPException, status

from app.core.config import settings
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


def _fallback_parse(trimmed: str) -> AIExtractedRequest:
    blood_group = _extract_blood_group(trimmed)
    city = _extract_city(trimmed)
    hospital = _extract_hospital(trimmed)
    urgency = _extract_urgency(trimmed)

    if not blood_group and not city and not hospital:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="AI could not extract any details from that description. Try including the blood group, hospital, and city.",
        )

    return AIExtractedRequest(bloodGroup=blood_group, hospital=hospital, city=city, urgency=urgency)


def parse_blood_request(text: str) -> AIExtractedRequest:
    trimmed = text.strip()
    if not trimmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please describe the emergency first.")
    if len(trimmed) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not understand the request. Please add a few more details.",
        )

    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        return _fallback_parse(trimmed)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = f"""You are a medical assistant for LifeLink Pakistan. Extract details from this emergency blood request:
"{trimmed}"

Provide a JSON object with these EXACT keys:
- "bloodGroup": Blood group string. Must be exactly one of: "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", or "" if unknown.
- "hospital": Name of the hospital (e.g., "Mayo Hospital", "Aga Khan Hospital", "PIMS Hospital") or "" if unknown.
- "city": City in Pakistan. Must be one of: "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta", "Sialkot", "Hyderabad", or "" if unknown.
- "urgency": Urgency level. Must be exactly one of: "Critical", "Urgent", "Normal". Default to "Normal" if not specified.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if response.text:
            import json

            data = json.loads(response.text)
            extracted = AIExtractedRequest(
                bloodGroup=data.get("bloodGroup", "") or data.get("blood_group", ""),
                hospital=data.get("hospital", ""),
                city=data.get("city", ""),
                urgency=data.get("urgency", "Normal"),
            )
            return extracted

        return _fallback_parse(trimmed)
    except Exception:
        # Fallback to regex parsing if external call fails
        return _fallback_parse(trimmed)


