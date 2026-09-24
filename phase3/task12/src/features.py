from __future__ import annotations

from typing import Mapping


RANKING_FEATURES = [
    "skill_overlap",
    "experience_match",
    "location_match",
    "popularity",
]


def _normalise(values) -> set[str]:
    return {
        str(value).strip().lower()
        for value in values
        if str(value).strip()
    }


def skill_overlap(candidate: Mapping, job: Mapping) -> float:
    candidate_skills = _normalise(candidate.get("skills", []))
    job_skills = _normalise(job.get("skills", []))

    if not job_skills:
        return 0.0

    return len(candidate_skills & job_skills) / len(job_skills)


def experience_match(candidate: Mapping, job: Mapping) -> float:
    return float(
        str(candidate.get("experience_level", "")).lower()
        == str(job.get("experience_level", "")).lower()
    )


def location_match(candidate: Mapping, job: Mapping) -> float:
    return float(
        str(candidate.get("location", "")).lower()
        == str(job.get("location", "")).lower()
    )


def popularity(job: Mapping) -> float:
    return float(job.get("popularity", 0.0)) / 100.0


def candidate_job_features(
    candidate: Mapping,
    job: Mapping,
) -> dict[str, float]:
    return {
        "skill_overlap": skill_overlap(candidate, job),
        "experience_match": experience_match(candidate, job),
        "location_match": location_match(candidate, job),
        "popularity": popularity(job),
    }


def company_candidate_features(
    company: Mapping,
    candidate: Mapping,
) -> dict[str, float]:
    company_skills = _normalise(company.get("skills", []))
    candidate_skills = _normalise(candidate.get("skills", []))

    overlap = 0.0
    if company_skills:
        overlap = len(company_skills & candidate_skills) / len(company_skills)

    experience = float(
        str(company.get("preferred_experience", "")).lower()
        == str(candidate.get("experience_level", "")).lower()
    )

    location = float(
        str(company.get("location", "")).lower()
        == str(candidate.get("location", "")).lower()
    )

    return {
        "skill_overlap": overlap,
        "experience_match": experience,
        "location_match": location,
    }