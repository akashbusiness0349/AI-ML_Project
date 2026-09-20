from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.baseline import (
    recency_risk_score,
)
from src.evaluation import (
    choose_operating_threshold,
    evaluate_holdout,
    plot_pr_curve,
    save_evaluation,
)
from src.features import (
    get_feature_columns,
)
from src.model import (
    load_model,
)


ROOT = Path(__file__).resolve().parent

MODEL_PATH = (
    ROOT
    / "models"
    / "churn_model.joblib"
)

FEATURE_PATH = (
    ROOT
    / "logs"
    / "feature_table.csv"
)

EVALUATION_PATH = (
    ROOT
    / "logs"
    / "evaluation.json"
)

PR_CURVE_PATH = (
    ROOT
    / "logs"
    / "precision_recall_curve.png"
)

THRESHOLD_PATH = (
    ROOT
    / "logs"
    / "operating_threshold.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Task 08 model."
    )

    parser.add_argument(
        "--source-type",
        default="synthetic_demo",
        choices=[
            "synthetic_demo",
            "production",
        ],
    )

    return parser.parse_args()


def chronological_split(
    dataframe: pd.DataFrame,
):
    dataframe = dataframe.sort_values(
        "prediction_time"
    ).reset_index(
        drop=True
    )

    n = len(dataframe)

    train_end = int(
        n * 0.60
    )

    validation_end = int(
        n * 0.80
    )

    validation = dataframe.iloc[
        train_end:validation_end
    ].copy()

    holdout = dataframe.iloc[
        validation_end:
    ].copy()

    if validation.empty:
        raise ValueError(
            "Validation split is empty."
        )

    if holdout.empty:
        raise ValueError(
            "Holdout split is empty."
        )

    return (
        validation,
        holdout,
    )


def main() -> None:
    args = parse_args()

    print("=" * 72)
    print("PHASE 3 / TASK 08 — HELD-OUT EVALUATION")
    print("=" * 72)

    print(
        f"Data source           : {args.source_type}"
    )

    artifact = load_model(
        MODEL_PATH
    )

    feature_table = pd.read_csv(
        FEATURE_PATH,
        parse_dates=[
            "prediction_time",
            "future_horizon_end",
        ],
    )

    feature_columns = get_feature_columns()

    missing = (
        set(feature_columns)
        - set(feature_table.columns)
    )

    if missing:
        raise ValueError(
            "Feature table is missing: "
            + ", ".join(
                sorted(missing)
            )
        )

    (
        validation,
        holdout,
    ) = chronological_split(
        feature_table
    )

    model = artifact[
        "model"
    ]

    validation_probabilities = (
        model.predict_proba(
            validation[
                feature_columns
            ]
        )[:, 1]
    )

    threshold = choose_operating_threshold(
        validation[
            "churn_label"
        ].astype(int),
        validation_probabilities,
    )

    holdout_probabilities = (
        model.predict_proba(
            holdout[
                feature_columns
            ]
        )[:, 1]
    )

    baseline_scores = recency_risk_score(
        holdout
    )

    evaluation = evaluate_holdout(
        holdout=holdout,
        model_probabilities=holdout_probabilities,
        baseline_scores=baseline_scores,
        threshold=threshold,
    )

    evaluation[
        "evaluation_protocol"
    ] = {
        "threshold_selected_on": "validation_only",
        "final_metrics_on": "held_out_test_only",
        "data_split": "chronological_60_20_20",
        "baseline": "non_ml_recency",
        "target_leakage_policy": (
            "Future activity is used only for label "
            "construction and never as a prediction feature."
        ),
    }

    evaluation[
        "model_version"
    ] = artifact[
        "model_version"
    ]

    evaluation[
        "data_source_type"
    ] = args.source_type

    evaluation[
        "validation_rows"
    ] = len(validation)

    evaluation[
        "holdout_rows"
    ] = len(holdout)

    evaluation[
        "production_evidence_status"
    ] = (
        "NOT_PRODUCTION_EVIDENCE"
        if args.source_type
        == "synthetic_demo"
        else "PRODUCTION_DATA"
    )

    save_evaluation(
        evaluation,
        EVALUATION_PATH,
    )

    plot_pr_curve(
        y_true=holdout[
            "churn_label"
        ].astype(int),
        model_probabilities=holdout_probabilities,
        baseline_scores=baseline_scores,
        output_path=PR_CURVE_PATH,
    )

    threshold_payload = {
        "selected_on": "validation",
        "threshold": threshold,
        "selection_method": "maximum_validation_F1",
        "data_source_type": args.source_type,
    }

    with THRESHOLD_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            threshold_payload,
            handle,
            indent=2,
        )

    model_metrics = evaluation[
        "model"
    ]

    baseline_metrics = evaluation[
        "baseline"
    ]

    print()
    print(
        f"Operating threshold    : "
        f"{threshold:.6f}"
    )

    print()
    print(
        "===== HELD-OUT ML MODEL ====="
    )

    print(
        f"Precision              : "
        f"{model_metrics['precision']:.4f}"
    )

    print(
        f"Recall                 : "
        f"{model_metrics['recall']:.4f}"
    )

    print(
        f"Average Precision      : "
        f"{model_metrics['average_precision']:.4f}"
    )

    print()
    print(
        "===== NON-ML BASELINE ====="
    )

    print(
        f"Precision              : "
        f"{baseline_metrics['precision']:.4f}"
    )

    print(
        f"Recall                 : "
        f"{baseline_metrics['recall']:.4f}"
    )

    print(
        f"Average Precision      : "
        f"{baseline_metrics['average_precision']:.4f}"
    )

    print()
    print(
        "===== TOP-10% LIFT ====="
    )

    print(
        f"ML lift                : "
        f"{evaluation['model_lift']['lift']:.4f}"
    )

    print(
        f"Baseline lift          : "
        f"{evaluation['baseline_lift']['lift']:.4f}"
    )

    print()
    print(
        f"Evaluation JSON        : "
        f"{EVALUATION_PATH}"
    )

    print(
        f"PR curve               : "
        f"{PR_CURVE_PATH}"
    )

    print(
        f"Threshold evidence     : "
        f"{THRESHOLD_PATH}"
    )

    print()
    print(
        "HELD-OUT EVALUATION: PASS"
    )


if __name__ == "__main__":
    main()