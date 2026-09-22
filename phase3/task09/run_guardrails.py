from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data_ingestion import save_json
from src.guardrails import (
    GuardrailConfig,
    evaluate_guardrails,
)


TASK_ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--predictions",
        default=str(
            TASK_ROOT / "logs" / "experiment_predictions.csv"
        ),
    )

    args = parser.parse_args()

    prediction_path = Path(args.predictions)

    if not prediction_path.exists():
        raise FileNotFoundError(
            f"Predictions file not found: {prediction_path}"
        )

    frame = pd.read_csv(prediction_path)

    challenger = frame[
        frame["experiment_group"] == "challenger"
    ].copy()

    config = GuardrailConfig(
        minimum_hiring_relevance=0.70,
        minimum_average_precision=0.05,
        maximum_error_rate=0.35,
        minimum_rows=20,
    )

    result = evaluate_guardrails(
        challenger,
        config,
    )

    evidence_path = TASK_ROOT / "logs" / "guardrail_result.json"

    save_json(
        result,
        evidence_path,
    )

    print("=" * 70)
    print("TASK 09 — GUARDRAILS")
    print("=" * 70)
    print(f"Challenger rows     : {len(challenger)}")
    print(f"Decision            : {result['decision']}")
    print(f"Reason              : {result['reason']}")

    if result.get("failed_guardrails"):
        print("\nFailed guardrails:")
        for item in result["failed_guardrails"]:
            print(f" - {item}")

    print()
    print("Rule                : challenger breach => HALT_CHALLENGER")
    print("Safe degradation    : CONTROL_MODEL_CONTINUES")
    print(f"Evidence            : {evidence_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
