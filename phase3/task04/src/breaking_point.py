from __future__ import annotations

from typing import Any, Dict, List, Optional


def identify_breaking_point(
    results: List[Dict[str, Any]],
    latency_slo_ms: float = 100.0,
    error_rate_slo_percent: float = 1.0,
) -> Dict[str, Any]:

    if not results:
        return {
            "status": "NO_RESULTS",
            "breaking_point_found": False,
            "reason": "No load-test results were supplied.",
        }

    ordered = sorted(
        results,
        key=lambda item: int(item["concurrency"]),
    )

    first_breach: Optional[Dict[str, Any]] = None

    for result in ordered:
        p95 = float(result.get("p95_ms", 0.0))
        error_rate = float(
            result.get("error_rate_percent", 0.0)
        )

        latency_breach = p95 > latency_slo_ms
        error_breach = error_rate > error_rate_slo_percent

        if latency_breach or error_breach:
            first_breach = result
            break

    passing_results = [
        result
        for result in ordered
        if bool(result.get("slo_pass", False))
    ]

    if first_breach is None:
        return {
            "status": "NO_BREACH_IN_TESTED_RANGE",
            "breaking_point_found": False,
            "latency_slo_ms": latency_slo_ms,
            "error_rate_slo_percent": error_rate_slo_percent,
            "highest_tested_concurrency": ordered[-1]["concurrency"],
            "highest_tested_qps": ordered[-1]["qps"],
            "sustainable_result": (
                passing_results[-1] if passing_results else None
            ),
            "note": (
                "No SLO breach was observed within the tested range. "
                "Increase the test range before claiming an exact "
                "breaking point."
            ),
        }

    latency_breach = (
        float(first_breach.get("p95_ms", 0.0))
        > latency_slo_ms
    )

    error_breach = (
        float(first_breach.get("error_rate_percent", 0.0))
        > error_rate_slo_percent
    )

    reasons = []

    if latency_breach:
        reasons.append("p95_latency")

    if error_breach:
        reasons.append("error_rate")

    sustainable = (
        passing_results[-1]
        if passing_results
        else None
    )

    return {
        "status": "BREAKING_POINT_FOUND",
        "breaking_point_found": True,
        "latency_slo_ms": latency_slo_ms,
        "error_rate_slo_percent": error_rate_slo_percent,
        "breaking_point_concurrency": first_breach["concurrency"],
        "breaking_point_qps": first_breach["qps"],
        "breaking_point_p95_ms": first_breach["p95_ms"],
        "breaking_point_error_rate_percent": first_breach[
            "error_rate_percent"
        ],
        "breach_reasons": reasons,
        "sustainable_result": sustainable,
        "previous_passing_concurrency": (
            sustainable["concurrency"]
            if sustainable
            else None
        ),
        "previous_passing_qps": (
            sustainable["qps"]
            if sustainable
            else 0.0
        ),
    }