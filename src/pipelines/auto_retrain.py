from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

SUMMARY_PATH = Path("artifacts/metrics/evidently_summary.json")


def _extract_drift_share(summary: Dict[str, Any]) -> Optional[float]:
    """
    Evidently 0.4.x report.as_dict() structure can vary between presets.
    We defensively search for 'share_of_drifted_columns'.
    """
    # Common location in presets
    for metric in summary.get("metrics", []):
        res = metric.get("result", {})
        if isinstance(res, dict) and "share_of_drifted_columns" in res:
            try:
                return float(res["share_of_drifted_columns"])
            except Exception:
                pass
        # Sometimes nested under 'data_drift'
        dd = res.get("data_drift") if isinstance(res, dict) else None
        if isinstance(dd, dict) and "share_of_drifted_columns" in dd:
            try:
                return float(dd["share_of_drifted_columns"])
            except Exception:
                pass
    return None


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise SystemExit(
            f"No drift summary found at {SUMMARY_PATH}. Run `make drift-report` first."
        )

    with open(SUMMARY_PATH, "r") as f:
        summary = json.load(f)

    share = _extract_drift_share(summary)
    if share is None:
        print("Could not find 'share_of_drifted_columns' in Evidently summary; skipping retrain.")
        return

    # Threshold: env var or default 0.30
    threshold_str = os.getenv("DRIFT_THRESHOLD", "0.30")
    try:
        threshold = float(threshold_str)
    except ValueError:
        threshold = 0.30

    print(f"Drift share: {share:.3f} (threshold {threshold:.2f})")

    if share > threshold:
        print("Threshold exceeded → retraining...")
        # Call our training module (same as `make train`)
        subprocess.check_call(["python", "-m", "src.training.train"])
        print("Retraining complete.")
    else:
        print("No retrain needed.")


if __name__ == "__main__":
    main()
