from __future__ import annotations

from typing import Any, Dict


def safe_model_unavailable_response(
    request_id: str,
) -> Dict[str, Any]:
    return {
        "status": "degraded",
        "error_code": "MODEL_UNAVAILABLE",
        "model_available": False,
        "request_id": request_id,
        "recommendation": "NO_RANKING",
        "results": [],
        "explanation": (
            "The ranking model is unavailable. No fabricated ranking "
            "or recommendation was returned."
        ),
    }


def validate_fallback(
    response: Dict[str, Any],
) -> bool:
    return (
        response.get("status") == "degraded"
        and response.get("error_code") == "MODEL_UNAVAILABLE"
        and response.get("model_available") is False
        and response.get("recommendation") == "NO_RANKING"
        and response.get("results") == []
    )