import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
PATH = LOGS / "preregistration.json"


PREREGISTRATION = {
    "task": "Phase 3 Task 10",
    "experiment_name": "Disengagement Risk A/B Replay",
    "version": "1.0",
    "hypothesis": (
        "The treatment model will identify higher-risk users more effectively "
        "than the non-ML recency baseline on held-out logged data."
    ),
    "primary_metric": "heldout_model_average_precision",
    "secondary_online_metric": "14_day_churn_rate",
    "alpha": 0.05,
    "minimum_relative_effect": 0.05,
    "minimum_effect_basis": (
        "A 5% relative effect is the preregistered minimum practical effect "
        "for the replay comparison."
    ),
    "train_validation_holdout": "60/20/20 chronological split",
    "baseline": "non_ml_recency",
    "assignment": "deterministic_sha256_entity_assignment",
    "ship_rule": (
        "Production shipment requires preregistered statistical guardrails "
        "AND genuine production/live causal evidence."
    ),
    "online_validation_requirement": (
        "Offline replay cannot establish causal online intervention impact."
    ),
    "data_policy": (
        "Current verified dataset is synthetic_demo and must not be presented "
        "as production evidence."
    ),
}


def main():
    LOGS.mkdir(parents=True, exist_ok=True)

    if PATH.exists():
        with open(PATH, encoding="utf-8") as f:
            existing = json.load(f)

        if existing != PREREGISTRATION:
            raise RuntimeError(
                "LOCKED PREREGISTRATION MISMATCH. "
                "Do not overwrite preregistration after experiment results."
            )

        print("PREREGISTRATION: ALREADY LOCKED")
        print(PATH)
        return

    payload = dict(PREREGISTRATION)
    payload["registered_at_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            indent=2,
        )

    print("PREREGISTRATION: CREATED AND LOCKED")
    print(PATH)


if __name__ == "__main__":
    main()