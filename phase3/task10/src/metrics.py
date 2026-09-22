import math

import numpy as np
from scipy.stats import norm


def classification_metrics(y_true, scores, threshold=0.5):
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores).astype(float)

    predictions = (scores >= threshold).astype(int)

    tp = int(((predictions == 1) & (y_true == 1)).sum())
    fp = int(((predictions == 1) & (y_true == 0)).sum())
    tn = int(((predictions == 0) & (y_true == 0)).sum())
    fn = int(((predictions == 0) & (y_true == 1)).sum())

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    return {
        "threshold": float(threshold),
        "precision": float(precision),
        "recall": float(recall),
        "positive_rate": float(predictions.mean()),
        "confusion_matrix": [
            [tn, fp],
            [fn, tp],
        ],
    }


def proportion_effect(
    control_successes,
    control_n,
    treatment_successes,
    treatment_n,
):
    control_rate = control_successes / control_n
    treatment_rate = treatment_successes / treatment_n

    absolute_effect = treatment_rate - control_rate

    relative_effect = (
        absolute_effect / control_rate
        if control_rate > 0
        else 0.0
    )

    pooled = (
        (control_successes + treatment_successes)
        / (control_n + treatment_n)
    )

    standard_error = math.sqrt(
        pooled
        * (1 - pooled)
        * (
            1 / control_n
            + 1 / treatment_n
        )
    )

    if standard_error == 0:
        z = 0.0
        p_value = 1.0
    else:
        z = absolute_effect / standard_error
        p_value = 2 * norm.sf(abs(z))

    unpooled_se = math.sqrt(
        (
            control_rate * (1 - control_rate)
            / control_n
        )
        + (
            treatment_rate * (1 - treatment_rate)
            / treatment_n
        )
    )

    margin = 1.96 * unpooled_se

    return {
        "control_rate": float(control_rate),
        "treatment_rate": float(treatment_rate),
        "absolute_effect": float(absolute_effect),
        "relative_effect": float(relative_effect),
        "z_score": float(z),
        "p_value": float(p_value),
        "ci95_low": float(absolute_effect - margin),
        "ci95_high": float(absolute_effect + margin),
    }


def top_k_lift(y_true, scores, fraction=0.10):
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores).astype(float)

    n = len(y_true)
    k = max(1, int(round(n * fraction)))

    order = np.argsort(-scores)
    top = y_true[order[:k]]

    population_rate = y_true.mean()
    top_rate = top.mean()

    lift = (
        top_rate / population_rate
        if population_rate > 0
        else 0.0
    )

    return {
        "top_fraction": fraction,
        "top_k": k,
        "population_rate": float(population_rate),
        "top_k_rate": float(top_rate),
        "lift": float(lift),
    }