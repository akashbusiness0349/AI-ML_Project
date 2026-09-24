from __future__ import annotations


REQUIRED_CANDIDATE_FIELDS = {
    "candidate_id",
    "skills",
    "experience_level",
    "location",
}

REQUIRED_COMPANY_FIELDS = {
    "company_id",
    "skills",
    "preferred_experience",
    "location",
}

REQUIRED_JOB_FIELDS = {
    "job_id",
    "title",
    "skills",
    "experience_level",
    "location",
    "popularity",
}


def validate_records(
    records: list[dict],
    required_fields: set[str],
) -> dict:
    errors = []

    for index, row in enumerate(records):
        missing = sorted(
            required_fields - set(row.keys())
        )

        if missing:
            errors.append(
                {
                    "index": index,
                    "missing_fields": missing,
                }
            )

    return {
        "total": len(records),
        "valid": len(records) - len(errors),
        "invalid": len(errors),
        "all_valid": not errors,
        "errors": errors,
    }


def validate_interactions(
    interactions: list[dict],
    candidate_ids: set[str],
    company_ids: set[str],
    job_ids: set[str],
) -> dict:
    errors = []
    unknown_candidates = 0
    unknown_companies = 0
    unknown_jobs = 0

    for index, row in enumerate(interactions):
        missing = {
            field
            for field in (
                "interaction_id",
                "session_id",
                "candidate_id",
                "job_id",
                "event_type",
                "relevance",
            )
            if field not in row
        }

        if missing:
            errors.append(
                {
                    "index": index,
                    "missing_fields": sorted(missing),
                }
            )
            continue

        if row["candidate_id"] not in candidate_ids:
            unknown_candidates += 1

        if row.get("company_id") and (
            row["company_id"] not in company_ids
        ):
            unknown_companies += 1

        if row["job_id"] not in job_ids:
            unknown_jobs += 1

    return {
        "total": len(interactions),
        "valid": len(interactions) - len(errors),
        "invalid": len(errors),
        "all_valid": (
            not errors
            and unknown_candidates == 0
            and unknown_companies == 0
            and unknown_jobs == 0
        ),
        "errors": errors,
        "unknown_candidate_events": unknown_candidates,
        "unknown_company_events": unknown_companies,
        "unknown_job_events": unknown_jobs,
    }