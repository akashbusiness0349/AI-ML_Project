from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
)


def choose_operating_threshold(
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> float:
    """
    Select threshold on validation data only.

    Objective:
        maximize F1.

    This threshold must NOT be tuned on the held-out test set.
    """

    precision, recall, thresholds = precision_recall_curve(
        y_true,
        probabilities,
    )

    if len(thresholds) == 0:
        return 0.5

    f1 = (
        2 * precision[:-1] * recall[:-1]
        / np.maximum(
            precision[:-1] + recall[:-1],
            1e-12,
        )
    )

    best_index = int(np.nanargmax(f1))

    return float(
        np.clip(
            thresholds[best_index],
            0.01,
            0.99,
        )
    )


def calculate_metrics(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> dict:
    predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0,
    )

    average_precision = average_precision_score(
        y_true,
        probabilities,
    )

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    report = classification_report(
        y_true,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    return {
        "threshold": float(threshold),
        "precision": float(precision),
        "recall": float(recall),
        "average_precision": float(average_precision),
        "positive_rate": float(predictions.mean()),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }


def calculate_lift(
    y_true: pd.Series,
    scores: np.ndarray,
    top_fraction: float = 0.10,
) -> dict:
    """
    Lift over random/non-ML population selection.

    Top-K lift:
        precision among highest-risk top-K
        divided by overall positive rate.
    """

    y = np.asarray(y_true).astype(int)
    scores = np.asarray(scores).astype(float)

    if len(y) == 0:
        return {
            "top_fraction": top_fraction,
            "top_k": 0,
            "population_positive_rate": 0.0,
            "top_k_precision": 0.0,
            "lift": 0.0,
        }

    population_rate = float(y.mean())

    top_k = max(
        1,
        int(np.ceil(len(y) * top_fraction)),
    )

    order = np.argsort(
        -scores,
        kind="mergesort",
    )

    top_indices = order[:top_k]

    top_precision = float(
        y[top_indices].mean()
    )

    lift = (
        top_precision / population_rate
        if population_rate > 0
        else 0.0
    )

    return {
        "top_fraction": float(top_fraction),
        "top_k": int(top_k),
        "population_positive_rate": population_rate,
        "top_k_precision": top_precision,
        "lift": float(lift),
    }


def plot_pr_curve(
    y_true: pd.Series,
    model_probabilities: np.ndarray,
    baseline_scores: np.ndarray,
    output_path: str | Path,
) -> None:
    precision_model, recall_model, _ = precision_recall_curve(
        y_true,
        model_probabilities,
    )

    precision_baseline, recall_baseline, _ = precision_recall_curve(
        y_true,
        baseline_scores,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))

    plt.plot(
        recall_model,
        precision_model,
        label="ML model",
    )

    plt.plot(
        recall_baseline,
        precision_baseline,
        label="Non-ML recency baseline",
    )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Task 08 Precision-Recall Curve")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=160,
    )

    plt.close()


def evaluate_holdout(
    holdout: pd.DataFrame,
    model_probabilities: np.ndarray,
    baseline_scores: np.ndarray,
    threshold: float,
) -> dict:
    y_true = holdout["churn_label"].astype(int)

    model_metrics = calculate_metrics(
        y_true,
        model_probabilities,
        threshold,
    )

    baseline_threshold = 0.5

    baseline_metrics = calculate_metrics(
        y_true,
        baseline_scores,
        baseline_threshold,
    )

    model_lift = calculate_lift(
        y_true,
        model_probabilities,
    )

    baseline_lift = calculate_lift(
        y_true,
        baseline_scores,
    )

    return {
        "model": model_metrics,
        "baseline": baseline_metrics,
        "model_lift": model_lift,
        "baseline_lift": baseline_lift,
        "offline_online_gap_note": (
            "Offline predictive metrics do not establish online intervention "
            "effect. Online effect requires a controlled growth experiment."
        ),
    }


def save_evaluation(
    evaluation: dict,
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            evaluation,
            handle,
            indent=2,
            default=float,
        )