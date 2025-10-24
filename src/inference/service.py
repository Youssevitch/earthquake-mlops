from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

DEFAULT_MODEL_PATH = Path(os.getenv("MODEL_PATH", "artifacts/models/rf_pipeline.joblib"))
MLFLOW_MODEL_URI = os.getenv("MLFLOW_MODEL_URI", "").strip()


class TsunamiModelService:
    def __init__(self, model_path: Path | str | None = None) -> None:
        if MLFLOW_MODEL_URI:
            tracking = os.getenv("MLFLOW_TRACKING_URI", "")
            if not tracking:
                raise RuntimeError(
                    "MLFLOW_MODEL_URI is set but MLFLOW_TRACKING_URI is not configured."
                )
            self.model = mlflow.sklearn.load_model(MLFLOW_MODEL_URI)
        else:
            mp = Path(model_path) if model_path else DEFAULT_MODEL_PATH
            if not mp.exists():
                raise FileNotFoundError(f"Model file not found at {mp}")
            self.model = joblib.load(mp)

        # infer expected feature order from the preprocess step
        try:
            preprocess = self.model.named_steps.get("preprocess")
            if preprocess is not None and hasattr(preprocess, "feature_names_in_"):
                self.feature_names_: List[str] = list(preprocess.feature_names_in_)
            else:
                self.feature_names_ = []
        except Exception:
            self.feature_names_ = []

    def _to_dataframe(self, rows: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(rows)
        if self.feature_names_:
            df = df[self.feature_names_]
        else:
            df = df.reindex(sorted(df.columns), axis=1)
        return df

    def predict_proba(self, rows: List[Dict]) -> List[float]:
        df = self._to_dataframe(rows)
        probs = self.model.predict_proba(df)[:, 1]
        return probs.tolist()

    def predict(self, rows: List[Dict]) -> List[int]:
        df = self._to_dataframe(rows)
        preds = self.model.predict(df)
        return [int(p) for p in preds]
