"""
Task 05 intelligence model.

The model implements deterministic skill-overlap matching using
integer bitmasks. This keeps the inference behavior explainable
and computationally efficient while allowing reproducible
load testing.

This is an experimental intelligence layer and is not represented
as a production ML model without further production validation.
"""

import hashlib
import os
import time
from dataclasses import dataclass
from typing import List


class ModelUnavailableError(RuntimeError):
    """Raised when the intelligence model is unavailable."""


@dataclass
class InferenceResult:
    score: float
    decision: str
    matched_skills: List[str]
    missing_skills: List[str]
    threshold: float
    explanation: str
    computation_token: str
    latency_ms: float
    model_available: bool


class SkillMatchingModel:
    def __init__(self) -> None:
        self.model_available = (
            os.getenv(
                "TASK05_MODEL_AVAILABLE",
                "true",
            ).lower()
            == "true"
        )

        self.threshold = float(
            os.getenv(
                "TASK05_MATCH_THRESHOLD",
                "0.7",
            )
        )

        self.work_units = int(
            os.getenv(
                "TASK05_WORK_UNITS",
                "5000",
            )
        )

        self.vocabulary: dict[str, int] = {}

    @staticmethod
    def normalize(values: List[str]) -> List[str]:
        return sorted(
            {
                str(value).strip().lower()
                for value in values
                if str(value).strip()
            }
        )

    def build_mask(self, skills: List[str]) -> int:
        mask = 0

        for skill in skills:
            if skill not in self.vocabulary:
                self.vocabulary[skill] = len(
                    self.vocabulary
                )

            mask |= 1 << self.vocabulary[skill]

        return mask

    def predict(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
    ) -> InferenceResult:

        if not self.model_available:
            raise ModelUnavailableError(
                "MODEL_UNAVAILABLE"
            )

        started = time.perf_counter()

        candidate = self.normalize(candidate_skills)
        required = self.normalize(required_skills)

        if not required:
            score = 0.0
            matched = []
            missing = []

        else:
            candidate_mask = self.build_mask(candidate)
            required_mask = self.build_mask(required)

            matched_mask = (
                candidate_mask & required_mask
            )

            matched = [
                skill
                for skill in required
                if (
                    matched_mask
                    & (1 << self.vocabulary[skill])
                )
            ]

            missing = [
                skill
                for skill in required
                if skill not in matched
            ]

            score = (
                len(matched) / len(required)
            )

        decision = (
            "MATCH"
            if score >= self.threshold
            else "NO_MATCH"
        )

        # Deterministic CPU work makes latency measurable
        # during sustained load without pretending to represent
        # a particular production hardware cost.
        digest = "|".join(
            candidate + required
        ).encode("utf-8")

        for _ in range(
            max(0, self.work_units)
        ):
            digest = hashlib.sha256(
                digest
            ).digest()

        computation_token = digest.hex()[:16]

        latency_ms = (
            time.perf_counter() - started
        ) * 1000.0

        if matched:
            explanation = (
                f"{len(matched)} of "
                f"{len(required)} required skills matched."
            )
        else:
            explanation = (
                "No required skills matched."
            )

        return InferenceResult(
            score=round(score, 6),
            decision=decision,
            matched_skills=matched,
            missing_skills=missing,
            threshold=self.threshold,
            explanation=explanation,
            computation_token=computation_token,
            latency_ms=round(latency_ms, 6),
            model_available=True,
        )