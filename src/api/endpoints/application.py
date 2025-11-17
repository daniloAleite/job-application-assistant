from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_setting
from src.models.schemas import ApplicationRequest, FeedbackResponse


router = APIRouter()


@router.post("/analyze", response_model=FeedbackResponse)
def analyze_application(
    request: ApplicationRequest,
    settings: Depends(get_setting)
):
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
