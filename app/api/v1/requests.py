from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.blood_request import (
    BloodRequestCreate,
    BloodRequestRead,
    BloodRequestStatusUpdate,
    BloodRequestUpdate,
)
from app.schemas.donor import MatchingDonor
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["Blood Requests"])


@router.get("", response_model=list[BloodRequestRead])
def list_requests(
    mine: bool = Query(True, description="If true, only return the current user's requests"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BloodRequestRead]:
    user_filter = current_user.id if (mine and current_user.role != UserRole.ADMIN) else None
    requests = request_service.get_requests(db, user_id=user_filter)
    return [BloodRequestRead.model_validate(r) for r in requests]


@router.post("", response_model=BloodRequestRead, status_code=201)
def create_request(
    payload: BloodRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BloodRequestRead:
    request = request_service.create_request(db, current_user.id, payload)
    return BloodRequestRead.model_validate(request)


def _get_owned_request(request_id: str, current_user: User, db: Session):
    request = request_service.get_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blood request not found.")
    if request.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage your own requests.")
    return request


@router.get("/{request_id}", response_model=BloodRequestRead)
def get_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BloodRequestRead:
    request = _get_owned_request(request_id, current_user, db)
    return BloodRequestRead.model_validate(request)


@router.put("/{request_id}", response_model=BloodRequestRead)
def update_request(
    request_id: str,
    payload: BloodRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BloodRequestRead:
    request = _get_owned_request(request_id, current_user, db)
    request = request_service.update_request(db, request, payload)
    return BloodRequestRead.model_validate(request)


@router.patch("/{request_id}/status", response_model=BloodRequestRead)
def update_request_status(
    request_id: str,
    payload: BloodRequestStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BloodRequestRead:
    request = _get_owned_request(request_id, current_user, db)
    request = request_service.update_status(db, request, payload.status)
    return BloodRequestRead.model_validate(request)


@router.get("/{request_id}/matching-donors", response_model=list[MatchingDonor])
def get_matching_donors(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MatchingDonor]:
    request = _get_owned_request(request_id, current_user, db)
    return request_service.get_matching_donors(db, request)
