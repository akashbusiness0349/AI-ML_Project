from __future__ import annotations

import json
from pathlib import Path

from src.data import (
    load_candidates,
    load_jobs,
    load_train,
    save_json,
)
from src.ranker import (
    save_model,
    train_pairwise_model,
)


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = (
    BASE_DIR
    / "models"
    / "task11_ltr_model.joblib"
)


def main() -> None:
    candidates = load_candidates()
    jobs = load_jobs()
    interactions = load_train()

    candidate_map = {
        row["candidate_id"]: row
        for row in candidates
    }

    job_map = {
        row["job_id"]: row
        for row in jobs
    }

    result = train_pairwise_model(
        interactions,
        candidate_map,
        job_map,
    )

    model = result["model"]

    save_model(
        model,
        MODEL_PATH,
    )

    output = {
        "task": "Phase 3 Task 11",
        "status": "PASS",
        "objective": (
            "pairwise_learning_to_rank"
        ),
        "training_data": {
            "source": "data/train.json",
            "records": len(interactions),
        },
        "model_type": (
            "LogisticRegression_on_pairwise_feature_differences"
        ),
        "position_bias_correction": True,
        "feature_names": model.feature_names,
        "training_examples": result[
            "training_examples"
        ],
        "training_metadata": result[
            "training_metadata"
        ],
        "model_path": str(
            MODEL_PATH
        ),
    }

    save_json(
        output,
        "logs/training_result.json",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()