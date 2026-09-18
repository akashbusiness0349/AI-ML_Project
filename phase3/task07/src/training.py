


from __future__ import annotations

import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODELS = ROOT / "models"
LOGS = ROOT / "logs"

MODEL_VERSION = "cold-start-trained-v4.0.0"


def sigmoid(value: float) -> float:
    value = max(-50.0, min(50.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def feature_vector(row: dict) -> list[float]:
    return [
        float(row.get("skill_overlap", 0)),
        float(row.get("location_match", 0)),
        float(row.get("experience_match", 0)),
        float(row.get("job_popularity", 0)),
    ]


def train_logistic_regression(
    rows: list[dict],
    epochs: int = 2000,
    learning_rate: float = 0.01,
) -> tuple[list[float], float]:
    if not rows:
        raise ValueError("Training dataset is empty.")

    weights = [0.0] * 4
    bias = 0.0

    for _ in range(epochs):
        grad_w = [0.0] * 4
        grad_b = 0.0

        for row in rows:
            x = feature_vector(row)
            y = float(row["label"])

            z = sum(w * value for w, value in zip(weights, x)) + bias
            prediction = sigmoid(z)

            error = prediction - y

            for index in range(4):
                grad_w[index] += error * x[index]

            grad_b += error

        scale = 1.0 / len(rows)

        for index in range(4):
            weights[index] -= learning_rate * grad_w[index] * scale

        bias -= learning_rate * grad_b * scale

    return weights, bias


def main() -> None:
    MODELS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    training_path = DATA / "training_data.json"

    with training_path.open("r", encoding="utf-8") as f:
        dataset = json.load(f)

    rows = dataset["records"]

    if not rows:
        raise ValueError("No training records found.")

    candidate_ids = sorted(
        {
            row["candidate_id"]
            for row in rows
        }
    )

    positive_examples = sum(
        int(row["label"]) == 1
        for row in rows
    )

    negative_examples = sum(
        int(row["label"]) == 0
        for row in rows
    )

    weights, bias = train_logistic_regression(rows)

    model = {
        "model_version": MODEL_VERSION,
        "model_type": "logistic_regression",
        "task": "cold_start_job_ranking",
        "feature_names": [
            "skill_overlap",
            "location_match",
            "experience_match",
            "job_popularity",
        ],
        "weights": weights,
        "bias": bias,
        "training": {
            "dataset": "data/training_data.json",
            "dataset_type": dataset.get(
                "dataset_type",
                "local_training",
            ),
            "source": dataset.get(
                "source",
                "candidate_job_catalog",
            ),
            "candidate_count": len(candidate_ids),
            "training_examples": len(rows),
            "positive_examples": positive_examples,
            "negative_examples": negative_examples,
            "production_data": False,
            "heldout_data_excluded": True,
        },
    }

    versioned_path = MODELS / f"{MODEL_VERSION}.json"
    active_path = MODELS / "active_model.json"
    registry_path = MODELS / "model_registry.json"

    with versioned_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    shutil.copy2(versioned_path, active_path)

    registry = {
        "active_model": MODEL_VERSION,
        "models": [
            {
                "model_version": MODEL_VERSION,
                "path": str(versioned_path.relative_to(ROOT)),
                "status": "active",
                "production_data": False,
            }
        ],
    }

    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    result = {
        "status": "TRAINING_COMPLETE",
        "model_path": str(
            versioned_path.relative_to(ROOT)
        ),
        "model_version": MODEL_VERSION,
        "training_examples": len(rows),
        "positive_examples": positive_examples,
        "negative_examples": negative_examples,
        "training_candidate_count": len(candidate_ids),
        "production_data": False,
        "heldout_data_excluded": True,
    }

    with (LOGS / "training_result_v4.json").open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(result, f, indent=2)

    print("STATUS:", result["status"])
    print("MODEL:", result["model_version"])
    print("TRAINING EXAMPLES:", result["training_examples"])
    print("POSITIVE EXAMPLES:", result["positive_examples"])
    print("NEGATIVE EXAMPLES:", result["negative_examples"])
    print("TRAINING CANDIDATES:", result["training_candidate_count"])
    print("HELDOUT DATA EXCLUDED:", result["heldout_data_excluded"])
    print("PRODUCTION DATA:", result["production_data"])


if __name__ == "__main__":
    main()
