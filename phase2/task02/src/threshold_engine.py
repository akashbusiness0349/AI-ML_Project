"""
PlaceMux Phase 2 — Task 2
Job Posting with Skill Thresholds

Converts job skill thresholds into match vectors and validates
student competency against those thresholds.
"""

from typing import Dict, Any


MODEL_VERSION = "v1"


VALID_COMPETENCY_LEVELS = {
    "beginner": (0, 49),
    "intermediate": (50, 69),
    "advanced": (70, 84),
    "expert": (85, 100),
}


def validate_threshold(threshold: float) -> None:
    """Validate that a skill threshold is between 0 and 100."""

    if not isinstance(threshold, (int, float)):
        raise TypeError("Threshold must be numeric.")

    if threshold < 0 or threshold > 100:
        raise ValueError("Threshold must be between 0 and 100.")


def competency_from_score(score: float) -> str:
    """Map a competency score to a competency level."""

    if not isinstance(score, (int, float)):
        raise TypeError("Competency score must be numeric.")

    if score < 0 or score > 100:
        raise ValueError("Competency score must be between 0 and 100.")

    for level, (minimum, maximum) in VALID_COMPETENCY_LEVELS.items():
        if minimum <= score <= maximum:
            return level

    raise ValueError("Unable to determine competency level.")


def validate_job_thresholds(
    skill_thresholds: Dict[str, float],
) -> Dict[str, Any]:
    """
    Validate all skill thresholds in a job posting.

    Returns validated threshold metadata.
    """

    if not isinstance(skill_thresholds, dict):
        raise TypeError("skill_thresholds must be a dictionary.")

    if not skill_thresholds:
        raise ValueError("At least one skill threshold is required.")

    validated = {}

    for skill, threshold in skill_thresholds.items():
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("Skill names must be non-empty strings.")

        validate_threshold(threshold)

        validated[skill.strip()] = float(threshold)

    return validated


def generate_match_vector(
    student_scores: Dict[str, float],
    job_thresholds: Dict[str, float],
) -> Dict[str, int]:
    """
    Generate a binary match vector.

    1 = student meets or exceeds job threshold
    0 = student is below job threshold
    """

    validated_thresholds = validate_job_thresholds(job_thresholds)

    match_vector = {}

    for skill, threshold in validated_thresholds.items():

        student_score = student_scores.get(skill, 0)

        if not isinstance(student_score, (int, float)):
            raise TypeError(
                f"Student score for '{skill}' must be numeric."
            )

        if student_score < 0 or student_score > 100:
            raise ValueError(
                f"Student score for '{skill}' must be between 0 and 100."
            )

        match_vector[skill] = int(student_score >= threshold)

    return match_vector


def generate_detailed_match_vector(
    student_scores: Dict[str, float],
    job_thresholds: Dict[str, float],
) -> Dict[str, Dict[str, Any]]:
    """
    Generate detailed threshold-to-competency mapping.
    """

    validated_thresholds = validate_job_thresholds(job_thresholds)

    result = {}

    for skill, threshold in validated_thresholds.items():

        student_score = student_scores.get(skill, 0)

        if student_score < 0 or student_score > 100:
            raise ValueError(
                f"Student score for '{skill}' must be between 0 and 100."
            )

        result[skill] = {
            "student_score": student_score,
            "required_threshold": threshold,
            "student_competency": competency_from_score(
                student_score
            ),
            "threshold_competency": competency_from_score(
                threshold
            ),
            "threshold_met": student_score >= threshold,
            "match_value": int(student_score >= threshold),
        }

    return result


def calculate_vector_score(
    match_vector: Dict[str, int],
) -> float:
    """Calculate percentage of required thresholds satisfied."""

    if not match_vector:
        return 0.0

    matched = sum(match_vector.values())
    total = len(match_vector)

    return round(matched / total, 4)


def build_threshold_match(
    student_id: str,
    job_id: str,
    student_scores: Dict[str, float],
    job_thresholds: Dict[str, float],
) -> Dict[str, Any]:
    """
    Build the complete Task 2 threshold matching result.
    """

    match_vector = generate_match_vector(
        student_scores,
        job_thresholds,
    )

    detailed_vector = generate_detailed_match_vector(
        student_scores,
        job_thresholds,
    )

    vector_score = calculate_vector_score(match_vector)

    return {
        "student_id": student_id,
        "job_id": job_id,
        "match_vector": match_vector,
        "vector_score": vector_score,
        "vector_score_percentage": round(
            vector_score * 100,
            2,
        ),
        "threshold_mapping": detailed_vector,
        "model_version": MODEL_VERSION,
    }