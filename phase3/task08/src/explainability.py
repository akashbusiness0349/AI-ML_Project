from __future__ import annotations

import pandas as pd


def explain_prediction(
    row: pd.Series,
    probability: float,
) -> dict:
    """
    Generate a plain-English behavioral explanation.

    Only behavioral features are used.
    """

    reasons: list[str] = []

    days = float(
        row["days_since_last_activity"]
    )

    recent_7d = int(
        row["recent_7d_events"]
    )

    event_count = int(
        row["event_count_14d"]
    )

    active_days = int(
        row["active_days_14d"]
    )

    if days >= 10:
        reasons.append(
            f"no recent activity for approximately {days:.1f} days"
        )
    elif days >= 5:
        reasons.append(
            f"activity recency has weakened ({days:.1f} days since last activity)"
        )

    if recent_7d == 0:
        reasons.append(
            "no activity was observed in the last 7 days"
        )

    if event_count <= 1:
        reasons.append(
            "very low activity volume in the 14-day lookback"
        )

    if active_days <= 1:
        reasons.append(
            "activity occurred on only one day in the lookback"
        )

    if not reasons:
        reasons.append(
            "recent behavioral activity remains present, "
            "but the model identifies elevated disengagement risk"
        )

    if probability >= 0.70:
        segment = "HIGH"
    elif probability >= 0.40:
        segment = "MEDIUM"
    else:
        segment = "LOW"

    return {
        "risk_probability": round(float(probability), 6),
        "risk_segment": segment,
        "reasons": reasons,
        "plain_english_reason": "; ".join(reasons),
        "recommended_action": recommended_action(segment),
    }


def recommended_action(segment: str) -> str:
    if segment == "HIGH":
        return (
            "Prioritize for immediate growth intervention using a "
            "re-engagement message or human follow-up."
        )

    if segment == "MEDIUM":
        return (
            "Place in a monitored re-engagement campaign and "
            "track response."
        )

    return (
        "No immediate intervention; continue normal lifecycle monitoring."
    )