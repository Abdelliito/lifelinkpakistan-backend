from pydantic import BaseModel, Field


class AIParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000, description="Free-text description of the emergency")


class AIExtractedRequest(BaseModel):
    """
    Structured fields extracted from free text. Mapped to camelCase for Next.js frontend compatibility.
    """

    bloodGroup: str = Field(default="", alias="blood_group")
    hospital: str = Field(default="")
    city: str = Field(default="")
    urgency: str = Field(default="")

    class Config:
        populate_by_name = True

