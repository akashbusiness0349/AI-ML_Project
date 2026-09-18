"""
Task 07 — Cold Start Ranking

Uses the trained model artifact for ranking.
Includes explicit epsilon-greedy exploration and explainable scores.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "active_model.json"


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def load_model() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Active model not found: {MODEL_PATH}. "
            "Run python run_training.py first."
        )

    with MODEL_PATH.open("r", encoding="utf-8") as f:
        model = json.load(f)

    required = {"weights", "bias", "feature_names"}

    missing = required - set(model)

    if missing:
        raise ValueError(
            f"Invalid model artifact. Missing fields: {sorted(missing)}"
        )

    return model


def candidate_features(
    candidate: dict[str, Any],
    job: dict[str, Any],
) -> dict[str, float]:
    candidate_skills = {
        normalize(skill)
        for skill in candidate.get("skills", [])
        if normalize(skill)
    }

    job_skills = {
        normalize(skill)
        for skill in job.get("skills", [])
        if normalize(skill)
    }

    skill_overlap = (
        len(candidate_skills & job_skills) / len(job_skills)
        if job_skills
        else 0.0
    )

    location_match = float(
        normalize(candidate.get("location"))
        == normalize(job.get("location"))
    )

    candidate_level = normalize(
        candidate.get("experience_level")
        or candidate.get("experience")
    )

    job_level = normalize(job.get("experience_level"))

    experience_match = float(
        candidate_level != ""
        and job_level != ""
        and candidate_level == job_level
    )

    popularity = float(job.get("popularity", 0) or 0)

    job_popularity = min(max(popularity / 100.0, 0.0), 1.0)

    return {
        "skill_overlap": skill_overlap,
        "location_match": location_match,
        "experience_match": experience_match,
        "job_popularity": job_popularity,
    }


def sigmoid(value: float) -> float:
    value = max(min(value, 35.0), -35.0)
    return 1.0 / (1.0 + math.exp(-value))


def model_score(
    candidate: dict[str, Any],
    job: dict[str, Any],
    model: dict[str, Any],
) -> tuple[float, dict[str, float]]:
    features = candidate_features(candidate, job)

    contributions: dict[str, float] = {}

    for feature_name, weight in zip(
        model["feature_names"],
        model["weights"],
    ):
        contributions[feature_name] = (
            float(weight) * features.get(feature_name, 0.0)
        )

    raw_score = float(model["bias"]) + sum(contributions.values())

    probability = sigmoid(raw_score)

    return probability, contributions


def stable_random(candidate_id: str, job_id: str) -> float:
    """
    Deterministic pseudo-random value.

    Deterministic exploration is useful for reproducible offline tests.
    The live API can use a fresh session seed for randomized assignment.
    """

    value = f"{candidate_id}:{job_id}".encode("utf-8")

    digest = hashlib.sha256(value).hexdigest()

    integer = int(digest[:16], 16)

    return integer / float(16**16 - 1)


def rank_candidate(
    candidate: dict[str, Any],
    jobs: list[dict[str, Any]],
    model: dict[str, Any] | None = None,
    top_k: int = 5,
    epsilon: float = 0.10,
) -> list[dict[str, Any]]:
    """
    Rank jobs for a cold-start candidate.

    epsilon:
        Exploration probability.

    With probability epsilon, a job receives an exploration boost.
    Otherwise the trained model score is used.

    The exploration decision is deterministic for reproducible offline runs.
    """

    if model is None:
        model = load_model()

    ranked: list[dict[str, Any]] = []

    for job in jobs:
        score, contributions = model_score(
            candidate,
            job,
            model,
        )

        exploration_value = stable_random(
            str(candidate.get("candidate_id", "")),
            str(job.get("job_id", "")),
        )

        explored = exploration_value < epsilon

        final_score = score

        if explored:
            # Explicit exploration boost.
            # The original model score remains visible.
            final_score += 0.05

        ranked.append(
            {
                "job_id": job.get("job_id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "score": round(final_score, 8),
                "model_probability": round(score, 8),
                "exploration": explored,
                "exploration_probability": epsilon,
                "feature_contributions": {
                    key: round(value, 8)
                    for key, value in contributions.items()
                },
            }
        )

    ranked.sort(
        key=lambda item: (
            item["score"],
            item["job_id"],
        ),
        reverse=True,
    )

    return ranked[:top_k]


def explain_recommendation(
    recommendation: dict[str, Any],
) -> list[str]:
    contributions = recommendation.get(
        "feature_contributions",
        {},
    )

    explanations: list[str] = []

    ordered = sorted(
        contributions.items(),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )

    for feature, contribution in ordered:
        if abs(float(contribution)) < 0.001:
            continue

        if feature == "skill_overlap":
            text = (
                "Strong skill overlap with the candidate profile."
                if contribution > 0
                else
                "Limited skill overlap with the candidate profile."
            )

        elif feature == "location_match":
            text = (
                "Candidate and job locations match."
                if contribution > 0
                else
                "Candidate and job locations do not match."
            )

        elif feature == "experience_match":
            text = (
                "Experience level matches the job requirement."
                if contribution > 0
                else
                "Experience level does not match the job requirement."
            )

        elif feature == "job_popularity":
            text = (
                "Job popularity contributes to the ranking."
                if contribution > 0
                else
                "Job popularity reduces the model score."
            )

        else:
            text = f"{feature} contributed to the ranking."

        explanations.append(text)

    if recommendation.get("exploration"):
        explanations.append(
            "This recommendation received an exploration boost "
            "to collect additional onboarding feedback."
        )

    return explanations


# Backward-compatible alias for older runners.
rank = rank_candidate