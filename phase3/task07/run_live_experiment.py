from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.activation_metrics import (
    compare_experiment_groups,
)
from src.recommender import recommend


ROOT = Path(__file__).resolve().parent


def load(name: str):
    with (ROOT / "data" / name).open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def timestamp():
    return datetime.now(
        timezone.utc
    ).isoformat()


def main():
    candidates = load(
        "candidates.json"
    )

    jobs = load(
        "jobs.json"
    )

    random.seed(20260918)

    events = []

    for candidate in candidates:
        session_id = (
            f"exp_{uuid.uuid4().hex[:10]}"
        )

        group = (
            "treatment"
            if random.random() < 0.5
            else "control"
        )

        if group == "control":
            from src.baseline import (
                rank_popularity,
            )

            recommendations = rank_popularity(
                jobs
            )
        else:
            result = recommend(
                candidate,
                jobs,
                session_id=session_id,
                epsilon=0.20,
                model_available=True,
            )

            recommendations = result[
                "recommendations"
            ]

        for recommendation in recommendations:
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "candidate_id": candidate[
                        "candidate_id"
                    ],
                    "job_id": recommendation[
                        "job_id"
                    ],
                    "event_type": "impression",
                    "position": recommendation[
                        "position"
                    ],
                    "model_version": recommendation[
                        "model_version"
                    ],
                    "session_id": session_id,
                    "experiment_group": group,
                    "timestamp": timestamp(),
                    "source_type": "experiment_capture",
                }
            )

        # Experiment capture simulates user action only
        # for local validation. It must not be described
        # as production-user behavior.
        top = recommendations[0]

        if group == "treatment":
            action = "click"
        else:
            action = "click" if (
                random.random() < 0.40
            ) else "skip"

        if action == "click":
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "candidate_id": candidate[
                        "candidate_id"
                    ],
                    "job_id": top["job_id"],
                    "event_type": "click",
                    "position": top["position"],
                    "model_version": top[
                        "model_version"
                    ],
                    "session_id": session_id,
                    "experiment_group": group,
                    "timestamp": timestamp(),
                    "source_type": "experiment_capture",
                }
            )

    output = (
        ROOT
        / "logs"
        / "online_experiment_events.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            events,
            handle,
            indent=2,
        )

    metrics = compare_experiment_groups(
        events
    )

    metrics_path = (
        ROOT
        / "logs"
        / "online_experiment_metrics.json"
    )

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            {
                "experiment_type": (
                    "randomized_local_capture"
                ),
                "production": False,
                "production_lift_claimed": False,
                "metrics": metrics,
            },
            handle,
            indent=2,
        )

    print(
        "\n"
        "============================================\n"
        "TASK 07 — ONLINE EXPERIMENT CAPTURE\n"
        "============================================"
    )

    print(
        f"Captured events : {len(events)}"
    )

    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "This is a randomized local experiment "
        "capture, not a production-user A/B test."
    )

    print(
        "Production lift is NOT claimed."
    )


if __name__ == "__main__":
    main()