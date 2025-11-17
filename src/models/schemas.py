from pydantic import BaseModel, Field


# Schema for application request
class ApplicationRequest(BaseModel):
    resume: str = Field(..., description="User resume(plain text)")
    job_description: str = Field(...,
                                 description="Job description(plain text)")


# Schema for application response
class FeedbackResponse(BaseModel):
    feedback: str
    cover_letter_suggestion: str
    resume_Improvement: str


class ApplicationStateSchema(BaseModel):
    resume: str
    job_description: str
    job_requirements: str = ""
    resume_skills: str = ""
    feedback: str = ""
    cover_letter_suggestion: str = ""
    resume_improvements: str = ""
