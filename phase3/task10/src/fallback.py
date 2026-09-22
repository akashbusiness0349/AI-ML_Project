from .baseline import baseline_score


def safe_prediction(
    model,
    row,
    model_available=True,
):
    if model_available and model is not None:
        from .data import FEATURE_COLUMNS

        score = float(
            model.predict_proba(
                row[FEATURE_COLUMNS]
            )[:, 1][0]
        )

        return {
            "variant": "treatment",
            "score": score,
            "fallback_used": False,
        }

    score = float(
        baseline_score(row).iloc[0]
    )

    return {
        "variant": "control_fallback",
        "score": score,
        "fallback_used": True,
    }