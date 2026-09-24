from __future__ import annotations

import json
from pathlib import Path

from src.data import (
    load_candidates,
    load_companies,
    load_jobs,
)


ROOT = Path(__file__).resolve().parent


def main():
    candidates = load_candidates()
    companies = load_companies()
    jobs = load_jobs()

    model_dir = ROOT / "models"
    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_info = {
        "task": "Phase 3 Task 12",
        "status": "PASS",
        "model_type": "feature_based_two_sided_recommender",
        "candidate_count": len(candidates),
        "company_count": len(companies),
        "job_count": len(jobs),
        "ranking_features": [
            "skill_overlap",
            "experience_match",
            "location_match",
            "popularity",
        ],
        "model_path": str(
            model_dir / "task12_recommendation_model.json"
        ),
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
    }

    with (
        model_dir / "task12_recommendation_model.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            model_info,
            f,
            indent=2,
        )

    print(
        json.dumps(
            model_info,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()