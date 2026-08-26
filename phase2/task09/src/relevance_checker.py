"""
PlaceMux Phase 2 — Task 9
Relevance Regression Checker
"""

MODEL_VERSION = "v1-conversion-quality"


def calculate_average_score(results):
    """Calculate average match score."""

    if not results:
        return 0.0

    total = sum(
        item["match_score"]
        for item in results
    )

    return round(
        total / len(results),
        4
    )


def calculate_top_1_relevance(results):
    """Check whether the top-ranked result is relevant."""

    if not results:
        return 0.0

    return round(
        1.0
        if results[0]["relevant"]
        else 0.0,
        4
    )


def calculate_top_3_relevance(results):
    """Calculate relevance among top three results."""

    if not results:
        return 0.0

    top_results = results[:3]

    relevant_count = sum(
        1
        for item in top_results
        if item["relevant"]
    )

    return round(
        relevant_count / len(top_results),
        4
    )


def check_ranking_consistency(results):
    """Verify scores are in descending order."""

    scores = [
        item["match_score"]
        for item in results
    ]

    return scores == sorted(
        scores,
        reverse=True
    )


def calculate_high_quality_rate(results):
    """Calculate percentage of high-quality matches."""

    if not results:
        return 0.0

    count = sum(
        1
        for item in results
        if item["match_score"] >= 0.70
    )

    return round(
        count / len(results),
        4
    )


def calculate_low_quality_rate(results):
    """Calculate percentage of low-quality matches."""

    if not results:
        return 0.0

    count = sum(
        1
        for item in results
        if item["match_score"] < 0.50
    )

    return round(
        count / len(results),
        4
    )


def evaluate_relevance(results):
    """Generate relevance metrics for a ranking."""

    return {
        "average_match_score":
            calculate_average_score(results),

        "top_1_relevance":
            calculate_top_1_relevance(results),

        "top_3_relevance":
            calculate_top_3_relevance(results),

        "ranking_consistency":
            check_ranking_consistency(results),

        "high_quality_match_rate":
            calculate_high_quality_rate(results),

        "low_quality_match_rate":
            calculate_low_quality_rate(results)
    }