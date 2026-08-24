"""
PlaceMux Phase 2 — Task 6
Match Quality Baseline Engine
"""

MODEL_VERSION = "v1"

HIGH_QUALITY_THRESHOLD = 0.80
LOW_QUALITY_THRESHOLD = 0.50


def calculate_average_match_score(results):
    """Calculate average match score."""

    if not results:
        return 0.0

    total = sum(
        item["match_score"]
        for item in results
    )

    return total / len(results)


def calculate_top_1_relevance(
    results,
    expected_top_id
):
    """Check whether the expected best match is ranked first."""

    if not results:
        return 0.0

    first_result = results[0]

    result_id = (
        first_result.get("job_id")
        or first_result.get("student_id")
    )

    return 1.0 if result_id == expected_top_id else 0.0


def calculate_top_3_relevance(
    results,
    relevant_ids
):
    """Calculate the percentage of relevant items inside top 3."""

    if not results:
        return 0.0

    top_three = results[:3]

    matched = 0

    for item in top_three:

        result_id = (
            item.get("job_id")
            or item.get("student_id")
        )

        if result_id in relevant_ids:
            matched += 1

    return matched / len(top_three)


def check_ranking_consistency(
    first_results,
    second_results
):
    """Check whether repeated rankings are identical."""

    if len(first_results) != len(
        second_results
    ):
        return False

    for first, second in zip(
        first_results,
        second_results
    ):

        first_id = (
            first.get("job_id")
            or first.get("student_id")
        )

        second_id = (
            second.get("job_id")
            or second.get("student_id")
        )

        if first_id != second_id:
            return False

        if (
            first["match_score"]
            != second["match_score"]
        ):
            return False

    return True


def calculate_high_quality_rate(results):
    """Calculate percentage of matches >= 80%."""

    if not results:
        return 0.0

    high_quality = sum(
        item["match_score"]
        >= HIGH_QUALITY_THRESHOLD
        for item in results
    )

    return high_quality / len(results)


def calculate_low_quality_rate(results):
    """Calculate percentage of matches below 50%."""

    if not results:
        return 0.0

    low_quality = sum(
        item["match_score"]
        < LOW_QUALITY_THRESHOLD
        for item in results
    )

    return low_quality / len(results)


def calculate_overall_quality(
    average_match_score,
    top_1_relevance,
    top_3_relevance,
    ranking_consistency
):
    """
    Calculate an overall baseline quality score.

    Equal weighting is used so the baseline remains
    transparent and easy to compare in future tasks.
    """

    consistency_score = (
        1.0
        if ranking_consistency
        else 0.0
    )

    return (
        average_match_score
        + top_1_relevance
        + top_3_relevance
        + consistency_score
    ) / 4


def build_quality_baseline(
    results,
    expected_top_id,
    relevant_ids,
    repeated_results
):
    """Build the complete quality baseline."""

    average_score = (
        calculate_average_match_score(
            results
        )
    )

    top_1 = calculate_top_1_relevance(
        results,
        expected_top_id
    )

    top_3 = calculate_top_3_relevance(
        results,
        relevant_ids
    )

    consistency = check_ranking_consistency(
        results,
        repeated_results
    )

    high_quality_rate = (
        calculate_high_quality_rate(
            results
        )
    )

    low_quality_rate = (
        calculate_low_quality_rate(
            results
        )
    )

    overall_quality = (
        calculate_overall_quality(
            average_score,
            top_1,
            top_3,
            consistency
        )
    )

    return {
        "average_match_score":
            round(average_score, 4),

        "top_1_relevance":
            round(top_1, 4),

        "top_3_relevance":
            round(top_3, 4),

        "ranking_consistency":
            consistency,

        "high_quality_match_rate":
            round(high_quality_rate, 4),

        "low_quality_match_rate":
            round(low_quality_rate, 4),

        "overall_baseline_quality":
            round(overall_quality, 4)
    }