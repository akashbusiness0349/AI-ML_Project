"""
PlaceMux Phase 2 — Task 1
Student ↔ Job Matching Engine

This module provides a simple, deterministic baseline matching engine.
It converts student and job profile attributes into comparable signals
and produces an overall match score.
"""

from typing import Any, Dict, List


MODEL_VERSION = "v1"


def normalize(value: str) -> str:
    """Normalize text for comparison."""
    return value.strip().lower()


def calculate_skill_match(
    student_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
) -> float:
    """
    Calculate skill compatibility.

    Required skills receive higher importance than preferred skills.
    """

    student = {normalize(skill) for skill in student_skills}
    required = {normalize(skill) for skill in required_skills}
    preferred = {normalize(skill) for skill in preferred_skills}

    if not required and not preferred:
        return 1.0

    required_score = (
        len(student & required) / len(required)
        if required
        else 1.0
    )

    preferred_score = (
        len(student & preferred) / len(preferred)
        if preferred
        else 1.0
    )

    return round(
        (0.7 * required_score) + (0.3 * preferred_score),
        4,
    )


def calculate_education_match(
    student_degree: str,
    student_field: str,
    required_degree: str,
    required_fields: List[str],
) -> float:
    """Calculate education compatibility."""

    degree_match = (
        normalize(student_degree) == normalize(required_degree)
        if required_degree
        else True
    )

    field_match = (
        normalize(student_field)
        in {normalize(field) for field in required_fields}
        if required_fields
        else True
    )

    if degree_match and field_match:
        return 1.0

    if degree_match or field_match:
        return 0.5

    return 0.0


def calculate_experience_match(
    student_years: float,
    minimum_years: float,
) -> float:
    """Calculate experience compatibility."""

    if minimum_years <= 0:
        return 1.0

    score = student_years / minimum_years

    return round(min(score, 1.0), 4)


def calculate_location_match(
    student_country: str,
    student_city: str,
    job_country: str,
    job_city: str,
) -> float:
    """Calculate location compatibility."""

    if (
        normalize(student_country) == normalize(job_country)
        and normalize(student_city) == normalize(job_city)
    ):
        return 1.0

    if normalize(student_country) == normalize(job_country):
        return 0.5

    return 0.0


def calculate_role_match(
    desired_roles: List[str],
    job_role: str,
) -> float:
    """Calculate role compatibility."""

    desired = {normalize(role) for role in desired_roles}
    role = normalize(job_role)

    if role in desired:
        return 1.0

    return 0.0


def calculate_work_mode_match(
    preferred_modes: List[str],
    job_mode: str,
) -> float:
    """Calculate work-mode compatibility."""

    preferred = {normalize(mode) for mode in preferred_modes}
    mode = normalize(job_mode)

    if mode in preferred:
        return 1.0

    return 0.0


def calculate_verified_score_match(
    student_scores: Dict[str, float],
    required_scores: Dict[str, float],
) -> float:
    """Calculate compatibility with verified job score requirements."""

    if not required_scores:
        return 1.0

    scores = []

    for skill, required_score in required_scores.items():
        student_score = student_scores.get(skill)

        if student_score is None:
            scores.append(0.0)
            continue

        if required_score <= 0:
            scores.append(1.0)
            continue

        score = student_score / required_score
        scores.append(min(score, 1.0))

    return round(sum(scores) / len(scores), 4)


def calculate_match(
    student: Dict[str, Any],
    job: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare a student profile with a job profile.

    Returns a structured matching result compatible with the Task 1 API
    contract.
    """

    signals = {
        "skill_match": calculate_skill_match(
            student.get("skills", []),
            job.get("required_skills", []),
            job.get("preferred_skills", []),
        ),
        "education_match": calculate_education_match(
            student.get("degree", ""),
            student.get("field_of_study", ""),
            job.get("required_degree", ""),
            job.get("required_fields", []),
        ),
        "experience_match": calculate_experience_match(
            student.get("years_experience", 0),
            job.get("minimum_years_experience", 0),
        ),
        "location_match": calculate_location_match(
            student.get("country", ""),
            student.get("city", ""),
            job.get("country", ""),
            job.get("city", ""),
        ),
        "role_match": calculate_role_match(
            student.get("desired_roles", []),
            job.get("job_role", ""),
        ),
        "work_mode_match": calculate_work_mode_match(
            student.get("work_modes", []),
            job.get("work_mode", ""),
        ),
        "verified_score_match": calculate_verified_score_match(
            student.get("verified_scores", {}),
            job.get("required_verified_scores", {}),
        ),
    }

    weights = {
        "skill_match": 0.30,
        "education_match": 0.10,
        "experience_match": 0.15,
        "location_match": 0.10,
        "role_match": 0.15,
        "work_mode_match": 0.10,
        "verified_score_match": 0.10,
    }

    match_score = sum(
        signals[name] * weights[name]
        for name in signals
    )

    return {
        "student_id": student["student_id"],
        "job_id": job["job_id"],
        "match_score": round(match_score, 4),
        "signals": signals,
        "model_version": MODEL_VERSION,
    }