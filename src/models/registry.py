from __future__ import annotations

import argparse
import os

from mlflow.tracking import MlflowClient


def promote(model_name: str, version: str, stage: str) -> None:
    client = MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
        archive_existing_versions=True,
    )
    print(f"Promoted {model_name} v{version} -> {stage}")


def rollback_to(model_name: str, version: str, stage: str = "Production") -> None:
    promote(model_name, version, stage)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_prom = sub.add_parser("promote")
    p_prom.add_argument("--name", required=True)
    p_prom.add_argument("--version", required=True)
    p_prom.add_argument(
        "--stage", default="Production", choices=["Staging", "Production", "Archived"]
    )

    p_rb = sub.add_parser("rollback")
    p_rb.add_argument("--name", required=True)
    p_rb.add_argument("--version", required=True)
    p_rb.add_argument("--stage", default="Production")

    args = p.parse_args()

    if args.cmd == "promote":
        promote(args.name, args.version, args.stage)
    elif args.cmd == "rollback":
        rollback_to(args.name, args.version, args.stage)


if __name__ == "__main__":
    main()
