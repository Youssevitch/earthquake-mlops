# Earthquake Tsunami MLOps — Presentation

## 1. Problem & Objective
- Predict tsunami potential (0/1) from earthquake features (magnitude, depth, location, etc.).
- Build a **production-grade MLOps pipeline** (on-prem) with training, serving, monitoring, and automated retraining.

## 2. Data
- CSV: `earthquake_data_tsunami.csv` (2001–2022)
- Target: `tsunami` (0/1)
- Key Features: magnitude, depth, latitude/longitude, intensity metrics, etc.
- Data validation: required columns, dtypes, ranges (soft-fail).

## 3. Modeling
- Algorithm: `RandomForestClassifier` (robust, interpretable feature importances).
- Pipeline: `SimpleImputer(strategy="median")` + RF.
- Train/Test split: stratified.

**Baseline metrics (example):**
- Weighted F1 ≈ **0.93**, Precision ≈ 0.93, Recall ≈ 0.93

## 4. Tracking & Versioning
- **MLflow** for experiments and **Model Registry**.
- Each train → new registered model version.
- Stages: Staging / Production; simple **rollback** supported.
- **DVC** for reproducible pipeline (train stage).

## 5. Serving (FastAPI)
- Endpoints: `/health`, `/predict`.
- Model loading: **Registry** via `MLFLOW_MODEL_URI` or local artifact fallback.
- Pydantic validation for inputs.

## 6. Monitoring & Auto-Retrain
- **Evidently** drift report (DataDrift + TargetDrift).
- HTML report + JSON summary; **threshold-based retraining** (default 0.30).
- Make targets: `make drift-report`, `make auto-retrain`.

## 7. CI/CD
- GitHub Actions: format, lint, tests, coverage, smoke train.
- Enforces repo health on PRs.

## 8. Architecture (high level)
```mermaid
flowchart LR
  A[CSV] --> V[Validate] --> P[Preprocess] --> T[Train → MLflow Run + Registry]
  T --> M[(Joblib artifact)]
  Registry --> API[FastAPI /predict]
  M --> API
  P --> D[Drift Report (Evidently)] --> R{Drift > thr?} -->|Yes| T
```
Notes: Registry-first serving; Evidently triggers retraining; DVC encapsulates pipeline.

## 9. Demo Script (5–7 min)
1. Show **MLflow UI** (runs + Model Registry).
2. Call **/health** and **/predict** (live).
3. Generate **drift report** → open HTML.
4. Run **auto-retrain** (maybe force with `DRIFT_THRESHOLD=0.01`).
5. Promote new version to **Production**, hit `/predict` again.

## 10. Risks & Mitigations
- Data quality drift → Evidently + validation.
- Model regression → Staging promotion & easy rollback.
- On-prem ops → Runbook + logging + Makefile.

## 11. Next Steps
- Feature importance and SHAP for explainability.
- Add auth & TLS for external exposure.
- Containerize (Docker) + orchestrate (K8s) when available.
- Add scheduled jobs (cron/Airflow) for drift checks.

## 12. Q&A Notes
- Why RF? Strong baseline for tabular data, fast inference, robust to scaling.
- Why Registry? Enables safe promotion/rollback and API/model decoupling.
- Why Evidently? Simple, interpretable drift metrics and reports.
