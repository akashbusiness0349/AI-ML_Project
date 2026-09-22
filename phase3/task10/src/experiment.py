import hashlib

from .data import FEATURE_COLUMNS
from .baseline import baseline_score
from .model import train_model
from .metrics import (
    classification_metrics,
    proportion_effect,
    top_k_lift,
)


def assign_variant(entity_id: str) -> str:
    digest = hashlib.sha256(
        entity_id.encode("utf-8")
    ).hexdigest()

    value = int(digest[:8], 16)

    return "treatment" if value % 2 else "control"


def choose_threshold(validation_df, model):
    y_true = validation_df["churn_label"].to_numpy()

    scores = model.predict_proba(
        validation_df[FEATURE_COLUMNS]
    )[:, 1]

    unique_scores = sorted(
        set(float(x) for x in scores)
    )

    candidates = {
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
    }

    candidates.update(
        round(x, 4)
        for x in unique_scores
        if 0.05 <= x <= 0.95
    )

    best_threshold = 0.5
    best_f1 = -1.0
    best_precision = -1.0
    best_recall = -1.0

    for threshold in sorted(candidates):
        predictions = (
            scores >= threshold
        ).astype(int)

        tp = int(
            ((predictions == 1) & (y_true == 1)).sum()
        )
        fp = int(
            ((predictions == 1) & (y_true == 0)).sum()
        )
        fn = int(
            ((predictions == 0) & (y_true == 1)).sum()
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp)
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn)
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if (precision + recall)
            else 0.0
        )

        # Primary: F1
        # Tie-break: precision, then recall
        if (
            f1 > best_f1
            or (
                f1 == best_f1
                and precision > best_precision
            )
            or (
                f1 == best_f1
                and precision == best_precision
                and recall > best_recall
            )
        ):
            best_f1 = f1
            best_precision = precision
            best_recall = recall
            best_threshold = threshold

    return float(best_threshold)


def run_experiment(
    train_df,
    validation_df,
    holdout_df,
    model_path,
):
    model = train_model(train_df)

    threshold = choose_threshold(
        validation_df,
        model,
    )

    model_scores = model.predict_proba(
        holdout_df[FEATURE_COLUMNS]
    )[:, 1]

    baseline_scores = baseline_score(
        holdout_df
    )

    model_metrics = classification_metrics(
        holdout_df["churn_label"],
        model_scores,
        threshold,
    )

    baseline_metrics = classification_metrics(
        holdout_df["churn_label"],
        baseline_scores,
        0.5,
    )

    model_lift = top_k_lift(
        holdout_df["churn_label"],
        model_scores,
    )

    baseline_lift = top_k_lift(
        holdout_df["churn_label"],
        baseline_scores,
    )

    replay = holdout_df[
        [
            "entity_id",
            "prediction_time",
            "future_horizon_end",
            "churn_label",
        ]
    ].copy()

    replay["variant"] = replay[
        "entity_id"
    ].map(assign_variant)

    replay["model_score"] = model_scores
    replay["baseline_score"] = baseline_scores

    replay["model_positive"] = (
        replay["model_score"] >= threshold
    ).astype(int)

    replay["baseline_positive"] = (
        replay["baseline_score"] >= 0.5
    ).astype(int)

    control = replay[
        replay["variant"] == "control"
    ]

    treatment = replay[
        replay["variant"] == "treatment"
    ]

    control_successes = int(
        control["churn_label"].sum()
    )

    treatment_successes = int(
        treatment["churn_label"].sum()
    )

    ab = proportion_effect(
        control_successes,
        len(control),
        treatment_successes,
        len(treatment),
    )

    return {
        "model": model,
        "threshold": threshold,
        "model_metrics": model_metrics,
        "baseline_metrics": baseline_metrics,
        "model_lift": model_lift,
        "baseline_lift": baseline_lift,
        "replay": replay,
        "ab_effect": ab,
        "model_path": str(model_path),
    }