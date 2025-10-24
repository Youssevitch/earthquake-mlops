from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml


def _is_dtype(s: pd.Series, expected: str) -> bool:
    if expected == "int":
        return bool(pd.api.types.is_integer_dtype(s))
    if expected == "float":
        return bool(pd.api.types.is_float_dtype(s) or pd.api.types.is_integer_dtype(s))
    if expected == "str":
        return bool(pd.api.types.is_string_dtype(s))
    return False


def validate_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    checks = []
    errors = 0
    warnings = 0

    cols: Dict[str, Dict[str, Any]] = schema["columns"]

    # 1) required columns present (ERROR)
    for col, rules in cols.items():
        if rules.get("required", False) and col not in df.columns:
            errors += 1
            checks.append(
                {
                    "column": col,
                    "check": "exists",
                    "severity": "error",
                    "passed": False,
                    "msg": "Missing required column",
                }
            )

    # Proceed with the columns that do exist
    for col, rules in cols.items():
        if col not in df.columns:
            continue
        s = df[col]

        # 2) dtype check (WARN unless target values invalid)
        dtype_ok = _is_dtype(s, rules["dtype"])
        if not dtype_ok:
            warnings += 1
        checks.append(
            {
                "column": col,
                "check": "dtype",
                "severity": "warn",
                "passed": bool(dtype_ok),
                "expected": rules["dtype"],
            }
        )

        # 3) allowed values vs ranges
        if "values" in rules:
            allowed = set(rules["values"])
            val_ok = bool(s.dropna().isin(allowed).all())
            sev = "error" if col == schema.get("target") else "warn"
            if not val_ok:
                if sev == "error":
                    errors += 1
                else:
                    warnings += 1
            checks.append(
                {
                    "column": col,
                    "check": "values",
                    "severity": sev,
                    "passed": bool(val_ok),
                    "allowed": sorted(list(allowed)),
                }
            )
        else:
            mn, mx = rules.get("min", None), rules.get("max", None)
            rng_ok = True
            if mn is not None:
                rng_ok = bool(rng_ok and (s.dropna() >= mn).all())
            if mx is not None:
                rng_ok = bool(rng_ok and (s.dropna() <= mx).all())
            if not rng_ok:
                warnings += 1
            checks.append(
                {
                    "column": col,
                    "check": "range",
                    "severity": "warn",
                    "passed": bool(rng_ok),
                    "min": mn,
                    "max": mx,
                }
            )

    # 4) missingness summary (store as native ints)
    na_counts = df.isna().sum().astype(int).to_dict()
    na_counts = {str(k): int(v) for k, v in na_counts.items()}

    # 5) class balance (store as native ints)
    target = schema["target"]
    class_counts = {}
    if target in df.columns:
        class_counts = df[target].value_counts(dropna=False).astype(int).to_dict()
        # keys to strings for JSON
        class_counts = {
            str(k) if not pd.isna(k) else "NaN": int(v) for k, v in class_counts.items()
        }

    result: Dict[str, Any] = {
        "errors": int(errors),
        "warnings": int(warnings),
        "checks": checks,
        "missing": na_counts,
        "class_counts": class_counts,
        "passed": bool(errors == 0),  # only errors block
    }
    return result


def run_validation(
    data_path: Path = Path("data/raw/earthquake_data_tsunami.csv"),
    schema_path: Path = Path("configs/schema.yaml"),
    out_report: Path = Path("artifacts/metrics/validation_report.json"),
) -> Dict[str, Any]:
    out_report.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path)
    with open(schema_path, "r") as f:
        schema = yaml.safe_load(f)

    result = validate_dataframe(df, schema)

    with open(out_report, "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    res = run_validation()
    # exit 1 only on errors (not warnings)
    raise SystemExit(0 if res["errors"] == 0 else 1)
