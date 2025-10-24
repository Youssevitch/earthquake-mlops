from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, confloat, conint


class TsunamiFeatures(BaseModel):
    magnitude: confloat(ge=0)  # model trained on >=6.5, but allow wider range
    cdi: conint(ge=0, le=9)
    mmi: conint(ge=1, le=12)  # some datasets use up to 12; safe upper bound
    sig: conint(ge=0)
    nst: Optional[conint(ge=0)] = None
    dmin: Optional[confloat(ge=0)] = None
    gap: Optional[confloat(ge=0)] = None
    depth: confloat(ge=0)
    latitude: float
    longitude: float
    Year: conint(ge=1900, le=2100)
    Month: conint(ge=1, le=12)


class PredictRequest(BaseModel):
    records: List[TsunamiFeatures] = Field(..., min_length=1, description="List of rows to score")


class PredictResponseRow(BaseModel):
    proba: float
    label: int


class PredictResponse(BaseModel):
    predictions: List[PredictResponseRow]
