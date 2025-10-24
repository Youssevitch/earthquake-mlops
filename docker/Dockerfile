# ---- Base image
FROM python:3.11-slim

# ---- System deps (curl only for debugging; remove if you like)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Workdir
WORKDIR /app

# ---- Copy requirements and install (layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# ---- Copy source code (no artifacts/data)
COPY src /app/src
COPY configs /app/configs

# ---- Env (can override at runtime)
ENV MODEL_PATH=/app/artifacts/models/rf_pipeline.joblib \
    MLFLOW_TRACKING_URI=/app/mlruns \
    PYTHONUNBUFFERED=1

# ---- Expose API port
EXPOSE 8000

# ---- Default command
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
