from .data import FEATURE_COLUMNS


def explain_model(model):
    classifier = model.named_steps[
        "classifier"
    ]

    coefficients = classifier.coef_[0]

    pairs = sorted(
        zip(
            FEATURE_COLUMNS,
            coefficients,
        ),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    return [
        {
            "feature": feature,
            "coefficient": float(coef),
            "direction": (
                "increases_risk"
                if coef > 0
                else "decreases_risk"
            ),
        }
        for feature, coef in pairs
    ]


def explain_row(model, row):
    score = float(
        model.predict_proba(
            row[FEATURE_COLUMNS]
        )[:, 1][0]
    )

    return {
        "prediction_score": score,
        "feature_values": {
            feature: float(row.iloc[0][
                feature
            ])
            for feature in FEATURE_COLUMNS
        },
        "explanation": (
            "Higher recent inactivity, longer time since activity, "
            "and lower recent activity can increase predicted disengagement risk. "
            "The model uses only prediction-time behavioral features."
        ),
    }