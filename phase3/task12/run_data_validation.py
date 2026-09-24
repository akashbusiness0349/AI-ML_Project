from __future__ import annotations

import json

from src.data import (
    load_candidates,
    load_companies,
    load_interactions,
    load_jobs,
)
from src.validation import (
    REQUIRED_CANDIDATE_FIELDS,
    REQUIRED_COMPANY_FIELDS,
    REQUIRED_JOB_FIELDS,
    validate_interactions,
    validate_records,
)


def main():
    candidates = load_candidates()
    companies = load_companies()
    jobs = load_jobs()
    interactions = load_interactions()

    candidate_validation = validate_records(
        candidates,
        REQUIRED_CANDIDATE_FIELDS,
    )

    company_validation = validate_records(
        companies,
        REQUIRED_COMPANY_FIELDS,
    )

    job_validation = validate_records(
        jobs,
        REQUIRED_JOB_FIELDS,
    )

    interaction_validation = validate_interactions(
        interactions,
        {
            row["candidate_id"]
            for row in candidates
        },
        {
            row["company_id"]
            for row in companies
        },
        {
            row["job_id"]
            for row in jobs
        },
    )

    passed = all(
        [
            candidate_validation["all_valid"],
            company_validation["all_valid"],
            job_validation["all_valid"],
            interaction_validation["all_valid"],
        ]
    )

    result = {
        "task": "Phase 3 Task 12",
        "status": "PASS" if passed else "FAIL",
        "candidate_validation": candidate_validation,
        "company_validation": company_validation,
        "job_validation": job_validation,
        "interaction_validation": interaction_validation,
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()