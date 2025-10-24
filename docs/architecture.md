# System Architecture

```mermaid
flowchart LR
  subgraph Data
    A[earthquake_data_tsunami.csv]
  end

  subgraph Validation
    A --> V[Data Validation (schema)\nsrc/data/validate.py]
    V -->|report.json| VR[artifacts/metrics/validation_report.json]
  end

  subgraph Training
    V --> P[Preprocess Pipeline (impute)\nsrc/features/preprocess.py]
    P --> S[Stratified Split\ntrain/test]
    S --> T[Train RandomForest\nsrc/training/train.py]
    T --> M1[[artifacts/models/rf_pipeline.joblib]]
    T --> ML[(MLflow Run + Metrics)]
    ML --> MR[(MLflow Model Registry)]
  end

  subgraph Serving
    MR -->|models:/tsunami-risk-classifier/Production| API[FastAPI\nsrc/api/app.py]
    M1 -->|fallback MODEL_PATH| API
    API --> C[/Clients/]
  end

  subgraph Monitoring
    S --> D[Drift Report (Evidently)\nsrc/monitoring/drift_report.py]
    D --> H[HTML+JSON\nartifacts/plots/* & artifacts/metrics/*]
    H --> J{Auto-retrain?}
    J -->|> threshold| T
    J -->|otherwise| S2[(No action)]
  end
```

## Components

### Data validation (`src/data/validate.py`)
- **Purpose:** Soft-fail validation of schema (required columns, dtypes, allowed values) and value ranges. Generates `artifacts/metrics/validation_report.json`.
- **Policy:** Only *critical* issues (missing required columns, invalid target labels) block training. All other issues log warnings.
- **Why:** Keeps training robust while surfacing data quality issues early.

### Preprocessing (`src/features/preprocess.py`)
- **Steps:** Median imputation for numeric features. (Scaling not required for tree models.)
- **Packaging:** Implemented as a scikit-learn `Pipeline` + `ColumnTransformer` so inference matches training.

### Training (`src/training/train.py`)
- **Model:** `RandomForestClassifier` with `class_weight="balanced"`.
- **Metrics:** Precision/Recall/F1 (weighted), logged to MLflow; printed as JSON (now via logging).
- **Artifacts:** Local `artifacts/models/rf_pipeline.joblib`, MLflow run, and **Model Registry registration**.
- **Repro:** `dvc.yaml` provides a pipeline stage for `dvc repro`.

### Serving (`src/api/app.py`, `src/inference/service.py`)
- **FastAPI** endpoints:
  - `GET /health` – service and model status.
  - `POST /predict` – batch scoring (`records` list).
- **Model loading:**
  - Prefer `MLFLOW_MODEL_URI` (e.g., `models:/tsunami-risk-classifier/Production`).
  - Fallback to `MODEL_PATH` (`artifacts/models/rf_pipeline.joblib`).
- **Input validation:** Pydantic models with constraints & helpful error messages.

### Monitoring (`src/monitoring/drift_report.py`)
- **Tooling:** Evidently 0.4.x using `ColumnMapping(target="tsunami")`.
- **Outputs:** `artifacts/plots/evidently_report.html` and `artifacts/metrics/evidently_summary.json`.
- **Why:** Detect data drift and target drift; feed into automated retraining.

### Auto-retrain (`src/pipelines/auto_retrain.py`)
- **Logic:** Parses Evidently summary; if `share_of_drifted_columns` > threshold (default 0.30), triggers `python -m src.training.train`.
- **Ops switch:** Override threshold via `DRIFT_THRESHOLD` env var.

### Versioning
- **Data & pipeline:** DVC (`dvc.yaml`, `dvc.lock`).
- **Models & metrics:** MLflow (runs + registry). Local server with SQLite backend and file artifact store.

## Environments & Variables

| Variable | Where | Purpose |
|---|---|---|
| `MLFLOW_TRACKING_URI` | API/Train | Points to MLflow server (`http://127.0.0.1:5001`) |
| `MLFLOW_MODEL_URI` | API | Points to a registry model, e.g., `models:/tsunami-risk-classifier/Production` |
| `MODEL_PATH` | API | Fallback local artifact path (joblib) |
| `DRIFT_THRESHOLD` | Auto-retrain | Drift share threshold (default `0.30`) |
| `STRICT_VALIDATION` | Train | If `1`, warnings block training |

## Sequence (Happy Path)
1. `make train` → validate, preprocess, train, log to MLflow, register model.
2. Promote in MLflow UI or `src/models/registry.py`.
3. `make run-api` with `MLFLOW_MODEL_URI` → serve predictions.
4. `make drift-report` → generate drift report.
5. `make auto-retrain` → retrain if drift exceeds threshold.

