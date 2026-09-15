from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


RECOMMENDATION_THRESHOLD = 0.70


@dataclass(frozen=True)
class Request:
    request_id: str
    candidate_skills: tuple[str, ...]
    job_skills: tuple[str, ...]
    experience_years: float
    required_experience_years: float


def _normalize(skills: Iterable[str]) -> list[str]:
    return [
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    ]


def build_request(record: dict) -> Request:
    return Request(
        request_id=str(record["request_id"]),
        candidate_skills=tuple(
            _normalize(record["candidate_skills"])
        ),
        job_skills=tuple(
            _normalize(record["job_skills"])
        ),
        experience_years=float(record["experience_years"]),
        required_experience_years=float(
            record["required_experience_years"]
        ),
    )


def _score(
    candidate_skills: Iterable[str],
    job_skills: Iterable[str],
    experience_years: float,
    required_experience_years: float,
) -> tuple[float, list[str]]:

    candidate = list(candidate_skills)
    job = list(job_skills)

    if not job:
        return 0.0, []

    matched = []

    for skill in job:
        for candidate_skill in candidate:
            if skill == candidate_skill:
                if skill not in matched:
                    matched.append(skill)
                break

    job_unique = len(set(job))

    skill_score = (
        len(matched) / job_unique
        if job_unique
        else 0.0
    )

    experience_score = (
        1.0
        if experience_years >= required_experience_years
        else max(
            0.0,
            experience_years
            / max(required_experience_years, 1.0),
        )
    )

    score = (
        0.75 * skill_score
        + 0.25 * experience_score
    )

    return score, matched


def baseline_inference(request: Request) -> dict:

    score, matched = _score(
        request.candidate_skills,
        request.job_skills,
        request.experience_years,
        request.required_experience_years,
    )

    return {
        "status": "OK",
        "recommendation": score >= RECOMMENDATION_THRESHOLD,
        "score": score,
        "matched_skills": matched,
    }


class OptimizedInference:

    def __init__(self, vocabulary: Iterable[str]):

        unique = sorted(
            {
                str(skill).strip().lower()
                for skill in vocabulary
                if str(skill).strip()
            }
        )

        self.index = {
            skill: index
            for index, skill in enumerate(unique)
        }

        self.skill_by_index = unique

    def _to_mask(self, skills: Iterable[str]) -> int:

        mask = 0

        for skill in skills:

            index = self.index.get(skill)

            if index is not None:
                mask |= 1 << index

        return mask

    def infer(self, request: Request) -> dict:

        try:

            candidate_mask = self._to_mask(
                request.candidate_skills
            )

            job_mask = self._to_mask(
                request.job_skills
            )

            if job_mask == 0:

                score = 0.0
                matched = []

            else:

                overlap = candidate_mask & job_mask

                matched = []

                while overlap:

                    lowest_bit = overlap & -overlap

                    index = (
                        lowest_bit.bit_length() - 1
                    )

                    matched.append(
                        self.skill_by_index[index]
                    )

                    overlap ^= lowest_bit

                job_unique_count = job_mask.bit_count()

                skill_score = (
                    len(matched)
                    / job_unique_count
                )

                experience_score = (
                    1.0
                    if (
                        request.experience_years
                        >= request.required_experience_years
                    )
                    else max(
                        0.0,
                        request.experience_years
                        / max(
                            request.required_experience_years,
                            1.0,
                        ),
                    )
                )

                score = (
                    0.75 * skill_score
                    + 0.25 * experience_score
                )

            return {
                "status": "OK",
                "recommendation": (
                    score >= RECOMMENDATION_THRESHOLD
                ),
                "score": score,
                "matched_skills": matched,
            }

        except Exception:

            return {
                "status": "MODEL_UNAVAILABLE",
                "recommendation": None,
                "score": None,
                "matched_skills": [],
                "fallback": "return_no_recommendation",
                "safe": True,
            }