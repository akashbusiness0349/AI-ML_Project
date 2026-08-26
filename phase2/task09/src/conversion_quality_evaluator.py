"""
PlaceMux Phase 2 — Task 9
Conversion Quality Evaluation
"""

from relevance_checker import (
    MODEL_VERSION,
    evaluate_relevance
)


MAX_ALLOWED_RELEVANCE_DROP = 0.05


def calculate_conversion_quality(
    results
):
    """
    Calculate a conversion-quality proxy.

    The proxy rewards relevant matches while ensuring
    monetization does not dominate relevance.
    """

    if not results:
        return 0.0

    relevant_results = sum(
        1
        for item in results
        if item["relevant"]
    )

    relevance_rate = (
        relevant_results / len(results)
    )

    average_score = (
        sum(
            item["match_score"]
            for item in results
        )
        / len(results)
    )

    conversion_quality = (
        relevance_rate * 0.60
        + average_score * 0.40
    )

    return round(
        conversion_quality,
        4
    )


def compare_metrics(
    baseline_metrics,
    post_paywall_metrics
):
    """Compare baseline and post-paywall relevance."""

    average_score_change = round(
        post_paywall_metrics[
            "average_match_score"
        ]
        -
        baseline_metrics[
            "average_match_score"
        ],
        4
    )

    top_1_change = round(
        post_paywall_metrics[
            "top_1_relevance"
        ]
        -
        baseline_metrics[
            "top_1_relevance"
        ],
        4
    )

    top_3_change = round(
        post_paywall_metrics[
            "top_3_relevance"
        ]
        -
        baseline_metrics[
            "top_3_relevance"
        ],
        4
    )

    return {
        "average_score_change":
            average_score_change,

        "top_1_relevance_change":
            top_1_change,

        "top_3_relevance_change":
            top_3_change
    }


def detect_relevance_regression(
    baseline_metrics,
    post_paywall_metrics
):
    """
    Detect whether relevance degraded beyond
    the configured tolerance.
    """

    changes = compare_metrics(
        baseline_metrics,
        post_paywall_metrics
    )

    average_regression = (
        changes["average_score_change"]
        < -MAX_ALLOWED_RELEVANCE_DROP
    )

    top_1_regression = (
        changes["top_1_relevance_change"]
        < -MAX_ALLOWED_RELEVANCE_DROP
    )

    top_3_regression = (
        changes["top_3_relevance_change"]
        < -MAX_ALLOWED_RELEVANCE_DROP
    )

    regression_detected = any(
        [
            average_regression,
            top_1_regression,
            top_3_regression
        ]
    )

    return {
        "regression_detected":
            regression_detected,

        "average_score_regression":
            average_regression,

        "top_1_regression":
            top_1_regression,

        "top_3_regression":
            top_3_regression,

        "allowed_relevance_drop":
            MAX_ALLOWED_RELEVANCE_DROP,

        "changes":
            changes
    }


def evaluate_conversion_quality(
    baseline_results,
    post_paywall_results
):
    """Run the complete conversion-quality evaluation."""

    baseline_metrics = evaluate_relevance(
        baseline_results
    )

    post_paywall_metrics = evaluate_relevance(
        post_paywall_results
    )

    baseline_conversion_quality = (
        calculate_conversion_quality(
            baseline_results
        )
    )

    post_paywall_conversion_quality = (
        calculate_conversion_quality(
            post_paywall_results
        )
    )

    regression = detect_relevance_regression(
        baseline_metrics,
        post_paywall_metrics
    )

    ranking_consistency = (
        post_paywall_metrics[
            "ranking_consistency"
        ]
    )

    no_relevance_regression = (
        not regression["regression_detected"]
    )

    overall_pass = all(
        [
            no_relevance_regression,
            ranking_consistency
        ]
    )

    return {
        "model_version":
            MODEL_VERSION,

        "baseline_metrics":
            baseline_metrics,

        "post_paywall_metrics":
            post_paywall_metrics,

        "baseline_conversion_quality":
            baseline_conversion_quality,

        "post_paywall_conversion_quality":
            post_paywall_conversion_quality,

        "conversion_quality_change":
            round(
                post_paywall_conversion_quality
                -
                baseline_conversion_quality,
                4
            ),

        "regression_check":
            regression,

        "ranking_consistency":
            ranking_consistency,

        "no_relevance_regression":
            no_relevance_regression,

        "overall_pass":
            overall_pass
    }