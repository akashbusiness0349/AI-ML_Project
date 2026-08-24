"""
PlaceMux Phase 2 — Task 7
Pay-per-Application Conversion-Oriented Ranking
"""

MODEL_VERSION = "v1-conversion"


def calculate_conversion_priority(
    match_score,
    relevance_score,
    application_intent_score,
    application_value_score
):
    """
    Calculate a conversion-oriented priority score.

    Match relevance remains the primary signal.
    Conversion-related signals provide controlled
    ranking adjustments.
    """

    return round(
        (
            match_score * 0.60
            + relevance_score * 0.20
            + application_intent_score * 0.10
            + application_value_score * 0.10
        ),
        4
    )


def rank_for_conversion(opportunities):
    """
    Rank opportunities using the tuned conversion score.
    """

    ranked = []

    for opportunity in opportunities:

        score = calculate_conversion_priority(
            match_score=opportunity[
                "match_score"
            ],
            relevance_score=opportunity[
                "relevance_score"
            ],
            application_intent_score=opportunity[
                "application_intent_score"
            ],
            application_value_score=opportunity[
                "application_value_score"
            ]
        )

        item = dict(opportunity)

        item[
            "conversion_priority_score"
        ] = score

        ranked.append(item)

    ranked.sort(
        key=lambda item:
            item[
                "conversion_priority_score"
            ],
        reverse=True
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):
        item["rank"] = index

    return ranked


def calculate_conversion_proxy(
    ranked_results,
    threshold=0.70
):
    """
    Conversion proxy.

    A result is considered conversion-ready when
    its tuned priority score reaches the threshold.

    This is a proxy metric because real paid-application
    history is not available in the current dataset.
    """

    if not ranked_results:
        return 0.0

    conversion_ready = sum(
        item[
            "conversion_priority_score"
        ] >= threshold
        for item in ranked_results
    )

    return round(
        conversion_ready
        / len(ranked_results),
        4
    )


def calculate_average_match_score(
    results
):
    """Calculate average original match quality."""

    if not results:
        return 0.0

    return round(
        sum(
            item["match_score"]
            for item in results
        ) / len(results),
        4
    )