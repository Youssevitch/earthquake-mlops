from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


@dataclass
class SplitData:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series


def build_preprocess_pipeline(numeric_features: List[str]) -> Pipeline:
    numeric = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])
    pre = ColumnTransformer(
        transformers=[("num", numeric, numeric_features)],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    return pre


def stratified_split(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    test_size: float,
    random_state: int,
) -> SplitData:
    X = df[features].copy()
    y = df[target].copy()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return SplitData(X_train, X_test, y_train, y_test)


def save_processed(split: SplitData, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    split.X_train.assign(tsunami=split.y_train).to_csv(out_dir / "train.csv", index=False)
    split.X_test.assign(tsunami=split.y_test).to_csv(out_dir / "test.csv", index=False)
