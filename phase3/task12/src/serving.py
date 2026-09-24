from __future__ import annotations

from statistics import mean


class RecommendationService:
    def __init__(self, engine) -> None:
        self.engine = engine

    def candidate_jobs(
        self,
        candidate_id: str,
        top_k: int = 5,
    ) -> dict:
        return self.engine.recommend_for_candidate(
            candidate_id,
            top_k,
        )

    def company_candidates(
        self,
        company_id: str,
        top_k: int = 5,
    ) -> dict:
        return self.engine.recommend_for_company(
            company_id,
            top_k,
        )


def benchmark_callable(
    callable_fn,
    iterations: int = 100,
) -> dict:
    timings = []

    for _ in range(iterations):
        result = callable_fn()

        latency = result.get(
            "latency_ms",
            0.0,
        )

        timings.append(float(latency))

    ordered = sorted(timings)

    p95_index = min(
        len(ordered) - 1,
        int(len(ordered) * 0.95),
    )

    return {
        "iterations": iterations,
        "mean_ms": mean(timings),
        "p95_ms": ordered[p95_index],
        "min_ms": min(timings),
        "max_ms": max(timings),
    }