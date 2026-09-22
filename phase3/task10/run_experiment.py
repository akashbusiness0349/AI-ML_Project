import json
from pathlib import Path

import pandas as pd

from src.data import (
    load_feature_table,
    chronological_split,
)
from src.model import save_model
from src.experiment import run_experiment


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "task08_feature_table.csv"
PREREG = ROOT / "logs" / "preregistration.json"


def main():
    if not PREREG.exists():
        raise RuntimeError(
            "Preregistration is missing. Run run_preregistration.py first."
        )

    with open(PREREG, encoding="utf-8") as f:
        prereg = json.load(f)

    df = load_feature_table(DATA)

    train, validation, holdout = chronological_split(
        df
    )

    model_path = ROOT / "models" / "task10_model.joblib"

    result = run_experiment(
        train,
        validation,
        holdout,
        model_path,
    )

    save_model(
        result["model"],
        model_path,
    )

    replay = result["replay"]

    replay.to_csv(
        ROOT / "logs" / "experiment_replay.csv",
        index=False,
    )

    output = {
        "experiment": "Phase 3 Task 10",
        "preregistration_version": prereg["version"],
        "data_source_type": "synthetic_demo",
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "split": {
            "train_rows": len(train),
            "validation_rows": len(validation),
            "holdout_rows": len(holdout),
        },
        "model": {
            "threshold": result["threshold"],
            "metrics": result["model_metrics"],
            "top_k_lift": result["model_lift"],
        },
        "baseline": {
            "metrics": result["baseline_metrics"],
            "top_k_lift": result["baseline_lift"],
        },
        "offline_ab_replay": {
            **result["ab_effect"],
            "interpretation": (
                "This is a historical offline replay comparison. "
                "The observed difference is not a causal online treatment effect."
            ),
        },
        "online_validation": {
            "status": "NOT_ESTABLISHED",
            "reason": (
                "No verified production/live A/B traffic was available."
            ),
        },
    }

    with open(
        ROOT / "logs" / "experiment_result.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()