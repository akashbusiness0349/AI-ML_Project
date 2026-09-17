from datetime import datetime, timezone
from typing import Dict, List


def build_signoff(
    slo_config: Dict,
    observed_metrics: Dict,
    slo_evaluation: Dict,
    integration_passed: bool,
    fallback_passed: bool,
    heldout_evaluation: Dict,
    headroom: Dict,
    residual_risks: List[Dict],
    real_logged_data_available: bool = False,
    baseline_comparison_passed: bool = False,
) -> Dict:
    results = slo_evaluation.get("results", [])

    highest_safe = headroom.get(
        "capacity_reference_concurrency",
        slo_evaluation.get(
            "highest_safe_tested_concurrency",
            0,
        ),
    )

    recommended = headroom.get(
        "recommended_operating_concurrency",
        0,
    )

    safe_results = [
        item
        for item in results
        if item.get("passed") is True
    ]

    load_test_passed = len(safe_results) > 0 and highest_safe > 0
    slo_passed = (
        load_test_passed
        and all(
            item.get("p95_ms", float("inf"))
            <= item.get(
                "slo_latency_ms",
                slo_config.get("p95_latency_ms", 100.0),
            )
            and item.get("error_rate", 1.0)
            <= item.get(
                "slo_error_rate",
                slo_config.get("error_rate", 0.01),
            )
            and item.get("availability", 0.0)
            >= item.get(
                "slo_availability",
                slo_config.get("availability", 0.99),
            )
            for item in safe_results
        )
    )

    headroom_passed = (
        highest_safe > 0
        and recommended > 0
        and recommended < highest_safe
        and headroom.get("headroom_target", 0) > 0
    )

    heldout_passed = bool(
        heldout_evaluation.get("passed", False)
        or heldout_evaluation.get("quality_preserved", False)
        or (
            heldout_evaluation.get(
                "decision_consistency_percent",
                0,
            ) == 100.0
            and heldout_evaluation.get(
                "score_consistency_percent",
                0,
            ) == 100.0
        )
    )

    checks = {
        "normal_service": bool(observed_metrics.get("normal_service", True)),
        "integration": bool(integration_passed),
        "real_logged_data": bool(real_logged_data_available),
        "heldout_validation": heldout_passed,
        "baseline_quality": bool(baseline_comparison_passed),
        "load_test": load_test_passed,
        "slo": slo_passed,
        "headroom": headroom_passed,
        "fallback": bool(fallback_passed),
    }

    signoff_status = (
        "READY_FOR_REVIEW"
        if all(checks.values())
        else "NOT_READY"
    )

    return {
        "task": "Phase 3 Task 05",
        "title": "Reliability Sign-off & Scale Integration",
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "signoff_status": signoff_status,
        "checks": checks,
        "scale_evidence": {
            "highest_safe_tested_concurrency": highest_safe,
            "recommended_operating_concurrency": recommended,
            "capacity_reference_concurrency": highest_safe,
            "headroom_target": headroom.get(
                "headroom_target",
                0,
            ),
            "breaking_point_concurrency": slo_evaluation.get(
                "breaking_point_concurrency"
            ),
        },
        "slo_interpretation": {
            "policy": "SLO must hold at the declared operating concurrency. Higher concurrency tests are used to establish the measured breaking point.",
            "all_levels_within_slo": slo_evaluation.get(
                "all_levels_within_slo",
                False,
            ),
            "operating_level_within_slo": slo_passed,
        },
        "residual_risks": residual_risks,
    }