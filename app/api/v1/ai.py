from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AIExtractedRequest, AIParseRequest
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/parse-request", response_model=AIExtractedRequest)
def parse_blood_request(
    payload: AIParseRequest,
    current_user: User = Depends(get_current_user),
) -> AIExtractedRequest:
    """
    Simulated AI extraction only — never creates or submits a blood
    request on its own. The frontend must show the result in an editable
    form for the user to review before calling POST /requests.
    """
    return ai_service.parse_blood_request(payload.text)
