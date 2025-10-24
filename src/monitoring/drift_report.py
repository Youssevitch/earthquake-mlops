from __future__ import annotations

from pathlib import Path

import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.report import Report

REF_PATH = Path("data/processed/train.csv")
CURR_PATH = Path("data/processed/test.csv")
OUT_HTML = Path("artifacts/plots/evidently_report.html")
OUT_JSON = Path("artifacts/metrics/evidently_summary.json")


def main():
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    ref = pd.read_csv(REF_PATH)
    cur = pd.read_csv(CURR_PATH)

    # Tell Evidently which column is the target
    mapping = ColumnMapping(target="tsunami")

    report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
    report.run(reference_data=ref, current_data=cur, column_mapping=mapping)

    report.save_html(str(OUT_HTML))

    # Save machine-readable summary
    summary = report.as_dict()
    import json

    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {OUT_HTML} and {OUT_JSON}")


if __name__ == "__main__":
    main()
