from __future__ import annotations

import pandas as pd


def assign_risk_segment(
    probability: float,
) -> str:
    if probability >= 0.70:
        return "HIGH"

    if probability >= 0.40:
        return "MEDIUM"

    return "LOW"


def build_at_risk_list(
    predictions: pd.DataFrame,
    explanations: list[dict],
) -> pd.DataFrame:
    """
    Build prioritized actionable list for Growth.

    Only HIGH and MEDIUM risk users are included.
    """

    if len(predictions) != len(explanations):
        raise ValueError(
            "Prediction and explanation counts do not match."
        )

    rows: list[dict] = []

    for row, explanation in zip(
        predictions.itertuples(index=False),
        explanations,
    ):
        probability = float(
            row.churn_probability
        )

        segment = assign_risk_segment(
            probability
        )

        if segment == "LOW":
            continue

        rows.append(
            {
                "entity_id": row.entity_id,
                "entity_type": row.entity_type,
                "prediction_time": row.prediction_time.isoformat(),
                "risk_probability": round(
                    probability,
                    6,
                ),
                "risk_segment": segment,
                "priority_rank": 0,
                "reason": explanation[
                    "plain_english_reason"
                ],
                "recommended_action": explanation[
                    "recommended_action"
                ],
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(
            columns=[
                "entity_id",
                "entity_type",
                "prediction_time",
                "risk_probability",
                "risk_segment",
                "priority_rank",
                "reason",
                "recommended_action",
            ]
        )

    result = result.sort_values(
        "risk_probability",
        ascending=False,
    ).reset_index(drop=True)

    result["priority_rank"] = (
        result.index + 1
    )

    return result


def save_at_risk_list(
    dataframe: pd.DataFrame,
    path: str,
) -> None:
    dataframe.to_csv(
        path,
        index=False,
    )