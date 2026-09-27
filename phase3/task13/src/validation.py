from __future__ import annotations

from collections import Counter


REQUIRED_RESUME_FIELDS = {
    "resume_id",
    "title",
    "summary",
    "skills",
    "experience",
}

REQUIRED_JOB_FIELDS = {
    "job_id",
    "title",
    "description",
    "requirements",
}


def validate_documents(
    resumes: list[dict],
    jobs: list[dict],
) -> dict:
    errors = []

    for index, row in enumerate(resumes):
        missing = sorted(
            REQUIRED_RESUME_FIELDS - set(row)
        )

        if missing:
            errors.append(
                {
                    "type": "resume",
                    "index": index,
                    "missing_fields": missing,
                }
            )

    for index, row in enumerate(jobs):
        missing = sorted(
            REQUIRED_JOB_FIELDS - set(row)
        )

        if missing:
            errors.append(
                {
                    "type": "job",
                    "index": index,
                    "missing_fields": missing,
                }
            )

    resume_ids = [x["resume_id"] for x in resumes]
    job_ids = [x["job_id"] for x in jobs]

    duplicate_resumes = [
        key
        for key, count in Counter(resume_ids).items()
        if count > 1
    ]

    duplicate_jobs = [
        key
        for key, count in Counter(job_ids).items()
        if count > 1
    ]

    if duplicate_resumes:
        errors.append(
            {
                "type": "duplicate_resume_ids",
                "ids": duplicate_resumes,
            }
        )

    if duplicate_jobs:
        errors.append(
            {
                "type": "duplicate_job_ids",
                "ids": duplicate_jobs,
            }
        )

    return {
        "status": "PASS" if not errors else "FAIL",
        "resume_count": len(resumes),
        "job_count": len(jobs),
        "errors": errors,
    }