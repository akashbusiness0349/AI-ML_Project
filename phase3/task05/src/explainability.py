"""
Explainability utilities for Task 05.
"""


def build_explanation(result) -> dict:
    return {
        "method": "skill_overlap",
        "decision": result.decision,
        "score": result.score,
        "threshold": result.threshold,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "plain_english_reason": result.explanation,
    }