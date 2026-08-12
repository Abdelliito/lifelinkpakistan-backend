from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import BloodGroup, City, DonorAvailability


class DonorCreate(BaseModel):
    blood_group: BloodGroup
    city: City
    phone: str
    availability: DonorAvailability = DonorAvailability.AVAILABLE
    last_donation_date: date | None = None


class DonorUpdate(BaseModel):
    blood_group: BloodGroup | None = None
    city: City | None = None
    phone: str | None = None
    availability: DonorAvailability | None = None
    last_donation_date: date | None = None


class DonorAvailabilityUpdate(BaseModel):
    availability: DonorAvailability


class DonorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    initials: str
    blood_group: BloodGroup
    city: City
    availability: DonorAvailability
    phone: str
    last_donation_date: date | None = None
    joined_date: date


class MatchingDonor(BaseModel):
    """Privacy-conscious view of a donor returned alongside a blood request."""

    id: str
    name: str
    initials: str
    blood_group: BloodGroup
    city: City
    availability: DonorAvailability
