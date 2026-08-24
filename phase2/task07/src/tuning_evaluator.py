"""
PlaceMux Phase 2 — Task 7
Baseline vs Tuned Ranking Evaluation
"""


def check_ranking_quality(
    ranked_results
):
    """
    Verify that ranking scores are descending.
    """

    scores = [
        item[
            "conversion_priority_score"
        ]
        for item in ranked_results
    ]

    return scores == sorted(
        scores,
        reverse=True
    )


def check_rank_sequence(
    ranked_results
):
    """Verify sequential ranking numbers."""

    expected = list(
        range(
            1,
            len(ranked_results) + 1
        )
    )

    actual = [
        item["rank"]
        for item in ranked_results
    ]

    return actual == expected


def check_match_quality_protection(
    baseline_average,
    tuned_average,
    tolerance=0.05
):
    """
    Ensure tuned ranking does not degrade average
    match quality by more than the allowed tolerance.

    Example:
    baseline = 0.80
    tolerance = 0.05

    Minimum acceptable tuned quality = 0.75
    """

    minimum_allowed = (
        baseline_average
        - tolerance
    )

    return tuned_average >= minimum_allowed


def calculate_quality_change(
    baseline_average,
    tuned_average
):
    """Calculate change in average match quality."""

    return round(
        tuned_average
        - baseline_average,
        4
    )


def calculate_conversion_change(
    baseline_conversion_proxy,
    tuned_conversion_proxy
):
    """Calculate conversion proxy improvement."""

    return round(
        tuned_conversion_proxy
        - baseline_conversion_proxy,
        4
    )


def evaluate_tuning(
    baseline_average_match,
    tuned_average_match,
    baseline_conversion_proxy,
    tuned_conversion_proxy,
    tuned_results
):
    """
    Evaluate whether the tuned ranking is suitable
    for the pay-per-application flow.
    """

    ranking_order = (
        check_ranking_quality(
            tuned_results
        )
    )

    rank_sequence = (
        check_rank_sequence(
            tuned_results
        )
    )

    quality_protected = (
        check_match_quality_protection(
            baseline_average_match,
            tuned_average_match
        )
    )

    quality_change = (
        calculate_quality_change(
            baseline_average_match,
            tuned_average_match
        )
    )

    conversion_change = (
        calculate_conversion_change(
            baseline_conversion_proxy,
            tuned_conversion_proxy
        )
    )

    conversion_improved_or_maintained = (
        conversion_change >= 0
    )

    overall_pass = all(
        [
            ranking_order,
            rank_sequence,
            quality_protected,
            conversion_improved_or_maintained
        ]
    )

    return {
        "ranking_order":
            ranking_order,

        "rank_sequence":
            rank_sequence,

        "match_quality_protected":
            quality_protected,

        "baseline_average_match":
            round(
                baseline_average_match,
                4
            ),

        "tuned_average_match":
            round(
                tuned_average_match,
                4
            ),

        "match_quality_change":
            quality_change,

        "baseline_conversion_proxy":
            round(
                baseline_conversion_proxy,
                4
            ),

        "tuned_conversion_proxy":
            round(
                tuned_conversion_proxy,
                4
            ),

        "conversion_proxy_change":
            conversion_change,

        "conversion_proxy_improved_or_maintained":
            conversion_improved_or_maintained,

        "overall_pass":
            overall_pass
    }