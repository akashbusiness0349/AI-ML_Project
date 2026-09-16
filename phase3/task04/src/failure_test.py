from __future__ import annotations

import os
from typing import Any, Dict

from .inference import (
    ModelUnavailableError,
    SkillMatchingModel,
    safe_model_unavailable_response,
)


def run_failure_path_test() -> Dict[str, Any]:
    """
    Demonstrates the safe MODEL_UNAVAILABLE path.

    This test changes the environment only for this process and restores
    the previous value before returning.
    """

    previous_value = os.environ.get(
        "TASK04_MODEL_AVAILABLE"
    )

    os.environ["TASK04_MODEL_AVAILABLE"] = "false"

    try:
        model = SkillMatchingModel(
            work_units=0
        )

        try:
            model.predict(
                request_id="task04_failure_001",
                student_id="failure_student",
                candidate_skills=["python"],
                required_skills=["python"],
            )

            return {
                "test_status": "FAILED",
                "expected": "MODEL_UNAVAILABLE",
                "observed": "prediction_returned",
            }

        except ModelUnavailableError as exc:
            fallback = safe_model_unavailable_response(
                request_id="task04_failure_001",
                student_id="failure_student",
            )

            return {
                "test_status": "PASSED",
                "error_code": str(exc),
                "fallback_response": fallback,
                "assertions": {
                    "no_fabricated_score": (
                        fallback["score"] is None
                    ),
                    "no_recommendation": (
                        fallback["decision"]
                        == "NO_RECOMMENDATION"
                    ),
                    "model_marked_unavailable": (
                        fallback["model_available"] is False
                    ),
                },
            }

    finally:
        if previous_value is None:
            os.environ.pop(
                "TASK04_MODEL_AVAILABLE",
                None,
            )
        else:
            os.environ["TASK04_MODEL_AVAILABLE"] = previous_value