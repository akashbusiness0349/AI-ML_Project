from __future__ import annotations

import json

from src.data import (
    load_candidates,
    load_companies,
    load_jobs,
)
from src.recommender import RecommendationEngine
from src.serving import benchmark_callable


LATENCY_SLO_MS = 100.0


def main():
    candidates = load_candidates()
    companies = load_companies()
    jobs = load_jobs()

    engine = RecommendationEngine(
        candidates,
        companies,
        jobs,
    )

    candidate_id = candidates[0][
        "candidate_id"
    ]

    company_id = companies[0][
        "company_id"
    ]

    candidate_benchmark = benchmark_callable(
        lambda: engine.recommend_for_candidate(
            candidate_id,
            top_k=5,
        ),
        iterations=100,
    )

    company_benchmark = benchmark_callable(
        lambda: engine.recommend_for_company(
            company_id,
            top_k=5,
        ),
        iterations=100,
    )

    passed = (
        candidate_benchmark["p95_ms"]
        <= LATENCY_SLO_MS
        and company_benchmark["p95_ms"]
        <= LATENCY_SLO_MS
    )

    result = {
        "task": "Phase 3 Task 12",
        "status": "PASS" if passed else "FAIL",
        "latency_slo_ms": LATENCY_SLO_MS,
        "candidate_to_job": candidate_benchmark,
        "company_to_candidate": company_benchmark,
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()