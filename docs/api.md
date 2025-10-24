# Tsunami Risk API

Base URL (local): `http://0.0.0.0:8000`

## Authentication
None (local on-prem demo). Add auth middleware if exposing beyond localhost.

## Content Type
All requests are JSON: `application/json`.

---

## GET `/health`

**Description:** Liveness & model readiness.

**Response 200**
```json
{
  "status": "ok",
  "model_loaded": true,
  "error": ""
}
```
- `status`: `"ok"` or `"error"`
- `model_loaded`: boolean
- `error`: message if model failed to load

---

## POST `/predict`

**Description:** Batch-score tsunami potential for one or more rows.

**Request Body**
```json
{
  "records": [
    {
      "magnitude": 7.2,
      "cdi": 6,
      "mmi": 6,
      "sig": 1200,
      "nst": 20,
      "dmin": 1.2,
      "gap": 60.0,
      "depth": 10.0,
      "latitude": 35.5,
      "longitude": 140.1,
      "Year": 2010,
      "Month": 8
    }
  ]
}
```

**Constraints (pydantic)**
- `magnitude`: float (>= 0)
- `cdi`: int (0..9)
- `mmi`: int (1..12)
- `sig`: int (>= 0)
- `nst`: int (>= 0, optional)
- `dmin`: float (>= 0, optional)
- `gap`: float (>= 0, optional)
- `depth`: float (>= 0)
- `latitude`: float
- `longitude`: float
- `Year`: int (1900..2100)
- `Month`: int (1..12)

**Response 200**
```json
{
  "predictions": [
    { "proba": 0.73, "label": 1 }
  ]
}
```
- `proba`: float in [0,1]
- `label`: int {0,1} (threshold 0.5)

**Response 503**
```json
{
  "detail": "Model not available: <reason>"
}
```

**Response 422 (Validation error)**
Standard FastAPI validation error for bad payloads.

---

## OpenAPI / Swagger
When server is running: `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/openapi.json`.

## Examples

**Single row**
```bash
curl -s -X POST "http://0.0.0.0:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"records":[{"magnitude":7.2,"cdi":6,"mmi":6,"sig":1200,"nst":20,"dmin":1.2,"gap":60.0,"depth":10.0,"latitude":35.5,"longitude":140.1,"Year":2010,"Month":8}]}'
```

**Multiple rows**
```bash
curl -s -X POST "http://0.0.0.0:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"records":[
    {"magnitude":7.2,"cdi":6,"mmi":6,"sig":1200,"nst":20,"dmin":1.2,"gap":60.0,"depth":10.0,"latitude":35.5,"longitude":140.1,"Year":2010,"Month":8},
    {"magnitude":8.1,"cdi":7,"mmi":8,"sig":1800,"nst":42,"dmin":0.9,"gap":55.0,"depth":12.0,"latitude":38.3,"longitude":142.4,"Year":2016,"Month":6}
  ]}'
```
