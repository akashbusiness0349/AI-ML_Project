from __future__ import annotations

import json

from src.data import (
    load_candidates,
    load_jobs,
    save_json,
)
from src.fallback import (
    rank_with_fallback,
)
from src.ranker import load_model


def main() -> None:
    candidates = load_candidates()
    jobs = load_jobs()

    candidate = candidates[0]

    model = load_model(
        "models/task11_ltr_model.joblib"
    )

    normal = rank_with_fallback(
        model,
        candidate,
        jobs,
    )

    failure = rank_with_fallback(
        None,
        candidate,
        jobs,
    )

    fallback_pass = (
        normal["fallback_used"] is False
        and failure["fallback_used"] is True
        and failure["variant"]
        == "heuristic_fallback"
        and len(
            failure["ranked_jobs"]
        ) == len(jobs)
    )

    output = {
        "task": "Phase 3 Task 11",
        "status": (
            "PASS"
            if fallback_pass
            else "FAIL"
        ),
        "normal_path": {
            "variant": normal["variant"],
            "fallback_used": normal[
                "fallback_used"
            ],
            "top_job": (
                normal["ranked_jobs"][0]
                if normal["ranked_jobs"]
                else None
            ),
        },
        "failure_path": {
            "variant": failure["variant"],
            "fallback_used": failure[
                "fallback_used"
            ],
            "top_job": (
                failure["ranked_jobs"][0]
                if failure["ranked_jobs"]
                else None
            ),
        },
        "fallback_test": (
            "PASS"
            if fallback_pass
            else "FAIL"
        ),
    }

    save_json(
        output,
        "logs/failure_test.json",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()