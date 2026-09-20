from __future__ import annotations

import numpy as np
import pandas as pd


BASELINE_NAME = "recency_non_ml_baseline"


def recency_risk_score(
    dataframe: pd.DataFrame,
    lookback_days: int = 14,
) -> np.ndarray:
    """
    Non-ML baseline.

    Risk rises linearly as inactivity approaches/exceeds the
    configured lookback period.

    score = days_since_last_activity / lookback_days
    clipped to [0, 1].
    """

    if "days_since_last_activity" not in dataframe.columns:
        raise ValueError(
            "days_since_last_activity is required for the baseline."
        )

    scores = (
        dataframe["days_since_last_activity"].astype(float)
        / float(lookback_days)
    )

    return np.clip(scores.to_numpy(), 0.0, 1.0)


def baseline_predictions(
    dataframe: pd.DataFrame,
    threshold: float = 0.5,
    lookback_days: int = 14,
) -> np.ndarray:
    scores = recency_risk_score(
        dataframe,
        lookback_days=lookback_days,
    )

    return (scores >= threshold).astype(int)


def baseline_reason(row: pd.Series) -> str:
    days = float(row["days_since_last_activity"])

    if days >= 14:
        return (
            f"No activity observed for approximately {days:.1f} days."
        )

    return (
        f"Last activity was approximately {days:.1f} days ago."
    )