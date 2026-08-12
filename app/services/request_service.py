from sqlalchemy.orm import Session

from app.models.blood_request import BloodRequest
from app.models.donor import Donor
from app.models.enums import DonorAvailability, RequestStatus
from app.schemas.blood_request import BloodRequestCreate, BloodRequestUpdate
from app.schemas.donor import MatchingDonor
from app.utils.blood_compatibility import get_compatible_donor_groups


def get_requests(db: Session, user_id: str | None = None) -> list[BloodRequest]:
    query = db.query(BloodRequest).order_by(BloodRequest.created_at.desc())
    if user_id:
        query = query.filter(BloodRequest.user_id == user_id)
    return query.all()


def get_request_by_id(db: Session, request_id: str) -> BloodRequest | None:
    return db.query(BloodRequest).filter(BloodRequest.id == request_id).first()


def create_request(db: Session, user_id: str, payload: BloodRequestCreate) -> BloodRequest:
    request = BloodRequest(
        user_id=user_id,
        patient_name=payload.patient_name,
        blood_group=payload.blood_group,
        hospital=payload.hospital,
        city=payload.city,
        urgency=payload.urgency,
        contact_number=payload.contact_number,
        status=RequestStatus.OPEN,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def update_request(db: Session, request: BloodRequest, payload: BloodRequestUpdate) -> BloodRequest:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)
    db.commit()
    db.refresh(request)
    return request


def update_status(db: Session, request: BloodRequest, status: RequestStatus) -> BloodRequest:
    request.status = status
    db.commit()
    db.refresh(request)
    return request


def get_matching_donors(db: Session, request: BloodRequest) -> list[MatchingDonor]:
    compatible_groups = get_compatible_donor_groups(request.blood_group)
    donors = (
        db.query(Donor)
        .filter(Donor.city == request.city, Donor.blood_group.in_(compatible_groups))
        .all()
    )
    # Available donors first
    donors.sort(key=lambda d: d.availability != DonorAvailability.AVAILABLE)
    return [
        MatchingDonor(
            id=d.id,
            name=d.name,
            initials=d.initials,
            blood_group=d.blood_group,
            city=d.city,
            availability=d.availability,
        )
        for d in donors
    ]
