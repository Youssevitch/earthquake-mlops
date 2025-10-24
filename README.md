# Earthquake Tsunami MLOps (On-Prem)

End-to-end MLOps project predicting tsunami potential from earthquake features.

## Highlights
- **Model**: RandomForestClassifier wrapped in a preprocessing `Pipeline`
- **Serving**: FastAPI with `/predict` and `/health`
- **Tracking & Registry**: MLflow local server (SQLite backend)
- **Monitoring**: Evidently drift report + auto-retrain trigger
- **Reproducibility**: DVC pipeline; Makefile tasks; tests & CI

## Quickstart
```bash
# env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pre-commit install

# train
make train

# start MLflow server (new terminal)
export MLFLOW_BACKEND_URI="sqlite:///mlruns.db"
export MLFLOW_ARTIFACT_ROOT="$(pwd)/mlruns"
mlflow server --backend-store-uri "$MLFLOW_BACKEND_URI" --default-artifact-root "$MLFLOW_ARTIFACT_ROOT" --host 127.0.0.1 --port 5001

# promote & serve from registry
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001
python -m src.models.registry promote --name tsunami-risk-classifier --version 1 --stage Production
export MLFLOW_MODEL_URI=models:/tsunami-risk-classifier/Production
make run-api
```

## API
- `GET /health` → liveness + model status
- `POST /predict` → batch scoring (`{"records":[{...}]}`)

Example:
```bash
curl -s -X POST "http://0.0.0.0:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"records":[{"magnitude":7.2,"cdi":6,"mmi":6,"sig":1200,"nst":20,"dmin":1.2,"gap":60.0,"depth":10.0,"latitude":35.5,"longitude":140.1,"Year":2010,"Month":8}]}'
```

## Monitoring & Auto-Retrain
```bash
make drift-report                  # Evidently HTML + JSON
make auto-retrain                  # retrain if drift share > 0.30
DRIFT_THRESHOLD=0.10 make auto-retrain  # override threshold
```

## Make commands
- `make format` / `make lint` / `make test`
- `make train` / `make run-api`
- `make drift-report` / `make auto-retrain`

## Project structure
```
src/
  api/        # FastAPI app + schemas
  data/       # validation
  features/   # preprocessing
  inference/  # model loading service
  monitoring/ # Evidently drift
  models/     # registry helper
  training/   # training script
configs/      # schema + training
data/         # raw/processed
artifacts/    # models/metrics/plots
```

## Docs
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Runbook](docs/runbook.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
