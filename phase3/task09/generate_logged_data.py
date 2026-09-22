from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


SEED = 42
ENTITY_COUNT = 200
DAYS = 30
EVENT_TYPES = [
    "application_view",
    "profile_update",
    "resume_view",
    "job_view",
    "application_started",
    "application_completed",
    "message_opened",
    "interview_activity",
]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def main() -> None:
    rng = random.Random(SEED)

    start = datetime(
        2026,
        8,
        1,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    records = []

    for index in range(1, ENTITY_COUNT + 1):
        entity_id = f"entity_{index:04d}"

        entity_type = (
            "candidate"
            if index <= int(ENTITY_COUNT * 0.70)
            else "company"
        )

        base_engagement = rng.uniform(0.20, 0.95)
        hiring_relevance = rng.uniform(0.35, 0.98)

        latent_activity = rng.randint(8, 30)

        for day in range(DAYS):
            current_date = start + timedelta(days=day)

            daily_probability = clamp(
                0.10
                + base_engagement * 0.35
                + latent_activity / 150.0
            )

            if rng.random() > daily_probability:
                continue

            event_count = max(
                1,
                int(
                    rng.gauss(
                        1.5 + base_engagement * 4.0,
                        1.2,
                    )
                ),
            )

            for event_index in range(event_count):
                event_time = current_date + timedelta(
                    minutes=rng.randint(0, 1439)
                )

                event_type = rng.choice(EVENT_TYPES)

                engagement_noise = rng.uniform(-0.10, 0.10)

                engagement_score = clamp(
                    base_engagement + engagement_noise
                )

                outcome_signal = (
                    0.15
                    + 0.45 * engagement_score
                    + 0.30 * hiring_relevance
                    + (
                        0.15
                        if event_type
                        in {
                            "application_completed",
                            "interview_activity",
                        }
                        else 0.0
                    )
                    + rng.uniform(-0.15, 0.15)
                )

                outcome_label = int(
                    rng.random() < clamp(outcome_signal)
                )

                records.append(
                    {
                        "event_id": (
                            f"evt_{index:04d}_"
                            f"{day:02d}_"
                            f"{event_index:02d}"
                        ),
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "event_timestamp": event_time.isoformat(),
                        "event_type": event_type,
                        "engagement_score": round(
                            engagement_score,
                            6,
                        ),
                        "hiring_relevance": round(
                            hiring_relevance,
                            6,
                        ),
                        "outcome_label": outcome_label,
                    }
                )

    records.sort(
        key=lambda row: (
            row["event_timestamp"],
            row["entity_id"],
            row["event_id"],
        )
    )

    output_path = Path(
        "phase3/task09/data/demo_logged_data.json"
    )
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "dataset_name": "task09_demo_logged_data",
        "source_type": "synthetic_demo",
        "generation_seed": SEED,
        "warning": (
            "Synthetic fixture for engineering validation only. "
            "It is not production evidence."
        ),
        "records": records,
    }

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            indent=2,
        )

    print("=" * 70)
    print("TASK 09 — DEMO LOG GENERATION")
    print("=" * 70)
    print(f"Rows              : {len(records)}")
    print(f"Entities          : {ENTITY_COUNT}")
    print(f"Days              : {DAYS}")
    print(f"Seed              : {SEED}")
    print(f"Source type       : synthetic_demo")
    print(f"Output            : {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()