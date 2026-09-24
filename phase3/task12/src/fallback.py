from __future__ import annotations


class RecommendationUnavailable(RuntimeError):
    pass


def fallback_recommendations(
    items: list[dict],
    item_id_field: str,
    top_k: int = 5,
) -> dict:
    ranked = sorted(
        items,
        key=lambda row: row.get(item_id_field, ""),
    )[:top_k]

    return {
        "status": "FALLBACK",
        "reason": "MODEL_UNAVAILABLE",
        "recommendations": [
            {
                item_id_field: row[item_id_field],
                "score": 0.0,
                "position": position,
                "explanation": (
                    "Recommendation model unavailable; "
                    "returned deterministic fallback ordering."
                ),
            }
            for position, row in enumerate(ranked, start=1)
        ],
    }