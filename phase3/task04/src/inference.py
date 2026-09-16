from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence


class ModelUnavailableError(RuntimeError):
    """Raised when the inference model is unavailable."""


@dataclass(frozen=True)
class InferenceResult:
    request_id: str
    student_id: str
    score: float
    decision: str
    matched_skills: List[str]
    missing_skills: List[str]
    model_available: bool
    explanation: Dict[str, Any]


class SkillMatchingModel:
    """
    Deterministic skill-matching inference model.

    Uses integer bitmasks for efficient skill membership operations.

    Environment variables:

    TASK04_MODEL_AVAILABLE
        true/false. Used to demonstrate MODEL_UNAVAILABLE safely.

    TASK04_WORK_UNITS
        Number of deterministic CPU operations performed per inference.
    """

    DEFAULT_SKILLS = (
        "python",
        "sql",
        "machine learning",
        "pandas",
        "java",
        "spring",
        "git",
        "react",
        "javascript",
        "typescript",
        "html",
        "css",
        "fastapi",
        "docker",
        "aws",
        "kubernetes",
        "pytorch",
        "numpy",
        "deep learning",
        "postgresql",
        "analytics",
        "c++",
        "data structures",
        "algorithms",
        "node.js",
        "mongodb",
        "express",
        "tensorflow",
    )

    def __init__(
        self,
        skills: Optional[Sequence[str]] = None,
        work_units: Optional[int] = None,
    ) -> None:

        selected_skills = skills or self.DEFAULT_SKILLS

        normalized_skills = sorted(
            {
                self.normalize_skill(skill)
                for skill in selected_skills
                if self.normalize_skill(skill)
            }
        )

        self.skill_to_bit: Dict[str, int] = {
            skill: index
            for index, skill in enumerate(normalized_skills)
        }

        self.available = self._read_availability()

        if work_units is None:
            raw_work_units = os.getenv(
                "TASK04_WORK_UNITS",
                "5000",
            )

            try:
                work_units = int(raw_work_units)
            except ValueError:
                work_units = 5000

        self.work_units = max(0, work_units)

    @staticmethod
    def normalize_skill(skill: Any) -> str:
        return str(skill).strip().lower()

    @staticmethod
    def _read_availability() -> bool:
        value = os.getenv(
            "TASK04_MODEL_AVAILABLE",
            "true",
        ).strip().lower()

        return value not in {
            "0",
            "false",
            "no",
            "off",
        }

    def refresh_availability(self) -> None:
        self.available = self._read_availability()

    def _skills_to_mask(
        self,
        skills: Iterable[str],
    ) -> int:

        mask = 0

        for skill in skills:
            normalized = self.normalize_skill(skill)

            bit = self.skill_to_bit.get(normalized)

            if bit is not None:
                mask |= 1 << bit

        return mask

    def _deterministic_cpu_work(
        self,
        candidate_mask: int,
        required_mask: int,
    ) -> str:

        if self.work_units <= 0:
            return ""

        candidate_bytes = candidate_mask.to_bytes(
            max(
                1,
                (candidate_mask.bit_length() + 7) // 8,
            ),
            "little",
        )

        required_bytes = required_mask.to_bytes(
            max(
                1,
                (required_mask.bit_length() + 7) // 8,
            ),
            "little",
        )

        digest = hashlib.sha256(
            candidate_bytes + required_bytes
        ).digest()

        for index in range(self.work_units):
            digest = hashlib.sha256(
                digest + index.to_bytes(
                    4,
                    "little",
                )
            ).digest()

        return digest.hex()[:16]

    def predict(
        self,
        request_id: str,
        student_id: str,
        candidate_skills: Sequence[str],
        required_skills: Sequence[str],
    ) -> InferenceResult:

        self.refresh_availability()

        if not self.available:
            raise ModelUnavailableError(
                "MODEL_UNAVAILABLE"
            )

        candidate: set[str] = {
            self.normalize_skill(skill)
            for skill in candidate_skills
            if self.normalize_skill(skill)
        }

        required: set[str] = {
            self.normalize_skill(skill)
            for skill in required_skills
            if self.normalize_skill(skill)
        }

        candidate_mask = self._skills_to_mask(
            candidate
        )

        required_mask = self._skills_to_mask(
            required
        )

        matched = sorted(
            candidate.intersection(required)
        )

        missing = sorted(
            required.difference(candidate)
        )

        if not required:
            score = 0.0
        else:
            score = len(matched) / len(required)

        decision = (
            "MATCH"
            if score >= 0.70
            else "NO_MATCH"
        )

        computation_token = self._deterministic_cpu_work(
            candidate_mask,
            required_mask,
        )

        explanation = {
            "method": "skill_overlap",
            "required_skill_count": len(required),
            "matched_skill_count": len(matched),
            "missing_skill_count": len(missing),
            "matched_skills": matched,
            "missing_skills": missing,
            "threshold": 0.70,
            "candidate_mask": candidate_mask,
            "required_mask": required_mask,
            "computation_token": computation_token,
        }

        return InferenceResult(
            request_id=request_id,
            student_id=student_id,
            score=round(score, 6),
            decision=decision,
            matched_skills=matched,
            missing_skills=missing,
            model_available=True,
            explanation=explanation,
        )


def safe_model_unavailable_response(
    request_id: str,
    student_id: str,
) -> Dict[str, Any]:

    return {
        "request_id": request_id,
        "student_id": student_id,
        "status": "MODEL_UNAVAILABLE",
        "model_available": False,
        "score": None,
        "decision": "NO_RECOMMENDATION",
        "recommendation": (
            "Retry inference when the model service "
            "is available."
        ),
        "explanation": {
            "reason": (
                "The inference model is unavailable."
            ),
            "fallback": "NO_RECOMMENDATION",
        },
    }