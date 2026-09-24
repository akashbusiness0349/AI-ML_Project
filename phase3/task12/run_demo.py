from __future__ import annotations

import json

from src.data import (
    load_candidates,
    load_companies,
    load_jobs,
)
from src.recommender import RecommendationEngine


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

    candidate_result = (
        engine.recommend_for_candidate(
            candidate_id,
            top_k=5,
        )
    )

    company_result = (
        engine.recommend_for_company(
            company_id,
            top_k=5,
        )
    )

    print(
        json.dumps(
            {
                "task": "Phase 3 Task 12",
                "candidate_to_job": candidate_result,
                "company_to_candidate": company_result,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()