import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

from src.data.validate import run_validation
from src.features.preprocess import build_preprocess_pipeline, save_processed, stratified_split

CONFIG_PATH = Path("configs/train.yaml")
DATA_PATH = Path("data/raw/earthquake_data_tsunami.csv")
ARTIFACT_DIR = Path("artifacts/models")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def load_config(cfg_path: Path):
    with open(cfg_path, "r") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config(CONFIG_PATH)
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "./mlruns"))
    mlflow.set_experiment("tsunami-risk")

    # 0) validate data against schema (soft-fail)
    res = run_validation(
        DATA_PATH, Path("configs/schema.yaml"), Path("artifacts/metrics/validation_report.json")
    )
    strict = os.getenv("STRICT_VALIDATION", "0") == "1"
    if res["errors"] > 0:
        raise SystemExit(
            "Validation found critical errors. See artifacts/metrics/validation_report.json"
        )
    if strict and res["warnings"] > 0:
        raise SystemExit("STRICT_VALIDATION=1 and warnings present. See validation report.")

    df = pd.read_csv(DATA_PATH)

    target = cfg["target"]
    features = cfg["features"]

    split = stratified_split(df, features, target, cfg["test_size"], cfg["random_state"])
    save_processed(split, Path("data/processed"))

    if cfg["model"]["type"] == "RandomForestClassifier":
        estimator = RandomForestClassifier(
            **cfg["model"]["params"], random_state=cfg["random_state"]
        )
    else:
        raise ValueError("Unsupported model type")

    with mlflow.start_run():
        preprocess = build_preprocess_pipeline(features)
        model = Pipeline(steps=[("preprocess", preprocess), ("model", estimator)])
        model.fit(split.X_train, split.y_train)
        y_pred = model.predict(split.X_test)
        report = classification_report(split.y_test, y_pred, output_dict=True)
        print(json.dumps(report, indent=2))

        # log metrics
        mlflow.log_metrics(
            {
                "precision": report["weighted avg"]["precision"],
                "recall": report["weighted avg"]["recall"],
                "f1": report["weighted avg"]["f1-score"],
            }
        )

        # log params
        for k, v in cfg["model"]["params"].items():
            mlflow.log_param(k, v)

        # 1) Save local artifact
        model_path = ARTIFACT_DIR / "rf_pipeline.joblib"
        joblib.dump(model, model_path)
        mlflow.log_artifact(str(model_path))

        # 2) Log and **register** model in MLflow
        registered_name = os.getenv("MODEL_NAME", "tsunami-risk-classifier")
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=registered_name,
            input_example=split.X_test.head(2),
        )


if __name__ == "__main__":
    main()
