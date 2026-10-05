from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=4000)


class PredictionItem(BaseModel):
    label: str
    confidence: float


class PredictResponse(BaseModel):
    category: PredictionItem
    priority: PredictionItem
    problem_type: PredictionItem