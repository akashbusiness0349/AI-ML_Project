from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.data_ingestion import load_logged_data
from src.experiment_assignment import AssignmentConfig, assign_entity
from src.features import build_features
from src.metrics import (
    classification_metrics,
    group_metrics,
    daily_group_metrics,
    top_fraction_lift,
)
from src.model import (
    FEATURES_V1,
    FEATURES_V2,
    train_model,
    predict_probability,
    save_model,
)


TASK_ROOT = Path(__file__).resolve().parent
LOG_DIR = TASK_ROOT / "logs"
MODEL_DIR = TASK_ROOT / "models"


def save_json(payload, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        required=True,
    )

    parser.add_argument(
        "--source-type",
        required=True,
        choices=["synthetic_demo", "production"],
    )

    args = parser.parse_args()

    data_path = Path(args.data)

    print("=" * 70)
    print("TASK 09 — EXPERIMENT + MODEL VARIANTS")
    print("=" * 70)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Logged data not found: {data_path}"
        )

    raw = load_logged_data(data_path)

    if args.source_type == "production":
        print("Source type         : production")
    else:
        print("Source type         : synthetic_demo")
        print("Evidence boundary   : DEMO ONLY — NOT production evidence")

    print(f"Raw rows            : {len(raw)}")
    print(f"Raw entities        : {raw['entity_id'].nunique()}")

    # ------------------------------------------------------------
    # FEATURE ENGINEERING
    # ------------------------------------------------------------

    features = build_features(raw)

    print(f"Feature rows        : {len(features)}")
    print("Feature contract    : PASS")
    print(f"V1 features         : {len(FEATURES_V1)}")
    print(f"V2 features         : {len(FEATURES_V2)}")

    # ------------------------------------------------------------
    # TEMPORAL SPLIT
    # ------------------------------------------------------------

    timestamps = features["event_timestamp"].sort_values()

    split_index = max(
        1,
        min(
            len(features) - 1,
            int(len(features) * 0.70),
        ),
    )

    split_time = timestamps.iloc[split_index]

    train = features[
        features["event_timestamp"] < split_time
    ].copy()

    test = features[
        features["event_timestamp"] >= split_time
    ].copy()

    if train.empty or test.empty:
        raise ValueError("Temporal train/test split produced an empty partition.")

    if train["outcome_label"].nunique() < 2:
        raise ValueError("Training set does not contain both outcome classes.")

    if test["outcome_label"].nunique() < 2:
        raise ValueError("Held-out set does not contain both outcome classes.")

    print(f"Training rows       : {len(train)}")
    print(f"Held-out rows       : {len(test)}")
    print(f"Split timestamp     : {split_time}")

    # ------------------------------------------------------------
    # TRAIN TWO MODEL VARIANTS
    # ------------------------------------------------------------

    model_v1 = train_model(
        train,
        "model-v1",
    )

    model_v2 = train_model(
        train,
        "model-v2",
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    save_model(
        model_v1,
        MODEL_DIR / "model-v1.joblib",
    )

    save_model(
        model_v2,
        MODEL_DIR / "model-v2.joblib",
    )

    # ------------------------------------------------------------
    # PREDICT HELD-OUT DATA
    # ------------------------------------------------------------

    test = test.copy()

    test["prediction_v1"] = predict_probability(
        model_v1,
        test,
        "model-v1",
    )

    test["prediction_v2"] = predict_probability(
        model_v2,
        test,
        "model-v2",
    )

    config = AssignmentConfig()

    assignments = [
        assign_entity(
            str(entity_id),
            config,
        )
        for entity_id in test["entity_id"]
    ]

    test["experiment_bucket"] = [
        item["bucket"] for item in assignments
    ]

    test["experiment_group"] = [
        item["group"] for item in assignments
    ]

    test["experiment_variant"] = [
        item["variant"] for item in assignments
    ]

    # ------------------------------------------------------------
    # SERVED SCORE
    # ------------------------------------------------------------

    def choose_score(row):
        if row["experiment_variant"] == "model-v1":
            return float(row["prediction_v1"])

        if row["experiment_variant"] == "model-v2":
            return float(row["prediction_v2"])

        # Permanent holdout intentionally receives a non-ML baseline.
        relevance = float(row["hiring_relevance"])
        engagement = float(row["engagement_score"])

        return float(
            max(
                0.0,
                min(
                    1.0,
                    0.5 * relevance + 0.5 * engagement,
                ),
            )
        )

    test["prediction_score"] = test.apply(
        choose_score,
        axis=1,
    )

    test["source_type"] = args.source_type

    # ------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------

    v1_metrics = classification_metrics(
        test["outcome_label"],
        test["prediction_v1"],
    )

    v2_metrics = classification_metrics(
        test["outcome_label"],
        test["prediction_v2"],
    )

    served_metrics = group_metrics(
        test,
        score_column="prediction_score",
        label_column="outcome_label",
    )

    overall_lift = top_fraction_lift(
        test["outcome_label"],
        test["prediction_score"],
        fraction=0.10,
    )

    daily_metrics = daily_group_metrics(
        test,
        score_column="prediction_score",
        label_column="outcome_label",
    )

    # ------------------------------------------------------------
    # SAVE PREDICTIONS
    # ------------------------------------------------------------

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    prediction_path = LOG_DIR / "experiment_predictions.csv"

    test.to_csv(
        prediction_path,
        index=False,
    )

    # ------------------------------------------------------------
    # EXPERIMENT EVIDENCE
    # ------------------------------------------------------------

    experiment_result = {
        "task": "phase3_task09",
        "source_type": args.source_type,
        "evidence_boundary": (
            "Synthetic demo measurements are not production evidence."
            if args.source_type == "synthetic_demo"
            else "Production source declared by caller."
        ),
        "experiment_id": config.experiment_id,
        "training_rows": int(len(train)),
        "heldout_rows": int(len(test)),
        "training_entities": int(train["entity_id"].nunique()),
        "heldout_entities": int(test["entity_id"].nunique()),
        "split_timestamp": str(split_time),
        "models": {
            "model-v1": {
                "features": FEATURES_V1,
                "metrics": v1_metrics,
            },
            "model-v2": {
                "features": FEATURES_V2,
                "metrics": v2_metrics,
            },
        },
        "served_group_metrics": served_metrics,
        "top_10_percent_lift": overall_lift,
        "daily_group_metrics": daily_metrics,
        "expected_online_effect": {
            "target_relative_uplift": 0.05,
            "measurement_window_days": 7,
            "status": "PLANNED_NOT_ESTABLISHED_BY_SYNTHETIC_DEMO",
        },
        "prediction_artifact": str(prediction_path),
        "model_artifacts": [
            str(MODEL_DIR / "model-v1.joblib"),
            str(MODEL_DIR / "model-v2.joblib"),
        ],
    }

    save_json(
        experiment_result,
        LOG_DIR / "experiment_result.json",
    )

    # Also save a compact experiment log.
    log_row = pd.DataFrame(
        [
            {
                "experiment_id": config.experiment_id,
                "source_type": args.source_type,
                "model_v1_average_precision":
                    v1_metrics["average_precision"],
                "model_v2_average_precision":
                    v2_metrics["average_precision"],
                "top_10_percent_lift":
                    overall_lift,
                "training_rows": len(train),
                "heldout_rows": len(test),
                "expected_online_uplift": 0.05,
                "expected_window_days": 7,
            }
        ]
    )

    log_row.to_csv(
        LOG_DIR / "experiment_log.csv",
        index=False,
    )

    print()
    print("Model-v1 AP        :", round(v1_metrics["average_precision"], 6))
    print("Model-v2 AP        :", round(v2_metrics["average_precision"], 6))
    print("Top-10% lift       :", round(overall_lift, 6))
    print("Prediction rows    :", len(test))
    print("Prediction artifact:", prediction_path)
    print("Experiment evidence:", LOG_DIR / "experiment_result.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
