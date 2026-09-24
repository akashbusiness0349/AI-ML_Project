from __future__ import annotations

from typing import Mapping


FEATURE_NAMES = [
    "experience_match",
    "job_popularity",
    "location_match",
    "skill_overlap",
]


EXPERIENCE_ORDER = {
    "entry": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
}


def _normalise(value: object) -> str:
    return str(value or "").strip().lower()


def skill_overlap(candidate: Mapping, job: Mapping) -> float:
    candidate_skills = {
        _normalise(x)
        for x in candidate.get("skills", [])
    }

    job_skills = {
        _normalise(x)
        for x in job.get("skills", [])
    }

    if not job_skills:
        return 0.0

    return len(candidate_skills & job_skills) / len(job_skills)


def experience_match(candidate: Mapping, job: Mapping) -> float:
    candidate_level = _normalise(
        candidate.get("experience_level")
    )

    job_level = _normalise(
        job.get("experience_level")
    )

    if candidate_level == job_level:
        return 1.0

    if candidate_level not in EXPERIENCE_ORDER:
        return 0.0

    if job_level not in EXPERIENCE_ORDER:
        return 0.0

    distance = abs(
        EXPERIENCE_ORDER[candidate_level]
        - EXPERIENCE_ORDER[job_level]
    )

    return max(0.0, 1.0 - 0.5 * distance)


def location_match(candidate: Mapping, job: Mapping) -> float:
    return float(
        _normalise(candidate.get("location"))
        == _normalise(job.get("location"))
    )


def job_popularity(job: Mapping) -> float:
    popularity = float(job.get("popularity", 0.0))

    return max(
        0.0,
        min(1.0, popularity / 100.0),
    )


def build_feature_vector(
    candidate: Mapping,
    job: Mapping,
) -> list[float]:
    return [
        experience_match(candidate, job),
        job_popularity(job),
        location_match(candidate, job),
        skill_overlap(candidate, job),
    ]


def build_feature_dict(
    candidate: Mapping,
    job: Mapping,
) -> dict[str, float]:
    values = build_feature_vector(candidate, job)

    return dict(
        zip(
            FEATURE_NAMES,
            values,
        )
    )