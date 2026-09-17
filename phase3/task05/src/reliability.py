"""
Reliability calculations for Task 05.
"""

from typing import Dict, List

from .monitoring import (
    SLOConfig,
    evaluate_slos,
)


def evaluate_load_results(
    results: List[Dict],
    config: SLOConfig,
) -> List[Dict]:

    evaluated = []

    for result in results:

        slo = evaluate_slos(
            result["metrics"],
            config,
        )

        evaluated.append(
            {
                **result,
                "slo_evaluation": slo,
            }
        )

    return evaluated


def find_first_breach(
    results: List[Dict],
) -> Dict:

    for result in results:

        evaluation = result[
            "slo_evaluation"
        ]

        if not evaluation[
            "all_slos_met"
        ]:

            reasons = []

            if not evaluation[
                "latency"
            ]["pass"]:
                reasons.append(
                    "p95_latency"
                )

            if not evaluation[
                "error_rate"
            ]["pass"]:
                reasons.append(
                    "error_rate"
                )

            if not evaluation[
                "availability"
            ]["pass"]:
                reasons.append(
                    "availability"
                )

            return {
                "status": "BREACH_FOUND",
                "breaking_point_concurrency": (
                    result["concurrency"]
                ),
                "reasons": reasons,
                "observed_metrics": result[
                    "metrics"
                ],
                "slo_evaluation": evaluation,
            }

    return {
        "status": (
            "NO_BREACH_IN_TESTED_RANGE"
        ),
        "breaking_point_concurrency": None,
        "reasons": [],
        "observed_metrics": None,
        "slo_evaluation": None,
    }


def calculate_headroom(
    results: List[Dict],
    target_percent: float = 30.0,
) -> Dict:

    safe_levels = [
        result["concurrency"]
        for result in results
        if result[
            "slo_evaluation"
        ]["all_slos_met"]
    ]

    if not safe_levels:

        return {
            "status": "NO_SAFE_LEVEL",
            "headroom_target_percent": target_percent,
            "highest_safe_tested_concurrency": None,
            "recommended_operating_concurrency": None,
        }

    highest_safe = max(
        safe_levels
    )

    recommended = int(
        highest_safe
        * (
            1.0
            - target_percent / 100.0
        )
    )

    recommended = max(
        1,
        recommended,
    )

    breaking = find_first_breach(
        results
    )

    return {
        "status": "CALCULATED",
        "headroom_target_percent": target_percent,
        "highest_safe_tested_concurrency": highest_safe,
        "recommended_operating_concurrency": recommended,
        "capacity_reference_concurrency": (
            breaking[
                "breaking_point_concurrency"
            ]
        ),
        "capacity_reference_type": (
            "measured_breaking_point"
            if breaking[
                "breaking_point_concurrency"
            ]
            is not None
            else "highest_tested_safe_level"
        ),
        "formula": (
            "recommended operating concurrency = "
            "highest safe tested concurrency × "
            "(1 - headroom target)"
        ),
        "evidence_boundary": (
            "Measured capacity is specific to the "
            "tested local environment and workload. "
            "It is not a production traffic guarantee."
        ),
    }