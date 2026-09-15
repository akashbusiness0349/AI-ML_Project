from __future__ import annotations


def cpu_time_cost(
    runtime_ms: float,
    requests: int,
    cpu_rate_per_second: float = 0.02,
) -> float:

    return (
        runtime_ms
        / 1000.0
        * requests
        * cpu_rate_per_second
    )


def compare_inference_cost(
    baseline: dict,
    optimized: dict,
    requests: int,
) -> dict:

    cpu_rate = 0.02

    baseline_cost = cpu_time_cost(
        baseline["avg_ms"],
        requests,
        cpu_rate,
    )

    optimized_cost = cpu_time_cost(
        optimized["avg_ms"],
        requests,
        cpu_rate,
    )

    reduction = (
        (
            baseline_cost
            - optimized_cost
        )
        / baseline_cost
        * 100.0
        if baseline_cost
        else 0.0
    )

    return {
        "requests": requests,
        "cpu_rate_per_second": cpu_rate,
        "baseline_avg_ms": baseline["avg_ms"],
        "optimized_avg_ms": optimized["avg_ms"],
        "baseline_cost_proxy": baseline_cost,
        "optimized_cost_proxy": optimized_cost,
        "cost_reduction_percent": reduction,
        "cost_unit": (
            "illustrative CPU-time cost units"
        ),
        "not_cloud_billing": True,
    }