from __future__ import annotations

from typing import Dict


def explain_recommendation(
    candidate: Dict,
    recommendation: Dict,
) -> str:
    matched = recommendation.get(
        "matched_skills",
        [],
    )

    if matched:
        skills = ", ".join(matched)

        return (
            f"This job was recommended because your profile "
            f"matches these skills: {skills}. "
            f"The ranking also considered location, experience "
            f"level, and job popularity."
        )

    return (
        "This job was recommended using the cold-start "
        "profile signals available for the new account, "
        "together with the job popularity prior."
    )


def explanation_record(
    candidate: Dict,
    recommendation: Dict,
) -> Dict:
    return {
        "candidate_id": candidate["candidate_id"],
        "job_id": recommendation["job_id"],
        "model_version": recommendation.get(
            "model_version"
        ),
        "reason": explain_recommendation(
            candidate,
            recommendation,
        ),
        "signals": {
            "matched_skills": recommendation.get(
                "matched_skills",
                [],
            ),
            "skill_score": recommendation.get(
                "skill_score",
                0.0,
            ),
            "location_score": recommendation.get(
                "location_score",
                0.0,
            ),
            "experience_score": recommendation.get(
                "experience_score",
                0.0,
            ),
            "popularity": recommendation.get(
                "popularity",
                0.0,
            ),
        },
    }