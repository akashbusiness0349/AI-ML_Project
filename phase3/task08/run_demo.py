from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.explainability import (
    explain_prediction,
)
from src.model import (
    load_model,
)
from src.risk_prioritization import (
    build_at_risk_list,
)


ROOT = Path(__file__).resolve().parent

MODEL_PATH = (
    ROOT
    / "models"
    / "churn_model.joblib"
)

FEATURE_PATH = (
    ROOT
    / "logs"
    / "feature_table.csv"
)

THRESHOLD_PATH = (
    ROOT
    / "logs"
    / "operating_threshold.json"
)

AT_RISK_PATH = (
    ROOT
    / "logs"
    / "at_risk_users.csv"
)

DEMO_PATH = (
    ROOT
    / "logs"
    / "demo_output.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Task 08 at-risk demo."
    )

    parser.add_argument(
        "--source-type",
        default="synthetic_demo",
        choices=[
            "synthetic_demo",
            "production",
        ],
    )

    return parser.parse_args()


def load_threshold() -> float:
    with THRESHOLD_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        payload = json.load(
            handle
        )

    return float(
        payload["threshold"]
    )


def main() -> None:
    args = parse_args()

    print("=" * 72)
    print(
        "PHASE 3 / TASK 08 — AT-RISK USER DEMO"
    )
    print("=" * 72)

    print(
        f"Data source           : "
        f"{args.source_type}"
    )

    artifact = load_model(
        MODEL_PATH
    )

    threshold = load_threshold()

    feature_table = pd.read_csv(
        FEATURE_PATH,
        parse_dates=[
            "prediction_time",
            "future_horizon_end",
        ],
    )

    feature_columns = artifact[
        "feature_columns"
    ]

    latest_rows = (
        feature_table
        .sort_values(
            "prediction_time"
        )
        .groupby(
            "entity_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    probabilities = (
        artifact[
            "model"
        ].predict_proba(
            latest_rows[
                feature_columns
            ]
        )[:, 1]
    )

    latest_rows[
        "churn_probability"
    ] = probabilities

    latest_rows[
        "model_prediction"
    ] = (
        probabilities >= threshold
    ).astype(int)

    explanations = []

    for _, row in latest_rows.iterrows():
        explanations.append(
            explain_prediction(
                row,
                float(
                    row[
                        "churn_probability"
                    ]
                ),
            )
        )

    at_risk = build_at_risk_list(
        latest_rows,
        explanations,
    )

    at_risk.to_csv(
        AT_RISK_PATH,
        index=False,
    )

    demo_payload = {
        "status": "success",
        "data_source_type": args.source_type,
        "production_evidence_status": (
            "NOT_PRODUCTION_EVIDENCE"
            if args.source_type
            == "synthetic_demo"
            else "PRODUCTION_DATA"
        ),
        "model_version": artifact[
            "model_version"
        ],
        "operating_threshold": threshold,
        "entities_scored": len(
            latest_rows
        ),
        "at_risk_entities": len(
            at_risk
        ),
        "fallback_available": True,
        "sample_worked_example": None,
    }

    if not at_risk.empty:
        sample = at_risk.iloc[
            0
        ].to_dict()

        demo_payload[
            "sample_worked_example"
        ] = sample

        print()
        print(
            "===== WORKED EXAMPLE ====="
        )

        print(
            f"Entity                : "
            f"{sample['entity_id']}"
        )

        print(
            f"Entity type           : "
            f"{sample['entity_type']}"
        )

        print(
            f"Risk probability      : "
            f"{sample['risk_probability']}"
        )

        print(
            f"Risk segment          : "
            f"{sample['risk_segment']}"
        )

        print(
            f"Reason                : "
            f"{sample['reason']}"
        )

        print(
            f"Growth action         : "
            f"{sample['recommended_action']}"
        )

    else:
        print()
        print(
            "No HIGH/MEDIUM risk entities "
            "were produced."
        )

    with DEMO_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            demo_payload,
            handle,
            indent=2,
            default=str,
        )

    print()
    print(
        "===== GROWTH HANDOFF ====="
    )

    print(
        f"Entities scored       : "
        f"{len(latest_rows)}"
    )

    print(
        f"At-risk entities      : "
        f"{len(at_risk)}"
    )

    print(
        f"Operating threshold   : "
        f"{threshold:.6f}"
    )

    print(
        f"At-risk CSV           : "
        f"{AT_RISK_PATH}"
    )

    print(
        f"Demo evidence         : "
        f"{DEMO_PATH}"
    )

    print()
    print(
        "LIVE DEMO: PASS"
    )


if __name__ == "__main__":
    main()