"""
PlaceMux Phase 2 — Task 4
Match Explainability Engine
"""

MODEL_VERSION = "v1"


def _normalise(values):
    return {
        str(value).strip().lower()
        for value in values
    }


def generate_match_explanation(student, job, match_score):
    """
    Generate a structured explanation connected to the
    actual student-job match.
    """

    student_skills = _normalise(
        student.get("skills", [])
    )

    required_skills = _normalise(
        job.get("required_skills", [])
    )

    preferred_skills = _normalise(
        job.get("preferred_skills", [])
    )

    matched_required = sorted(
        student_skills & required_skills
    )

    missing_required = sorted(
        required_skills - student_skills
    )

    matched_preferred = sorted(
        student_skills & preferred_skills
    )

    # ---------------------------------------------------------
    # EXPERIENCE
    # ---------------------------------------------------------

    student_experience = float(
        student.get("years_experience", 0)
    )

    required_experience = float(
        job.get("minimum_years_experience", 0)
    )

    experience_met = (
        student_experience >= required_experience
    )

    # ---------------------------------------------------------
    # ROLE
    # ---------------------------------------------------------

    desired_roles = _normalise(
        student.get("desired_roles", [])
    )

    job_role = str(
        job.get("job_role", "")
    ).strip().lower()

    role_match = job_role in desired_roles

    # ---------------------------------------------------------
    # WORK MODE
    # ---------------------------------------------------------

    student_work_modes = _normalise(
        student.get("work_modes", [])
    )

    job_work_mode = str(
        job.get("work_mode", "")
    ).strip().lower()

    work_mode_match = (
        job_work_mode in student_work_modes
    )

    # ---------------------------------------------------------
    # VERIFIED SCORES
    # ---------------------------------------------------------

    student_verified = student.get(
        "verified_scores",
        {}
    )

    required_verified = job.get(
        "required_verified_scores",
        {}
    )

    verified_results = []

    verified_passed = []
    verified_failed = []

    for skill, threshold in required_verified.items():

        student_score = float(
            student_verified.get(skill, 0)
        )

        threshold = float(threshold)

        if student_score >= threshold:
            verified_passed.append(skill)
        else:
            verified_failed.append(skill)

        if threshold > 0:
            verified_results.append(
                min(student_score / threshold, 1.0)
            )

    if verified_results:
        verified_score_match = (
            sum(verified_results)
            / len(verified_results)
        )
    else:
        verified_score_match = 1.0

    # ---------------------------------------------------------
    # EXPLANATION FACTORS
    # ---------------------------------------------------------

    positive_factors = []
    negative_factors = []

    if matched_required:
        positive_factors.append(
            f"Matched required skills: "
            f"{', '.join(matched_required)}."
        )

    if matched_preferred:
        positive_factors.append(
            f"Matched preferred skills: "
            f"{', '.join(matched_preferred)}."
        )

    if experience_met:
        positive_factors.append(
            f"Experience requirement met "
            f"({student_experience:.1f} years vs "
            f"{required_experience:.1f} required)."
        )
    else:
        negative_factors.append(
            f"Experience requirement not met "
            f"({student_experience:.1f} years vs "
            f"{required_experience:.1f} required)."
        )

    if role_match:
        positive_factors.append(
            f"Desired role matches job role: "
            f"{job.get('job_role')}."
        )
    else:
        negative_factors.append(
            f"Job role '{job.get('job_role')}' "
            f"is not in the student's desired roles."
        )

    if work_mode_match:
        positive_factors.append(
            f"Work mode preference matches: "
            f"{job.get('work_mode')}."
        )
    else:
        negative_factors.append(
            f"Work mode '{job.get('work_mode')}' "
            f"does not match the student's preferences."
        )

    if verified_passed:
        positive_factors.append(
            f"Verified competency thresholds passed: "
            f"{', '.join(verified_passed)}."
        )

    if verified_failed:
        negative_factors.append(
            f"Verified competency thresholds not met: "
            f"{', '.join(verified_failed)}."
        )

    if missing_required:
        negative_factors.append(
            f"Missing required skills: "
            f"{', '.join(missing_required)}."
        )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    if match_score >= 0.80:
        strength = "Strong"
    elif match_score >= 0.60:
        strength = "Moderate"
    else:
        strength = "Weak"

    summary = (
        f"{strength} match with a "
        f"{match_score * 100:.2f}% match score. "
        f"The score is supported by "
        f"{len(matched_required)} matched required skill(s), "
        f"experience compatibility, role compatibility, "
        f"work-mode compatibility, and verified competency signals."
    )

    return {
        "student_id": student["student_id"],
        "job_id": job["job_id"],
        "match_score": round(match_score, 4),
        "match_score_percentage": round(
            match_score * 100,
            2
        ),
        "explanation": {
            "summary": summary,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "skill_evidence": {
                "matched_required_skills": matched_required,
                "missing_required_skills": missing_required,
                "matched_preferred_skills": matched_preferred
            },
            "experience_evidence": {
                "student_years": student_experience,
                "required_years": required_experience,
                "requirement_met": experience_met
            },
            "role_evidence": {
                "student_desired_roles": student.get(
                    "desired_roles",
                    []
                ),
                "job_role": job.get("job_role"),
                "match": role_match
            },
            "work_mode_evidence": {
                "student_work_modes": student.get(
                    "work_modes",
                    []
                ),
                "job_work_mode": job.get(
                    "work_mode"
                ),
                "match": work_mode_match
            },
            "verified_score_evidence": {
                "passed": verified_passed,
                "failed": verified_failed,
                "score_match": round(
                    verified_score_match,
                    4
                )
            }
        },
        "model_version": MODEL_VERSION
    }