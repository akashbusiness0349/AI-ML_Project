from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
)


def average_precision(
    labels: pd.Series | np.ndarray,
    scores: pd.Series | np.ndarray,
) -> float:
    labels_array = np.asarray(labels).astype(int)
    scores_array = np.asarray(scores).astype(float)

    if len(np.unique(labels_array)) < 2:
        return 0.0

    return float(
        average_precision_score(
            labels_array,
            scores_array,
        )
    )


def classification_metrics(
    labels: pd.Series | np.ndarray,
    scores: pd.Series | np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    labels_array = np.asarray(labels).astype(int)
    scores_array = np.asarray(scores).astype(float)
    predictions = (scores_array >= threshold).astype(int)

    return {
        "average_precision": average_precision(
            labels_array,
            scores_array,
        ),
        "precision": float(
            precision_score(
                labels_array,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                labels_array,
                predictions,
                zero_division=0,
            )
        ),
        "threshold": float(threshold),
    }


def group_metrics(
    frame: pd.DataFrame,
    score_column: str = "prediction_score",
    label_column: str = "outcome_label",
    threshold: float = 0.5,
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}

    for group, group_frame in frame.groupby("experiment_group"):
        if group_frame.empty:
            continue

        result[group] = classification_metrics(
            group_frame[label_column],
            group_frame[score_column],
            threshold=threshold,
        )

        result[group]["rows"] = float(len(group_frame))
        result[group]["unique_entities"] = float(
            group_frame["entity_id"].nunique()
        )

    return result


def top_fraction_lift(
    labels: pd.Series | np.ndarray,
    scores: pd.Series | np.ndarray,
    fraction: float = 0.10,
) -> float:
    labels_array = np.asarray(labels).astype(int)
    scores_array = np.asarray(scores).astype(float)

    if len(labels_array) == 0:
        return 0.0

    base_rate = labels_array.mean()

    if base_rate <= 0:
        return 0.0

    cutoff = max(1, int(np.ceil(len(scores_array) * fraction)))

    order = np.argsort(-scores_array)
    selected = labels_array[order[:cutoff]]

    selected_rate = selected.mean()

    return float(selected_rate / base_rate)


def daily_group_metrics(
    frame: pd.DataFrame,
    score_column: str = "prediction_score",
    label_column: str = "outcome_label",
) -> list[dict[str, Any]]:
    work = frame.copy()

    work["metric_date"] = pd.to_datetime(
        work["event_timestamp"],
        utc=True,
    ).dt.date.astype(str)

    rows: list[dict[str, Any]] = []

    for (metric_date, group), group_frame in work.groupby(
        ["metric_date", "experiment_group"]
    ):
        rows.append(
            {
                "date": metric_date,
                "group": group,
                "rows": int(len(group_frame)),
                "unique_entities": int(
                    group_frame["entity_id"].nunique()
                ),
                "average_precision": average_precision(
                    group_frame[label_column],
                    group_frame[score_column],
                ),
                "mean_score": float(
                    group_frame[score_column].mean()
                ),
                "mean_hiring_relevance": float(
                    group_frame["hiring_relevance"].mean()
                ),
            }
        )

    return rows