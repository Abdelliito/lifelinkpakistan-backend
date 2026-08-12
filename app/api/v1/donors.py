from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import BloodGroup, City, DonorAvailability
from app.models.user import User
from app.schemas.donor import DonorAvailabilityUpdate, DonorCreate, DonorRead, DonorUpdate
from app.services import donor_service

router = APIRouter(prefix="/donors", tags=["Donors"])


@router.get("", response_model=list[DonorRead])
def search_donors(
    blood_group: BloodGroup | None = None,
    city: City | None = None,
    availability: DonorAvailability | None = None,
    db: Session = Depends(get_db),
) -> list[DonorRead]:
    donors = donor_service.search_donors(db, blood_group=blood_group, city=city, availability=availability)
    return [DonorRead.model_validate(d) for d in donors]


@router.get("/me", response_model=DonorRead)
def get_my_donor_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DonorRead:
    donor = donor_service.get_donor_by_user_id(db, current_user.id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have not registered as a donor yet.")
    return DonorRead.model_validate(donor)


@router.post("", response_model=DonorRead, status_code=201)
def create_donor_profile(
    payload: DonorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DonorRead:
    donor = donor_service.create_donor(db, current_user, payload)
    return DonorRead.model_validate(donor)


@router.get("/{donor_id}", response_model=DonorRead)
def get_donor(donor_id: str, db: Session = Depends(get_db)) -> DonorRead:
    donor = donor_service.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")
    return DonorRead.model_validate(donor)


def _get_owned_donor(donor_id: str, current_user: User, db: Session):
    donor = donor_service.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")
    if donor.user_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage your own donor profile.")
    return donor


@router.put("/{donor_id}", response_model=DonorRead)
def update_donor_profile(
    donor_id: str,
    payload: DonorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DonorRead:
    donor = _get_owned_donor(donor_id, current_user, db)
    donor = donor_service.update_donor(db, donor, payload)
    return DonorRead.model_validate(donor)


@router.patch("/{donor_id}/availability", response_model=DonorRead)
def update_donor_availability(
    donor_id: str,
    payload: DonorAvailabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DonorRead:
    donor = _get_owned_donor(donor_id, current_user, db)
    donor = donor_service.update_availability(db, donor, payload.availability)
    return DonorRead.model_validate(donor)


@router.delete("/{donor_id}", status_code=204)
def delete_donor_profile(
    donor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    donor = _get_owned_donor(donor_id, current_user, db)
    donor_service.delete_donor(db, donor)
