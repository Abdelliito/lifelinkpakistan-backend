from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BloodGroup, City, RequestStatus, UrgencyLevel


class BloodRequestCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    blood_group: BloodGroup
    hospital: str = Field(min_length=2, max_length=160)
    city: City
    urgency: UrgencyLevel
    contact_number: str = Field(min_length=7, max_length=30)


class BloodRequestUpdate(BaseModel):
    patient_name: str | None = None
    blood_group: BloodGroup | None = None
    hospital: str | None = None
    city: City | None = None
    urgency: UrgencyLevel | None = None
    contact_number: str | None = None


class BloodRequestStatusUpdate(BaseModel):
    status: RequestStatus


class BloodRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    patient_name: str
    blood_group: BloodGroup
    hospital: str
    city: City
    urgency: UrgencyLevel
    status: RequestStatus
    contact_number: str
    created_at: datetime
