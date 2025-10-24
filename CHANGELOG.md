# Changelog

## v0.1.1 — Polished Baseline
- Added docs: architecture, API reference, ops runbook
- Logging added to training and API
- Extra inference service smoke test
- CI workflow (lint, test, smoke-train)
- MLflow Model Registry integration for serving
- Evidently drift report + auto-retrain threshold

## v0.1.0 — First Working Baseline
- Repo scaffold with DVC, MLflow, FastAPI, training script
- Validation (soft-fail) + preprocessing pipeline
- Baseline RandomForest model training & artifact
- Basic API with `/health` and `/predict`
