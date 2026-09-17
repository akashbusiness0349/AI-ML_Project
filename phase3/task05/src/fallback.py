"""
Safe degradation behavior for model unavailability.
"""

from typing import Any, Dict


def safe_model_unavailable_response(
    request_id: str,
) -> Dict[str, Any]:
    return {
        "request_id": request_id,
        "status": "degraded",
        "error_code": "MODEL_UNAVAILABLE",
        "model_available": False,
        "decision": None,
        "score": None,
        "recommendation": "NO_RECOMMENDATION",
        "explanation": (
            "The intelligence model is unavailable. "
            "No prediction or fabricated score was generated."
        ),
    }