from pydantic import BaseModel, Field


class AIParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000, description="Free-text description of the emergency")


class AIExtractedRequest(BaseModel):
    """
    Structured fields extracted from free text. Fields are returned as
    plain strings (rather than enums) because extraction may be partial —
    the frontend is responsible for populating an editable form and
    letting the user confirm/correct every value before submission.
    """

    blood_group: str = ""
    hospital: str = ""
    city: str = ""
    urgency: str = ""
