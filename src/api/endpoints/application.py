from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_setting
from src.models.schemas import ApplicationRequest, FeedbackResponse
from src.services.agent_service import process_application

# Define the API router
router = APIRouter()


# Endpoint to analyze job application materials
@router.post("/analyze", response_model=FeedbackResponse)
def analyze_application(
    request: ApplicationRequest,
    settings=Depends(get_setting)
):
    try:
        response = process_application(
            request.resume, request.job_description, settings)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
