from __future__ import annotations

from typing import Mapping


def popularity_job_baseline(
    jobs: list[Mapping],
    top_k: int = 5,
) -> list[dict]:
    ranked = sorted(
        jobs,
        key=lambda job: (
            -float(job.get("popularity", 0)),
            job["job_id"],
        ),
    )

    output = []

    for position, job in enumerate(ranked[:top_k], start=1):
        output.append(
            {
                "job_id": job["job_id"],
                "score": float(job.get("popularity", 0)) / 100.0,
                "position": position,
            }
        )

    return output


def company_baseline(
    candidates: list[Mapping],
    top_k: int = 5,
) -> list[dict]:
    ranked = sorted(
        candidates,
        key=lambda candidate: candidate["candidate_id"],
    )

    return [
        {
            "candidate_id": row["candidate_id"],
            "score": 0.0,
            "position": position,
        }
        for position, row in enumerate(ranked[:top_k], start=1)
    ]