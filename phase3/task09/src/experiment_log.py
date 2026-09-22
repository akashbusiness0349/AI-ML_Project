from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .data_ingestion import save_json


def build_experiment_log(
    experiment_id: str,
    source_type: str,
    control_metrics: dict[str, Any],
    challenger_metrics: dict[str, Any],
    allocation: dict[str, Any],
    guardrail_result: dict[str, Any],
    expected_online_effect: dict[str, Any],
    evaluation_window_days: int,
) -> dict[str, Any]:
    control_ap = float(
        control_metrics.get("average_precision", 0.0)
    )
    challenger_ap = float(
        challenger_metrics.get("average_precision", 0.0)
    )

    return {
        "experiment_id": experiment_id,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_type": source_type,
        "evaluation_window_days": evaluation_window_days,
        "model_versions": {
            "control": "model-v1",
            "challenger": "model-v2",
            "permanent_holdout": "non_ml_baseline",
        },
        "traffic_allocation": allocation,
        "offline_metrics": {
            "control": control_metrics,
            "challenger": challenger_metrics,
            "average_precision_gap": challenger_ap - control_ap,
        },
        "expected_online_effect": expected_online_effect,
        "guardrails": guardrail_result,
        "decision": guardrail_result.get(
            "decision",
            "UNKNOWN",
        ),
        "reproducibility": {
            "assignment_is_deterministic": True,
            "assignment_is_entity_level": True,
            "future_outcome_used_as_feature": False,
        },
    }


def write_experiment_log(
    payload: dict[str, Any],
    path: str | Path,
) -> None:
    save_json(payload, path)