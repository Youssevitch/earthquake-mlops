# Operations Runbook

This runbook describes how to operate the on-prem tsunami risk service: start services, promote/rollback, monitor, and troubleshoot.

---

## 1) Start & Stop

### MLflow server (Model Registry)
```bash
export MLFLOW_BACKEND_URI="sqlite:///mlruns.db"
export MLFLOW_ARTIFACT_ROOT="$(pwd)/mlruns"
mlflow server \
  --backend-store-uri "$MLFLOW_BACKEND_URI" \
  --default-artifact-root "$MLFLOW_ARTIFACT_ROOT" \
  --host 127.0.0.1 --port 5001
```

### API server (FastAPI via Uvicorn)
**From Model Registry:**
```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001
export MLFLOW_MODEL_URI=models:/tsunami-risk-classifier/Production
make run-api
```

**From local artifact (fallback):**
```bash
unset MLFLOW_MODEL_URI
export MODEL_PATH=artifacts/models/rf_pipeline.joblib
make run-api
```

Stop servers with `CTRL+C` in their terminals.

---

## 2) Train, Register, Promote, Rollback

### Train & Register
```bash
make train   # logs run + registers new model version
```

### Promote to Production
```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001
python -m src.models.registry promote --name tsunami-risk-classifier --version <N> --stage Production
```

### Rollback Production
```bash
python -m src.models.registry rollback --name tsunami-risk-classifier --version <N>
```

---

## 3) Monitoring & Auto-Retrain

### Generate Drift Report (Evidently)
```bash
make train         # ensures processed data exists
make drift-report  # -> artifacts/plots/evidently_report.html & artifacts/metrics/evidently_summary.json
```

### Auto-Retrain Based on Drift
```bash
make auto-retrain                 # uses default DRIFT_THRESHOLD=0.30
DRIFT_THRESHOLD=0.10 make auto-retrain  # example override
```

---

## 4) CI/CD (GitHub Actions)

- Workflow: `.github/workflows/ci.yaml`
- Steps: setup Python, install dependencies, lint (black/isort/flake8), test, upload coverage, smoke-train.
- Requires PAT with `repo` + `workflow` scopes to push workflow changes (if using HTTPS).

---

## 5) Troubleshooting

### API `/health` returns nothing or connection refused
- API not running. Start with `make run-api`.
- If using registry, ensure MLflow server is running and `MLFLOW_TRACKING_URI` set.

### 503 Model not available
- Check env vars: `MLFLOW_TRACKING_URI`, `MLFLOW_MODEL_URI`.
- Confirm model exists in MLflow UI under **Models** and stage is correct.

### Validation fails
- Inspect `artifacts/metrics/validation_report.json`.
- Adjust `configs/schema.yaml` (e.g., relax ranges) or fix dataset.

### MLflow “integer columns with missing values” warning
- Optional: cast numeric inputs to float in preprocessing (already supported); or ensure your request rows don’t contain nulls for integer fields.

### Evidently errors about ColumnMapping or path types
- Use `ColumnMapping(target="tsunami")` and pass string paths to `save_html`.

### Git pushes to workflows rejected
- Update PAT to include `workflow` scope or switch to SSH.

---

## 6) Backups & Versioning

- **MLflow artifacts**: `mlruns/` directory; **registry DB**: `mlruns.db` (SQLite). Back up both for model history.
- **Data & pipeline**: `dvc.yaml` and `dvc.lock` describe reproducible pipeline; use `dvc repro` to rebuild.
- **Tags**: create release tags after stable merges:
  ```bash
  git tag -a v0.1.1 -m "Polished baseline"
  git push origin v0.1.1
  ```

---

## 7) Security & Access (on-prem notes)
- If exposing API beyond localhost, add authentication (e.g., API key or OAuth2) and TLS termination (reverse proxy).
- Restrict access to MLflow UI if it contains sensitive artifacts/metrics.

---

## 8) Performance & Capacity
- Uvicorn workers can be scaled via `--workers N` (behind an nginx reverse proxy).
- RandomForest inference is fast; batch scoring accepted (`records` list). For high QPS, run multiple API instances behind a load balancer.

