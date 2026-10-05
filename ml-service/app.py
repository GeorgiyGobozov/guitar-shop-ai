from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from model import TicketClassifier
from schemas import PredictRequest, PredictResponse, PredictionItem

classifier = TicketClassifier()


@asynccontextmanager
async def lifespan(app: FastAPI):
    classifier.load()
    yield


app = FastAPI(title="StringTheory ML Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": classifier._is_fitted}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    try:
        preds = classifier.predict(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PredictResponse(
        category=PredictionItem(**preds["category"].__dict__),
        priority=PredictionItem(**preds["priority"].__dict__),
        problem_type=PredictionItem(**preds["problem_type"].__dict__),
    )