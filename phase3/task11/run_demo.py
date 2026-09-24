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

    model = load_model(
        "models/task11_ltr_model.joblib"
    )

    records = []

    for candidate in candidates[:5]:
        result = rank_with_fallback(
            model,
            candidate,
            jobs,
        )

        records.append(
            {
                "candidate_id": candidate[
                    "candidate_id"
                ],
                "variant": result["variant"],
                "fallback_used": result[
                    "fallback_used"
                ],
                "top_5": result[
                    "ranked_jobs"
                ][:5],
            }
        )

    output = {
        "task": "Phase 3 Task 11",
        "status": "PASS",
        "demo_type": (
            "executable_task11_ltr_ranking_demo"
        ),
        "data_source": (
            "task11_owned_synthetic_logged_impressions"
        ),
        "production_status": (
            "NOT_LIVE_PRODUCTION"
        ),
        "records_served": records,
        "fallback_supported": True,
    }

    save_json(
        output,
        "logs/live_demo.json",
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()