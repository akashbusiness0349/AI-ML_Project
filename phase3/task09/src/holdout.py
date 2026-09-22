from __future__ import annotations

from typing import Any

import pandas as pd

from .experiment_assignment import (
    AssignmentConfig,
    assign_entity,
)


def assign_entities(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Add stable experiment membership to event-level data.
    """
    config = AssignmentConfig()

    assignments = [
        assign_entity(entity_id, config)
        for entity_id in frame["entity_id"].astype(str)
    ]

    result = frame.copy()

    result["experiment_bucket"] = [
        item["bucket"] for item in assignments
    ]
    result["experiment_group"] = [
        item["group"] for item in assignments
    ]
    result["experiment_variant"] = [
        item["variant"] for item in assignments
    ]

    return result


def entity_allocation_summary(frame: pd.DataFrame) -> dict[str, Any]:
    """
    Measure allocation at unique-entity level, not event level.
    """
    entity_frame = (
        frame[
            [
                "entity_id",
                "experiment_bucket",
                "experiment_group",
                "experiment_variant",
            ]
        ]
        .drop_duplicates("entity_id")
    )

    counts = (
        entity_frame["experiment_group"]
        .value_counts()
        .to_dict()
    )

    total = len(entity_frame)

    return {
        "unique_entities": int(total),
        "counts": {
            key: int(value)
            for key, value in counts.items()
        },
        "percentages": {
            key: round((value / total) * 100, 4)
            for key, value in counts.items()
        },
    }


def verify_stability(entity_ids: list[str]) -> dict[str, Any]:
    config = AssignmentConfig()

    observations: dict[str, set[str]] = {}

    for entity_id in entity_ids:
        assignments = [
            assign_entity(entity_id, config)["group"]
            for _ in range(5)
        ]
        observations[entity_id] = set(assignments)

    unstable = [
        entity_id
        for entity_id, groups in observations.items()
        if len(groups) != 1
    ]

    return {
        "status": "PASS" if not unstable else "FAIL",
        "entities_checked": len(entity_ids),
        "unstable_entities": unstable,
    }