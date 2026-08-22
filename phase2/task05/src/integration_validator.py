"""
PlaceMux Phase 2 — Task 5
Marketplace Integration Validator
"""

MODEL_VERSION = "v1"


def validate_descending_ranking(results):
    """Verify that ranking scores are descending."""

    scores = [
        item["match_score"]
        for item in results
    ]

    return scores == sorted(
        scores,
        reverse=True
    )


def validate_ranks(results):
    """Verify that ranks are sequential."""

    expected_ranks = list(
        range(1, len(results) + 1)
    )

    actual_ranks = [
        item["rank"]
        for item in results
    ]

    return actual_ranks == expected_ranks


def validate_score_range(results):
    """Verify that scores are between 0 and 1."""

    return all(
        0 <= item["match_score"] <= 1
        for item in results
    )


def validate_explanations(results):
    """Verify that every result contains explanation data."""

    for item in results:

        explanation = item.get(
            "explanation"
        )

        if not explanation:
            return False

        if not explanation.get(
            "summary"
        ):
            return False

        if not isinstance(
            explanation.get(
                "positive_factors",
                []
            ),
            list
        ):
            return False

        if not isinstance(
            explanation.get(
                "negative_factors",
                []
            ),
            list
        ):
            return False

    return True


def validate_model_version(results):
    """Verify model version consistency."""

    return all(
        item.get("model_version")
        == MODEL_VERSION
        for item in results
    )


def validate_ranking_relevance(
    results,
    expected_top_id
):
    """
    Verify that the expected highly relevant
    result appears at rank 1.
    """

    if not results:
        return False

    return (
        results[0].get("job_id")
        == expected_top_id
        or
        results[0].get("student_id")
        == expected_top_id
    )


def validate_consistency(
    first_results,
    second_results
):
    """
    Verify that repeated execution produces
    the same ranking order and scores.
    """

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


def validate_end_to_end(
    job_results,
    candidate_results,
    expected_top_job,
    expected_top_candidate,
    repeated_job_results=None,
    repeated_candidate_results=None
):
    """
    Run the complete marketplace validation suite.
    """

    validation = {}

    validation[
        "ranked_jobs_returned"
    ] = bool(job_results)

    validation[
        "ranked_candidates_returned"
    ] = bool(candidate_results)

    validation[
        "job_ranking_order"
    ] = validate_descending_ranking(
        job_results
    )

    validation[
        "candidate_ranking_order"
    ] = validate_descending_ranking(
        candidate_results
    )

    validation[
        "job_rank_sequence"
    ] = validate_ranks(
        job_results
    )

    validation[
        "candidate_rank_sequence"
    ] = validate_ranks(
        candidate_results
    )

    validation[
        "job_score_range"
    ] = validate_score_range(
        job_results
    )

    validation[
        "candidate_score_range"
    ] = validate_score_range(
        candidate_results
    )

    validation[
        "job_explanations"
    ] = validate_explanations(
        job_results
    )

    validation[
        "candidate_explanations"
    ] = validate_explanations(
        candidate_results
    )

    validation[
        "job_model_version"
    ] = validate_model_version(
        job_results
    )

    validation[
        "candidate_model_version"
    ] = validate_model_version(
        candidate_results
    )

    validation[
        "job_relevance"
    ] = validate_ranking_relevance(
        job_results,
        expected_top_job
    )

    validation[
        "candidate_relevance"
    ] = validate_ranking_relevance(
        candidate_results,
        expected_top_candidate
    )

    if (
        repeated_job_results is not None
    ):
        validation[
            "job_ranking_consistency"
        ] = validate_consistency(
            job_results,
            repeated_job_results
        )

    if (
        repeated_candidate_results
        is not None
    ):
        validation[
            "candidate_ranking_consistency"
        ] = validate_consistency(
            candidate_results,
            repeated_candidate_results
        )

    validation[
        "all_checks_passed"
    ] = all(
        validation.values()
    )

    return validation