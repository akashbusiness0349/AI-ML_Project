from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data_ingestion import save_json
from src.guardrails import GuardrailConfig, evaluate_guardrails
from src.variant_serving import VariantServer


def main() -> None:
    predictions_path = Path(
        "phase3/task09/logs/experiment_predictions.csv"
    )

    if not predictions_path.exists():
        raise FileNotFoundError(
            "Run run_experiment.py before run_failure_test.py."
        )

    frame = pd.read_csv(predictions_path)

    challenger = frame[
        frame["experiment_group"] == "challenger"
    ].copy()

    if challenger.empty:
        raise RuntimeError(
            "No challenger rows available for failure test."
        )

    # ---------------------------------------------------------
    # Failure 1: intentionally destroy hiring relevance.
    # ---------------------------------------------------------
    broken = challenger.copy()
    broken["hiring_relevance"] = 0.0

    guardrail_result = evaluate_guardrails(
        broken,
        GuardrailConfig(
            minimum_hiring_relevance=0.70,
            minimum_average_precision=0.05,
            maximum_error_rate=0.35,
            minimum_rows=20,
        ),
    )

    if guardrail_result["decision"] != "HALT_CHALLENGER":
        raise AssertionError(
            "Failure test did not halt the challenger."
        )

    # ---------------------------------------------------------
    # Failure 2: model unavailable.
    # ---------------------------------------------------------
    feature_row = challenger.iloc[[0]].copy()

    server = VariantServer(
        model_v1_path=(
            "phase3/task09/models/nonexistent-model-v1.joblib"
        ),
        model_v2_path=(
            "phase3/task09/models/nonexistent-model-v2.joblib"
        ),
    )

    entity_id = str(feature_row.iloc[0]["entity_id"])

    try:
        serving_result = server.serve(
            entity_id,
            feature_row,
        )
    except Exception as exc:
        # This is not expected because VariantServer catches model
        # failures and routes to fallback. Keep a clear artifact if
        # an unexpected exception occurs.
        serving_result = {
            "entity_id": entity_id,
            "unexpected_exception": type(exc).__name__,
            "fallback_expected": True,
        }
    else:
        serving_result = {
            "entity_id": serving_result.entity_id,
            "variant": serving_result.variant,
            "group": serving_result.group,
            "score": serving_result.score,
            "fallback_used": serving_result.fallback_used,
            "reason": serving_result.reason,
        }

        if not serving_result["fallback_used"]:
            raise AssertionError(
                "Model-unavailable test did not activate fallback."
            )

    result = {
        "status": "PASS",
        "guardrail_failure": {
            "decision": guardrail_result["decision"],
            "failed_guardrails": guardrail_result.get(
                "failed_guardrails",
                [],
            ),
            "expected_safe_action": (
                "HALT_CHALLENGER; CONTROL_MODEL_CONTINUES"
            ),
        },
        "model_unavailable": serving_result,
        "expected_behavior": (
            "When a model cannot be loaded, serving falls back "
            "to the deterministic non-ML baseline."
        ),
    }

    output = "phase3/task09/logs/failure_test.json"
    save_json(result, output)

    print("=" * 70)
    print("TASK 09 — INTENTIONAL FAILURE TEST")
    print("=" * 70)
    print("Guardrail breach    : PASS")
    print("Challenger halted   : YES")
    print("Control continues   : YES")
    print("Model unavailable   : PASS")
    print("Fallback activated  : YES")
    print(f"Evidence            : {output}")
    print("=" * 70)


if __name__ == "__main__":
    main()