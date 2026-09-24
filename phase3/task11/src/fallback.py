from __future__ import annotations

from typing import Mapping

from .baseline import rank_jobs_baseline
from .ranker import rank_jobs_ltr


def rank_with_fallback(
    model,
    candidate: Mapping,
    jobs: list[Mapping],
) -> dict:
    try:
        if model is None:
            raise RuntimeError(
                "LTR model unavailable"
            )

        ranked = rank_jobs_ltr(
            model,
            candidate,
            jobs,
        )

        return {
            "variant": "ltr",
            "ranked_jobs": ranked,
            "fallback_used": False,
            "status": "PASS",
        }

    except Exception as exc:
        ranked = rank_jobs_baseline(
            candidate,
            jobs,
        )

        return {
            "variant": "heuristic_fallback",
            "ranked_jobs": ranked,
            "fallback_used": True,
            "fallback_reason": str(exc),
            "status": "PASS",
        }