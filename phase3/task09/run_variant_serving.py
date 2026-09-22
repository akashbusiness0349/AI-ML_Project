from __future__ import annotations

import argparse

import pandas as pd

from src.data_ingestion import load_logged_data, save_json
from src.experiment_assignment import AssignmentConfig, assign_entity
from src.holdout import assign_entities
from src.variant_serving import VariantServer, result_to_dict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        required=True,
    )
    args = parser.parse_args()

    frame = load_logged_data(args.data)

    assigned = assign_entities(frame)

    entities = (
        assigned[
            [
                "entity_id",
                "experiment_group",
            ]
        ]
        .drop_duplicates("entity_id")
    )

    server = VariantServer(
        model_v1_path=(
            "phase3/task09/models/model-v1.joblib"
        ),
        model_v2_path=(
            "phase3/task09/models/model-v2.joblib"
        ),
        assignment_config=AssignmentConfig(),
    )

    demonstrations = []

    for _, entity in entities.head(20).iterrows():
        entity_id = str(entity["entity_id"])

        rows = assigned[
            assigned["entity_id"] == entity_id
        ]

        row = rows.iloc[[0]].copy()

        first = server.serve(
            entity_id,
            row,
        )

        second = server.serve(
            entity_id,
            row,
        )

        if first.variant != second.variant:
            raise AssertionError(
                f"Variant changed for {entity_id}."
            )

        demonstrations.append(
            {
                "first_request": result_to_dict(first),
                "second_request": result_to_dict(second),
                "stable_assignment": (
                    first.variant == second.variant
                ),
            }
        )

    result = {
        "status": "PASS",
        "entities_demonstrated": len(demonstrations),
        "stable_assignment_verified": all(
            item["stable_assignment"]
            for item in demonstrations
        ),
        "traffic_policy": {
            "control": "80%",
            "challenger": "10%",
            "permanent_holdout": "10%",
        },
        "demonstrations": demonstrations,
    }

    output = (
        "phase3/task09/logs/"
        "variant_serving_demo.json"
    )

    save_json(result, output)

    print("=" * 70)
    print("TASK 09 — LIVE VARIANT SERVING")
    print("=" * 70)
    print(
        f"Status              : {result['status']}"
    )
    print(
        f"Entities demonstrated: "
        f"{result['entities_demonstrated']}"
    )
    print(
        f"Stable assignment   : "
        f"{result['stable_assignment_verified']}"
    )
    print(
        "Control             : model-v1"
    )
    print(
        "Challenger          : model-v2"
    )
    print(
        "Permanent holdout   : non-ML baseline"
    )
    print(
        f"Evidence            : {output}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()