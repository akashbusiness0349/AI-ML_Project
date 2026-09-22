import numpy as np


def baseline_score(df):
    """
    Non-ML recency baseline.

    Higher score means higher disengagement risk.
    """

    days = df["days_since_last_activity"].astype(float)

    score = days / 14.0

    return np.clip(score, 0.0, 1.0)


def baseline_predict(df, threshold=0.5):
    return (
        baseline_score(df) >= threshold
    ).astype(int)