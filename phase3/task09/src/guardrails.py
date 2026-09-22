from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .metrics import average_precision


@dataclass(frozen=True)
class GuardrailConfig:
    minimum_hiring_relevance: float = 0.70
    minimum_average_precision: float = 0.05
    maximum_error_rate: float = 0.35
    minimum_rows: int = 20


def evaluate_guardrails(
    challenger_frame: pd.DataFrame,
    config: GuardrailConfig | None = None,
) -> dict[str, Any]:
    config = config or GuardrailConfig()

    if len(challenger_frame) < config.minimum_rows:
        return {
            "decision": "HALT_CHALLENGER",
            "reason": "INSUFFICIENT_TRAFFIC",
            "guardrails": {},
        }

    labels = challenger_frame["outcome_label"].astype(int)
    scores = challenger_frame["prediction_score"].astype(float)

    hiring_relevance_rate = float(
        challenger_frame["hiring_relevance"].mean()
    )

    ap = average_precision(labels, scores)

    predictions = (scores >= 0.5).astype(int)
    error_rate = float(
        (predictions != labels).mean()
    )

    checks = {
        "hiring_relevance_floor": {
            "observed": hiring_relevance_rate,
            "threshold": config.minimum_hiring_relevance,
            "passed": (
                hiring_relevance_rate
                >= config.minimum_hiring_relevance
            ),
        },
        "average_precision_floor": {
            "observed": ap,
            "threshold": config.minimum_average_precision,
            "passed": ap >= config.minimum_average_precision,
        },
        "error_rate_ceiling": {
            "observed": error_rate,
            "threshold": config.maximum_error_rate,
            "passed": error_rate <= config.maximum_error_rate,
        },
    }

    failed = [
        name
        for name, check in checks.items()
        if not check["passed"]
    ]

    if failed:
        decision = "HALT_CHALLENGER"
        reason = "GUARDRAIL_BREACH"
    else:
        decision = "CONTINUE_CHALLENGER"
        reason = "ALL_GUARDRAILS_PASSED"

    return {
        "decision": decision,
        "reason": reason,
        "failed_guardrails": failed,
        "guardrails": checks,
    }