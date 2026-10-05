from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(..., max_length=120)
    customer_email: EmailStr
    subject: str = Field(..., max_length=255)
    description: str = Field(..., min_length=2)


class TicketOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    subject: str
    description: str
    ml_category: str | None
    ml_priority: str | None
    ml_problem_type: str | None
    ml_confidence: float | None
    status: str
    assignee: str | None
    created_at: datetime

    class Config:
        from_attributes = True