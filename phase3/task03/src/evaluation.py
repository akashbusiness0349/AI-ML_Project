from __future__ import annotations

import math


def _same_number(
    first,
    second,
    tolerance=1e-12
):

    return math.isclose(
        float(first),
        float(second),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def compare_predictions(
    baseline_outputs: list[dict],
    optimized_outputs: list[dict],
) -> dict:

    if len(baseline_outputs) != len(
        optimized_outputs
    ):
        raise ValueError(
            "Prediction lists have different lengths"
        )

    decision_matches = 0
    score_matches = 0

    first_mismatch = None

    for index, (
        baseline,
        optimized
    ) in enumerate(
        zip(
            baseline_outputs,
            optimized_outputs
        )
    ):

        decision_equal = (
            baseline.get("recommendation")
            == optimized.get("recommendation")
        )

        score_equal = _same_number(
            baseline.get("score", 0.0),
            optimized.get("score", 0.0),
        )

        if decision_equal:
            decision_matches += 1

        if score_equal:
            score_matches += 1

        if (
            first_mismatch is None
            and (
                not decision_equal
                or not score_equal
            )
        ):

            first_mismatch = {
                "index": index,
                "baseline": baseline,
                "optimized": optimized,
            }

    total = len(baseline_outputs)

    return {
        "total_predictions": total,
        "decision_consistency_percent": (
            decision_matches
            / total
            * 100.0
            if total
            else 100.0
        ),
        "score_consistency_percent": (
            score_matches
            / total
            * 100.0
            if total
            else 100.0
        ),
        "quality_preserved": (
            decision_matches == total
            and score_matches == total
        ),
        "first_mismatch": first_mismatch,
        "comparison_rule": (
            "same recommendation decision and "
            "same score within 1e-12"
        ),
    }