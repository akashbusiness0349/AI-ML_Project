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

    candidate_result = (
        engine.recommend_for_candidate(
            candidates[0]["candidate_id"],
            top_k=5,
            model_available=False,
        )
    )

    company_result = (
        engine.recommend_for_company(
            companies[0]["company_id"],
            top_k=5,
            model_available=False,
        )
    )

    passed = (
        candidate_result["status"] == "FALLBACK"
        and company_result["status"] == "FALLBACK"
    )

    result = {
        "task": "Phase 3 Task 12",
        "status": "PASS" if passed else "FAIL",
        "failure_mode": "MODEL_UNAVAILABLE",
        "candidate_fallback": candidate_result,
        "company_fallback": company_result,
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()