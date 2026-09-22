from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .experiment_assignment import (
    AssignmentConfig,
    assign_entity,
)
from .fallback import non_ml_baseline_score
from .model import load_model, predict_probability


@dataclass
class ServingResult:
    entity_id: str
    experiment_id: str
    group: str
    variant: str
    score: float
    fallback_used: bool
    reason: str


class VariantServer:
    """
    Runtime experiment-serving layer.

    Assignment happens at entity level and is deterministic.
    """

    def __init__(
        self,
        model_v1_path: str,
        model_v2_path: str,
        assignment_config: AssignmentConfig | None = None,
    ):
        self.model_v1_path = model_v1_path
        self.model_v2_path = model_v2_path
        self.assignment_config = assignment_config or AssignmentConfig()

        self.model_v1 = None
        self.model_v2 = None

    def load_models(self) -> None:
        self.model_v1 = load_model(self.model_v1_path)
        self.model_v2 = load_model(self.model_v2_path)

    def serve(
        self,
        entity_id: str,
        features: pd.DataFrame,
    ) -> ServingResult:
        assignment = assign_entity(
            entity_id,
            self.assignment_config,
        )

        row = features.copy()

        if len(row) != 1:
            raise ValueError(
                "VariantServer.serve expects exactly one feature row."
            )

        try:
            if assignment["variant"] == "model-v1":
                if self.model_v1 is None:
                    self.load_models()

                score = float(
                    predict_probability(
                        self.model_v1,
                        row,
                        "model-v1",
                    )[0]
                )

                reason = "Control model served."
                fallback = False

            elif assignment["variant"] == "model-v2":
                if self.model_v2 is None:
                    self.load_models()

                score = float(
                    predict_probability(
                        self.model_v2,
                        row,
                        "model-v2",
                    )[0]
                )

                reason = "Challenger model served."
                fallback = False

            else:
                score = float(
                    non_ml_baseline_score(row.iloc[0].to_dict())
                )

                reason = (
                    "Permanent holdout receives non-ML baseline."
                )
                fallback = True

        except Exception as exc:
            score = float(
                non_ml_baseline_score(row.iloc[0].to_dict())
            )

            reason = (
                "Model unavailable; deterministic non-ML fallback used: "
                f"{type(exc).__name__}"
            )
            fallback = True

        return ServingResult(
            entity_id=str(entity_id),
            experiment_id=assignment["experiment_id"],
            group=assignment["group"],
            variant=assignment["variant"],
            score=score,
            fallback_used=fallback,
            reason=reason,
        )


def result_to_dict(result: ServingResult) -> dict[str, Any]:
    return {
        "entity_id": result.entity_id,
        "experiment_id": result.experiment_id,
        "group": result.group,
        "variant": result.variant,
        "score": result.score,
        "fallback_used": result.fallback_used,
        "reason": result.reason,
    }