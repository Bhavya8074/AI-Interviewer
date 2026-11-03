from pydantic import BaseModel, Field

class InterviewSetup(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    experience: str = "Fresher"
    interview_type: str = "Technical"
    question_count: int = Field(default=5, ge=1, le=10)
    company_rules: str = Field(default="", max_length=4000)
    dataset_context: str = Field(default="", max_length=12000)

class AnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1, max_length=8000)
    company: str
    role: str
    interview_type: str
    company_rules: str = ""

class ReportRequest(BaseModel):
    company: str
    role: str
    answers: list[dict]
