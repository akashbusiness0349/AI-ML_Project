from __future__ import annotations

import pandas as pd

from .baseline import recency_risk_score


def fallback_predictions(
    dataframe: pd.DataFrame,
    lookback_days: int = 14,
) -> pd.DataFrame:
    """
    Safe degradation path.

    If ML model is unavailable, Growth still receives a deterministic
    recency-based risk signal.

    This is explicitly marked as fallback output.
    """

    result = dataframe.copy()

    result["churn_probability"] = recency_risk_score(
        result,
        lookback_days=lookback_days,
    )

    result["prediction_source"] = "NON_ML_FALLBACK"

    result["model_prediction"] = (
        result["churn_probability"] >= 0.5
    ).astype(int)

    return result


def model_unavailable_response(
    reason: str,
) -> dict:
    return {
        "status": "MODEL_UNAVAILABLE",
        "prediction_source": "NON_ML_FALLBACK",
        "message": (
            "The ML model is unavailable. "
            "The deterministic recency fallback should be used."
        ),
        "reason": reason,
    }