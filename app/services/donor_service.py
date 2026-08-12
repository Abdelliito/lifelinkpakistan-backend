from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.donor import Donor
from app.models.enums import BloodGroup, City, DonorAvailability, UserRole
from app.models.user import User
from app.schemas.donor import DonorCreate, DonorUpdate


def _initials_from_name(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts[:2]).upper()


def search_donors(
    db: Session,
    blood_group: BloodGroup | None = None,
    city: City | None = None,
    availability: DonorAvailability | None = None,
) -> list[Donor]:
    query = db.query(Donor)
    if blood_group:
        query = query.filter(Donor.blood_group == blood_group)
    if city:
        query = query.filter(Donor.city == city)
    if availability:
        query = query.filter(Donor.availability == availability)

    donors = query.all()
    # Available donors surface first, mirroring the frontend's mock search behavior
    return sorted(donors, key=lambda d: d.availability != DonorAvailability.AVAILABLE)


def get_donor_by_id(db: Session, donor_id: str) -> Donor | None:
    return db.query(Donor).filter(Donor.id == donor_id).first()


def get_donor_by_user_id(db: Session, user_id: str) -> Donor | None:
    return db.query(Donor).filter(Donor.user_id == user_id).first()


def create_donor(db: Session, user: User, payload: DonorCreate) -> Donor:
    if get_donor_by_user_id(db, user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have a donor profile.")

    donor = Donor(
        user_id=user.id,
        name=user.name,
        initials=_initials_from_name(user.name),
        blood_group=payload.blood_group,
        city=payload.city,
        phone=payload.phone,
        availability=payload.availability,
        last_donation_date=payload.last_donation_date,
    )
    db.add(donor)

    user.is_donor = True
    if user.role == UserRole.USER:
        user.role = UserRole.DONOR

    db.commit()
    db.refresh(donor)
    return donor


def update_donor(db: Session, donor: Donor, payload: DonorUpdate) -> Donor:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donor, field, value)
    db.commit()
    db.refresh(donor)
    return donor


def update_availability(db: Session, donor: Donor, availability: DonorAvailability) -> Donor:
    donor.availability = availability
    db.commit()
    db.refresh(donor)
    return donor


def delete_donor(db: Session, donor: Donor) -> None:
    db.delete(donor)
    db.commit()
