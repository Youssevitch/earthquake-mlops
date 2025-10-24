from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from src.api.schemas import PredictRequest, PredictResponse, PredictResponseRow
from src.inference.service import TsunamiModelService

APP_NAME = "Tsunami Risk API"
APP_VERSION = "0.2.0"

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Load model at startup (one time)
try:
    service = TsunamiModelService(model_path=os.getenv("MODEL_PATH"))
except Exception as e:
    # Defer failure to first predict call with clear message
    service = None
    load_error = str(e)
else:
    load_error = ""


@app.get("/health")
def health():
    ok = service is not None
    return {"status": "ok" if ok else "error", "model_loaded": ok, "error": load_error}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if service is None:
        raise HTTPException(status_code=503, detail=f"Model not available: {load_error}")

    rows = [r.model_dump() for r in req.records]
    probs = service.predict_proba(rows)
    labels = [1 if p >= 0.5 else 0 for p in probs]

    resp = PredictResponse(
        predictions=[
            PredictResponseRow(proba=float(p), label=int(y)) for p, y in zip(probs, labels)
        ]
    )
    return resp
