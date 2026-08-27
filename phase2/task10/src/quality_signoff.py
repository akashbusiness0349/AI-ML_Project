"""
PlaceMux Phase 2 — Task 10
Monetization Integration & Revenue Dashboard

Matching quality sign-off logic.
"""


def calculate_change(baseline, post_monetization):
    """
    Calculate absolute change between baseline and
    post-monetization metric.
    """
    return round(post_monetization - baseline, 4)


def evaluate_quality_signoff(
    baseline_metrics,
    post_monetization_metrics,
    allowed_relevance_drop=0.05
):
    """
    Compare baseline and post-monetization matching quality.

    Returns a structured quality sign-off payload.
    """

    comparison = {
        "average_match_score_change": calculate_change(
            baseline_metrics["average_match_score"],
            post_monetization_metrics["average_match_score"]
        ),
        "top_1_relevance_change": calculate_change(
            baseline_metrics["top_1_relevance"],
            post_monetization_metrics["top_1_relevance"]
        ),
        "top_3_relevance_change": calculate_change(
            baseline_metrics["top_3_relevance"],
            post_monetization_metrics["top_3_relevance"]
        ),
        "high_quality_match_rate_change": calculate_change(
            baseline_metrics["high_quality_match_rate"],
            post_monetization_metrics["high_quality_match_rate"]
        ),
        "low_quality_match_rate_change": calculate_change(
            baseline_metrics["low_quality_match_rate"],
            post_monetization_metrics["low_quality_match_rate"]
        )
    }

    ranking_consistency = (
        post_monetization_metrics["ranking_consistency"]
    )

    average_score_regression = (
        comparison["average_match_score_change"]
        < -allowed_relevance_drop
    )

    top_1_regression = (
        comparison["top_1_relevance_change"]
        < -allowed_relevance_drop
    )

    top_3_regression = (
        comparison["top_3_relevance_change"]
        < -allowed_relevance_drop
    )

    high_quality_regression = (
        comparison["high_quality_match_rate_change"]
        < -allowed_relevance_drop
    )

    no_ranking_bias = (
        ranking_consistency
        and comparison["top_1_relevance_change"] >= -allowed_relevance_drop
        and comparison["top_3_relevance_change"] >= -allowed_relevance_drop
    )

    no_quality_regression = not (
        average_score_regression
        or top_1_regression
        or top_3_regression
        or high_quality_regression
    )

    relevance_protected = (
        comparison["average_match_score_change"]
        >= -allowed_relevance_drop
        and comparison["top_1_relevance_change"]
        >= -allowed_relevance_drop
        and comparison["top_3_relevance_change"]
        >= -allowed_relevance_drop
    )

    overall_quality_check = (
        ranking_consistency
        and relevance_protected
        and no_ranking_bias
        and no_quality_regression
    )

    if overall_quality_check:
        decision = "APPROVED"
        matching_quality_status = "PASS"
        monetization_regression = False

        reason = (
            "Post-monetization matching quality remained within "
            "the configured regression threshold. Ranking consistency "
            "was preserved and no measurable relevance degradation "
            "was detected."
        )
    else:
        decision = "REVIEW_REQUIRED"
        matching_quality_status = "FAIL"
        monetization_regression = True

        reason = (
            "Post-monetization matching quality exceeded the configured "
            "regression threshold. Matching quality requires review "
            "before final sign-off."
        )

    return {
        "comparison": comparison,
        "quality_checks": {
            "ranking_consistency": ranking_consistency,
            "relevance_protected": relevance_protected,
            "no_ranking_bias": no_ranking_bias,
            "no_quality_regression": no_quality_regression,
            "overall_quality_check": overall_quality_check,
            "allowed_relevance_drop": allowed_relevance_drop
        },
        "sign_off": {
            "matching_quality_status": matching_quality_status,
            "monetization_regression": monetization_regression,
            "decision": decision,
            "reason": reason
        },
        "final_status": (
            "PASS" if overall_quality_check else "FAIL"
        )
    }