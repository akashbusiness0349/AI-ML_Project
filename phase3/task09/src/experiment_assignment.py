from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class AssignmentConfig:
    experiment_id: str = "task09-model-experiment-v1"
    salt: str = "task09-stable-assignment-v1"

    holdout_start: int = 0
    holdout_end: int = 9

    challenger_start: int = 10
    challenger_end: int = 19

    # Buckets 20..99 = control.
    bucket_count: int = 100


def stable_bucket(
    entity_id: str,
    config: AssignmentConfig,
) -> int:
    """
    Stable deterministic bucket.

    SHA-256 ensures the same entity receives the same bucket
    across requests and process restarts.
    """
    raw = (
        f"{config.experiment_id}|"
        f"{config.salt}|"
        f"{entity_id}"
    ).encode("utf-8")

    digest = hashlib.sha256(raw).hexdigest()
    integer = int(digest[:16], 16)

    return integer % config.bucket_count


def assign_entity(
    entity_id: str,
    config: AssignmentConfig | None = None,
) -> dict:
    config = config or AssignmentConfig()

    bucket = stable_bucket(entity_id, config)

    if config.holdout_start <= bucket <= config.holdout_end:
        group = "permanent_holdout"
        variant = "non_ml_baseline"
    elif config.challenger_start <= bucket <= config.challenger_end:
        group = "challenger"
        variant = "model-v2"
    else:
        group = "control"
        variant = "model-v1"

    return {
        "experiment_id": config.experiment_id,
        "entity_id": str(entity_id),
        "bucket": bucket,
        "group": group,
        "variant": variant,
    }


def traffic_split(config: AssignmentConfig | None = None) -> dict:
    config = config or AssignmentConfig()

    holdout = config.holdout_end - config.holdout_start + 1
    challenger = config.challenger_end - config.challenger_start + 1
    control = config.bucket_count - holdout - challenger

    return {
        "control_percent": control / config.bucket_count,
        "challenger_percent": challenger / config.bucket_count,
        "holdout_percent": holdout / config.bucket_count,
    }