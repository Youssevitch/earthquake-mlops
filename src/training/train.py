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
from sklearn.model_selection import train_test_split

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

    df = pd.read_csv(DATA_PATH)

    target = cfg["target"]
    features = cfg["features"]

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg["test_size"], random_state=cfg["random_state"], stratify=y
    )

    if cfg["model"]["type"] == "RandomForestClassifier":
        model = RandomForestClassifier(
            **cfg["model"]["params"], random_state=cfg["random_state"]
        )
    else:
        raise ValueError("Unsupported model type")

    with mlflow.start_run():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
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

        # save model artifact
        model_path = ARTIFACT_DIR / "rf_model.joblib"
        joblib.dump(model, model_path)
        mlflow.log_artifact(str(model_path))


if __name__ == "__main__":
    main()
