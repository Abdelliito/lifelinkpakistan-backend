from sqlalchemy.orm import Session

from app.models.blood_request import BloodRequest
from app.models.donor import Donor
from app.models.enums import DonorAvailability, RequestStatus
from app.models.user import User
from app.schemas.admin import PlatformStats


def get_platform_stats(db: Session) -> PlatformStats:
    return PlatformStats(
        total_users=db.query(User).count(),
        total_donors=db.query(Donor).count(),
        available_donors=db.query(Donor).filter(Donor.availability == DonorAvailability.AVAILABLE).count(),
        active_requests=db.query(BloodRequest).filter(BloodRequest.status == RequestStatus.OPEN).count(),
    )


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def list_donors(db: Session) -> list[Donor]:
    return db.query(Donor).order_by(Donor.joined_date.desc()).all()


def delete_donor(db: Session, donor: Donor) -> None:
    db.delete(donor)
    db.commit()


def list_requests(db: Session) -> list[BloodRequest]:
    return db.query(BloodRequest).order_by(BloodRequest.created_at.desc()).all()
