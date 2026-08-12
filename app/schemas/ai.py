from pydantic import BaseModel, Field, model_validator


class AIParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000, description="Free-text description of the emergency")


class AIExtractedRequest(BaseModel):
    """
    Structured fields extracted from free text description of blood emergency.
    Exposes both `blood_group` (snake_case) and `bloodGroup` (camelCase) for
    backend API and Next.js frontend compatibility.
    """

    blood_group: str = Field(default="")
    bloodGroup: str = Field(default="")
    hospital: str = Field(default="")
    city: str = Field(default="")
    urgency: str = Field(default="")

    @model_validator(mode="after")
    def sync_blood_group_fields(self) -> "AIExtractedRequest":
        val = self.blood_group or self.bloodGroup
        self.blood_group = val
        self.bloodGroup = val
        return self


