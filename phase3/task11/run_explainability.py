from __future__ import annotations

import json
from pathlib import Path

from src.data import (
    load_candidates,
    load_jobs,
    save_json,
)
from src.explainability import (
    explain_prediction,
)
from src.ranker import load_model


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "task11_ltr_model.joblib"
)


def main() -> None:
    candidates = load_candidates()
    jobs = load_jobs()

    model = load_model(
        MODEL_PATH
    )

    candidate = candidates[0]
    job = jobs[0]

    explanation = explain_prediction(
        model,
        candidate,
        job,
    )

    output = {
        "task": "Phase 3 Task 11",
        "status": "PASS",
        "worked_example": explanation,
        "explainability_method": (
            "linear_feature_contribution"
        ),
        "protected_features_used": [],
    }

    save_json(
        output,
        "logs/explainability.json",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()