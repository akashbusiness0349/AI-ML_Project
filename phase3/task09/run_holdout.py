from __future__ import annotations

import argparse

from src.data_ingestion import load_logged_data, save_json
from src.holdout import (
    assign_entities,
    entity_allocation_summary,
    verify_stability,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    frame = load_logged_data(args.data)
    assigned = assign_entities(frame)

    allocation = entity_allocation_summary(assigned)

    entity_ids = (
        assigned["entity_id"]
        .drop_duplicates()
        .astype(str)
        .tolist()
    )

    stability = verify_stability(entity_ids)

    result = {
        "status": (
            "PASS"
            if stability["status"] == "PASS"
            else "FAIL"
        ),
        "allocation": allocation,
        "stability": stability,
        "policy": {
            "control": "model-v1",
            "challenger": "model-v2",
            "permanent_holdout": "non_ml_baseline",
        },
        "purpose": (
            "The permanent holdout receives the non-ML baseline so "
            "cumulative model value can be measured against a stable "
            "non-model reference."
        ),
    }

    output = "phase3/task09/logs/holdout_validation.json"

    save_json(result, output)

    print("=" * 70)
    print("TASK 09 — PERMANENT HOLDOUT")
    print("=" * 70)
    print(f"Status              : {result['status']}")
    print(
        f"Unique entities     : "
        f"{allocation['unique_entities']}"
    )

    for group, percentage in allocation["percentages"].items():
        print(
            f"{group:<22}: {percentage:.2f}%"
        )

    print(
        f"Assignment stability: "
        f"{stability['status']}"
    )
    print(f"Evidence            : {output}")
    print("=" * 70)

    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()