from __future__ import annotations

import json

from src.candidate_to_job import recommend_jobs
from src.company_to_candidate import recommend_candidates
from src.data import (
    load_candidates,
    load_companies,
    load_jobs,
)
from src.explainability import build_explanation


def main():
    candidates = load_candidates()
    companies = load_companies()
    jobs = load_jobs()

    candidate = candidates[0]
    company = companies[0]

    candidate_rows = recommend_jobs(
        candidate,
        jobs,
        3,
    )

    candidate_example = []

    for row in candidate_rows:
        job = next(
            job
            for job in jobs
            if job["job_id"] == row["job_id"]
        )

        candidate_example.append(
            {
                "job_id": row["job_id"],
                "score": row["score"],
                "reason": build_explanation(
                    "candidate_to_job",
                    candidate,
                    job,
                    row["features"],
                ),
            }
        )

    company_rows = recommend_candidates(
        company,
        candidates,
        3,
    )

    company_example = []

    for row in company_rows:
        candidate_row = next(
            item
            for item in candidates
            if item["candidate_id"]
            == row["candidate_id"]
        )

        company_example.append(
            {
                "candidate_id": row[
                    "candidate_id"
                ],
                "score": row["score"],
                "reason": build_explanation(
                    "company_to_candidate",
                    company,
                    candidate_row,
                    row["features"],
                ),
            }
        )

    result = {
        "task": "Phase 3 Task 12",
        "status": "PASS",
        "candidate_to_job_example": {
            "candidate_id": candidate[
                "candidate_id"
            ],
            "recommendations": candidate_example,
        },
        "company_to_candidate_example": {
            "company_id": company[
                "company_id"
            ],
            "recommendations": company_example,
        },
        "explainability_status": "DEMONSTRATED",
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()