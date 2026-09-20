from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "data" / "demo_events.json"

RANDOM_SEED = 42


EVENT_TYPES = [
    "login",
    "profile_view",
    "application_started",
    "application_progress",
    "resume_view",
    "document_upload",
    "search",
    "notification_open",
]


def generate_entity_events(
    entity_id: str,
    entity_type: str,
    start_date: datetime,
    days: int,
    behavior: str,
    rng: random.Random,
) -> list[dict]:
    events: list[dict] = []

    for day_offset in range(days):
        current_day = start_date + timedelta(
            days=day_offset
        )

        if behavior == "active":
            probability = 0.82
            max_events = 5

        elif behavior == "medium":
            probability = 0.52
            max_events = 3

        elif behavior == "churn":
            if day_offset < days * 0.55:
                probability = 0.75
                max_events = 4
            elif day_offset < days * 0.72:
                probability = 0.35
                max_events = 2
            else:
                probability = 0.03
                max_events = 1

        elif behavior == "returning":
            if day_offset < days * 0.35:
                probability = 0.65
                max_events = 3
            elif day_offset < days * 0.70:
                probability = 0.08
                max_events = 1
            else:
                probability = 0.65
                max_events = 3

        else:
            probability = 0.50
            max_events = 2

        if rng.random() > probability:
            continue

        event_count = rng.randint(
            1,
            max_events,
        )

        for _ in range(event_count):
            event_type = rng.choice(
                EVENT_TYPES
            )

            hour = rng.randint(
                8,
                21,
            )

            minute = rng.randint(
                0,
                59,
            )

            timestamp = current_day.replace(
                hour=hour,
                minute=minute,
                second=rng.randint(0, 59),
                microsecond=0,
            )

            events.append(
                {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "timestamp": timestamp.isoformat(),
                    "event_type": event_type,
                }
            )

    return events


def generate_dataset() -> list[dict]:
    rng = random.Random(
        RANDOM_SEED
    )

    start_date = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    all_events: list[dict] = []

    # Candidates
    behaviors = (
        ["active"] * 18
        + ["medium"] * 18
        + ["churn"] * 24
        + ["returning"] * 10
    )

    rng.shuffle(
        behaviors
    )

    for index, behavior in enumerate(
        behaviors,
        start=1,
    ):
        entity_id = (
            f"candidate_{index:03d}"
        )

        all_events.extend(
            generate_entity_events(
                entity_id=entity_id,
                entity_type="candidate",
                start_date=start_date,
                days=120,
                behavior=behavior,
                rng=rng,
            )
        )

    # Companies
    company_behaviors = (
        ["active"] * 8
        + ["medium"] * 8
        + ["churn"] * 10
        + ["returning"] * 4
    )

    rng.shuffle(
        company_behaviors
    )

    for index, behavior in enumerate(
        company_behaviors,
        start=1,
    ):
        entity_id = (
            f"company_{index:03d}"
        )

        all_events.extend(
            generate_entity_events(
                entity_id=entity_id,
                entity_type="company",
                start_date=start_date,
                days=120,
                behavior=behavior,
                rng=rng,
            )
        )

    all_events.sort(
        key=lambda item: (
            item["timestamp"],
            item["entity_type"],
            item["entity_id"],
        )
    )

    return all_events


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    events = generate_dataset()

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            events,
            handle,
            indent=2,
        )

    entities = {
        event["entity_id"]
        for event in events
    }

    print("=" * 72)
    print("TASK 08 — DEMO DATA GENERATION")
    print("=" * 72)
    print()
    print("DATA SOURCE          : SYNTHETIC DEMO")
    print("RANDOM SEED          :", RANDOM_SEED)
    print("EVENTS GENERATED     :", len(events))
    print("ENTITIES GENERATED   :", len(entities))
    print()
    print(
        "IMPORTANT: This dataset is synthetic and is NOT production evidence."
    )
    print()
    print(f"Output               : {OUTPUT_PATH}")
    print()
    print("DEMO DATA GENERATION: PASS")


if __name__ == "__main__":
    main()