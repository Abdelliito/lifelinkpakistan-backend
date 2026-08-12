from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.schemas.admin import PlatformStats
from app.schemas.blood_request import BloodRequestRead, BloodRequestStatusUpdate
from app.schemas.donor import DonorRead
from app.schemas.user import UserRead
from app.services import admin_service, donor_service, request_service

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=PlatformStats)
def get_stats(db: Session = Depends(get_db)) -> PlatformStats:
    return admin_service.get_platform_stats(db)


# ── Users ────────────────────────────────────────────────────────────────────


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[UserRead]:
    return [UserRead.model_validate(u) for u in admin_service.list_users(db)]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> None:
    from app.services.auth_service import get_user_by_id

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.role.value == "ADMIN":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin accounts cannot be deleted.")
    admin_service.delete_user(db, user)


# ── Donors ───────────────────────────────────────────────────────────────────


@router.get("/donors", response_model=list[DonorRead])
def list_donors(db: Session = Depends(get_db)) -> list[DonorRead]:
    return [DonorRead.model_validate(d) for d in admin_service.list_donors(db)]


@router.delete("/donors/{donor_id}", status_code=204)
def delete_donor(donor_id: str, db: Session = Depends(get_db)) -> None:
    donor = donor_service.get_donor_by_id(db, donor_id)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donor not found.")
    admin_service.delete_donor(db, donor)


# ── Blood Requests ───────────────────────────────────────────────────────────


@router.get("/requests", response_model=list[BloodRequestRead])
def list_requests(db: Session = Depends(get_db)) -> list[BloodRequestRead]:
    return [BloodRequestRead.model_validate(r) for r in admin_service.list_requests(db)]


@router.patch("/requests/{request_id}/status", response_model=BloodRequestRead)
def update_request_status(request_id: str, payload: BloodRequestStatusUpdate, db: Session = Depends(get_db)) -> BloodRequestRead:
    request = request_service.get_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found.")
    request = request_service.update_status(db, request, payload.status)
    return BloodRequestRead.model_validate(request)
