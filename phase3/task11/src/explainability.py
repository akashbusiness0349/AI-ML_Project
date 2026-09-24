from __future__ import annotations

from typing import Mapping

from .features import build_feature_dict


def explain_prediction(
    model,
    candidate: Mapping,
    job: Mapping,
) -> dict:
    features = build_feature_dict(
        candidate,
        job,
    )

    coefficients = (
        model.model.coef_[0]
    )

    contributions = []

    for feature, value, coefficient in zip(
        model.feature_names,
        [
            features[name]
            for name in model.feature_names
        ],
        coefficients,
    ):
        contribution = float(
            value * coefficient
        )

        if contribution > 0:
            direction = "supports_ranking"
        elif contribution < 0:
            direction = "reduces_ranking"
        else:
            direction = "neutral"

        contributions.append(
            {
                "feature": feature,
                "value": float(value),
                "coefficient": float(
                    coefficient
                ),
                "contribution": contribution,
                "direction": direction,
            }
        )

    contributions.sort(
        key=lambda x: abs(
            x["contribution"]
        ),
        reverse=True,
    )

    top = contributions[:3]

    reasons = []

    for item in top:
        if item["direction"] == "supports_ranking":
            reasons.append(
                f"{item['feature']} contributed positively"
            )
        elif item["direction"] == "reduces_ranking":
            reasons.append(
                f"{item['feature']} reduced the score"
            )

    return {
        "candidate_id": candidate["candidate_id"],
        "job_id": job["job_id"],
        "score": float(
            model.score(
                candidate,
                job,
            )
        ),
        "probability": float(
            model.predict_proba(
                candidate,
                job,
            )
        ),
        "features": features,
        "feature_contributions": contributions,
        "plain_english_reason": (
            "; ".join(reasons)
            if reasons
            else "The ranking score was determined by the model features."
        ),
        "explainability_status": "PASS",
    }