"""
PlaceMux Phase 2 — Task 3
Search & Discovery Ranking Engine
"""

from typing import Dict, List


MODEL_VERSION = "v1"


def calculate_match_score(student: dict, job: dict) -> float:
    """
    Calculate a deterministic v1 match score using the signals
    established in Phase 2 Tasks 1 and 2.
    """

    student_skills = {
        skill.lower()
        for skill in student.get("skills", [])
    }

    required_skills = {
        skill.lower()
        for skill in job.get("required_skills", [])
    }

    preferred_skills = {
        skill.lower()
        for skill in job.get("preferred_skills", [])
    }

    # Required skill match
    if required_skills:
        required_match = (
            len(student_skills & required_skills)
            / len(required_skills)
        )
    else:
        required_match = 1.0

    # Preferred skill match
    if preferred_skills:
        preferred_match = (
            len(student_skills & preferred_skills)
            / len(preferred_skills)
        )
    else:
        preferred_match = 1.0

    # Role match
    desired_roles = {
        role.lower()
        for role in student.get("desired_roles", [])
    }

    job_role = job.get("job_role", "").lower()

    role_match = (
        1.0
        if job_role in desired_roles
        else 0.0
    )

    # Work mode match
    student_work_modes = {
        mode.lower()
        for mode in student.get("work_modes", [])
    }

    job_work_mode = job.get("work_mode", "").lower()

    work_mode_match = (
        1.0
        if job_work_mode in student_work_modes
        else 0.0
    )

    # Experience match
    student_experience = float(
        student.get("years_experience", 0)
    )

    required_experience = float(
        job.get("minimum_years_experience", 0)
    )

    experience_match = (
        1.0
        if student_experience >= required_experience
        else (
            student_experience / required_experience
            if required_experience > 0
            else 1.0
        )
    )

    # Verified score match
    verified_scores = student.get(
        "verified_scores",
        {}
    )

    required_verified_scores = job.get(
        "required_verified_scores",
        {}
    )

    verified_results = []

    for skill, threshold in required_verified_scores.items():
        student_score = verified_scores.get(skill, 0)

        if threshold > 0:
            verified_results.append(
                min(student_score / threshold, 1.0)
            )
        else:
            verified_results.append(1.0)

    verified_score_match = (
        sum(verified_results) / len(verified_results)
        if verified_results
        else 1.0
    )

    # Final weighted score
    final_score = (
        0.30 * required_match
        + 0.10 * preferred_match
        + 0.20 * role_match
        + 0.10 * work_mode_match
        + 0.15 * experience_match
        + 0.15 * verified_score_match
    )

    return round(final_score, 4)


def rank_jobs_for_student(
    student: dict,
    jobs: List[dict]
) -> List[dict]:
    """
    Rank multiple jobs for one student.
    """

    ranked_jobs = []

    for job in jobs:
        score = calculate_match_score(
            student,
            job
        )

        ranked_jobs.append(
            {
                "job_id": job["job_id"],
                "job_role": job["job_role"],
                "company": job.get("company", "Unknown"),
                "match_score": score,
                "match_score_percentage": round(
                    score * 100,
                    2
                ),
                "model_version": MODEL_VERSION,
            }
        )

    ranked_jobs.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    for rank, item in enumerate(
        ranked_jobs,
        start=1
    ):
        item["rank"] = rank

    return ranked_jobs


def rank_candidates_for_job(
    job: dict,
    students: List[dict]
) -> List[dict]:
    """
    Rank multiple candidates for one job.
    """

    ranked_candidates = []

    for student in students:
        score = calculate_match_score(
            student,
            job
        )

        ranked_candidates.append(
            {
                "student_id": student["student_id"],
                "candidate_name": student.get(
                    "name",
                    student["student_id"]
                ),
                "match_score": score,
                "match_score_percentage": round(
                    score * 100,
                    2
                ),
                "model_version": MODEL_VERSION,
            }
        )

    ranked_candidates.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    for rank, item in enumerate(
        ranked_candidates,
        start=1
    ):
        item["rank"] = rank

    return ranked_candidates