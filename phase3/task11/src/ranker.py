from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Mapping

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from .features import build_feature_vector
from .position_bias import (
    apply_position_bias_weights,
)


class PairwiseLTR:
    """
    Pairwise Learning-to-Rank model.

    The model is trained on feature differences:

        X_pair = features(item_a) - features(item_b)

    Label:
        1 -> item_a should rank above item_b
        0 -> item_a should rank below item_b

    For every positive/negative logged pair, both orientations
    are created so the classifier contains both classes.
    """

    def __init__(self) -> None:
        self.model = LogisticRegression(
            max_iter=2000,
            class_weight=None,
            random_state=42,
        )

        self.feature_names = [
            "experience_match",
            "job_popularity",
            "location_match",
            "skill_overlap",
        ]

        self.fitted = False

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weight: np.ndarray | None = None,
    ) -> None:
        unique_classes = np.unique(y)

        if len(unique_classes) < 2:
            raise ValueError(
                "Pairwise LTR training requires both label classes "
                "0 and 1. Received classes: "
                f"{unique_classes.tolist()}"
            )

        self.model.fit(
            X,
            y,
            sample_weight=sample_weight,
        )

        self.fitted = True

    def score_features(
        self,
        features: list[float],
    ) -> float:
        if not self.fitted:
            raise RuntimeError(
                "LTR model is not fitted."
            )

        X = np.asarray(
            [features],
            dtype=float,
        )

        return float(
            self.model.decision_function(X)[0]
        )

    def score(
        self,
        candidate: Mapping,
        job: Mapping,
    ) -> float:
        features = build_feature_vector(
            candidate,
            job,
        )

        return self.score_features(
            features
        )

    def predict_proba(
        self,
        candidate: Mapping,
        job: Mapping,
    ) -> float:
        if not self.fitted:
            raise RuntimeError(
                "LTR model is not fitted."
            )

        features = build_feature_vector(
            candidate,
            job,
        )

        X = np.asarray(
            [features],
            dtype=float,
        )

        return float(
            self.model.predict_proba(X)[0][1]
        )


def _group_by_session(
    interactions: list[Mapping],
) -> dict[str, list[Mapping]]:
    """
    Group logged impressions by session.
    """

    groups = defaultdict(list)

    for row in interactions:
        session_id = row.get("session_id")

        if session_id is None:
            continue

        groups[
            session_id
        ].append(row)

    return dict(groups)


def build_pairwise_dataset(
    interactions: list[Mapping],
    candidates: Mapping[str, Mapping],
    jobs: Mapping[str, Mapping],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """
    Build a pairwise LTR training dataset.

    For every session containing at least one positive and one
    negative impression:

        positive - negative -> label 1
        negative - positive -> label 0

    Creating both orientations is important because the model
    is implemented using binary logistic regression. Without the
    reverse orientation, y would contain only class 1 and
    LogisticRegression would fail during training.

    Position-bias weights are applied to both orientations.
    """

    X = []
    y = []
    weights = []

    groups = _group_by_session(
        interactions
    )

    position_weights, propensity_table = (
        apply_position_bias_weights(
            interactions
        )
    )

    weight_lookup = {
        id(row): weight
        for row, weight in zip(
            interactions,
            position_weights,
        )
    }

    pair_count = 0
    pairwise_examples = 0
    pairable_sessions = 0

    for session_id, events in groups.items():

        positives = [
            row
            for row in events
            if float(
                row.get("relevance", 0)
            ) > 0
        ]

        negatives = [
            row
            for row in events
            if float(
                row.get("relevance", 0)
            ) <= 0
        ]

        if not positives or not negatives:
            continue

        pairable_sessions += 1

        for positive in positives:

            candidate_id = positive[
                "candidate_id"
            ]

            candidate = candidates.get(
                candidate_id
            )

            if candidate is None:
                continue

            positive_job = jobs.get(
                positive["job_id"]
            )

            if positive_job is None:
                continue

            positive_features = np.asarray(
                build_feature_vector(
                    candidate,
                    positive_job,
                ),
                dtype=float,
            )

            positive_weight = float(
                weight_lookup.get(
                    id(positive),
                    1.0,
                )
            )

            for negative in negatives:

                negative_job = jobs.get(
                    negative["job_id"]
                )

                if negative_job is None:
                    continue

                negative_features = np.asarray(
                    build_feature_vector(
                        candidate,
                        negative_job,
                    ),
                    dtype=float,
                )

                negative_weight = float(
                    weight_lookup.get(
                        id(negative),
                        1.0,
                    )
                )

                pair_weight = (
                    positive_weight
                    + negative_weight
                ) / 2.0

                # ==================================================
                # ORIENTATION 1
                # Positive item should rank above negative item.
                #
                # positive - negative -> class 1
                # ==================================================

                difference = (
                    positive_features
                    - negative_features
                )

                X.append(
                    difference
                )

                y.append(1)

                weights.append(
                    pair_weight
                )

                # ==================================================
                # ORIENTATION 2
                # Negative item should rank below positive item.
                #
                # negative - positive -> class 0
                #
                # This gives LogisticRegression the second class.
                # ==================================================

                reverse_difference = (
                    negative_features
                    - positive_features
                )

                X.append(
                    reverse_difference
                )

                y.append(0)

                weights.append(
                    pair_weight
                )

                pair_count += 1
                pairwise_examples += 2

    if not X:
        raise ValueError(
            "No pairwise training examples could be created. "
            "Check that sessions contain both positive and "
            "negative impressions."
        )

    unique_labels = sorted(
        set(y)
    )

    if unique_labels != [0, 1]:
        raise ValueError(
            "Invalid pairwise label distribution. "
            f"Expected [0, 1], received {unique_labels}."
        )

    X_array = np.asarray(
        X,
        dtype=float,
    )

    y_array = np.asarray(
        y,
        dtype=int,
    )

    weights_array = np.asarray(
        weights,
        dtype=float,
    )

    metadata = {
        "sessions": len(groups),
        "pairable_sessions": pairable_sessions,
        "pair_count": pair_count,
        "pairwise_training_examples": pairwise_examples,
        "positive_pair_examples": int(
            np.sum(y_array == 1)
        ),
        "negative_pair_examples": int(
            np.sum(y_array == 0)
        ),
        "label_classes": unique_labels,
        "position_bias_correction": True,
        "propensity_positions": len(
            propensity_table
        ),
    }

    return (
        X_array,
        y_array,
        weights_array,
        metadata,
    )


def train_pairwise_model(
    interactions: list[Mapping],
    candidates: Mapping[str, Mapping],
    jobs: Mapping[str, Mapping],
) -> dict:
    """
    Train the pairwise LTR model.
    """

    X, y, weights, metadata = (
        build_pairwise_dataset(
            interactions,
            candidates,
            jobs,
        )
    )

    model = PairwiseLTR()

    model.fit(
        X,
        y,
        sample_weight=weights,
    )

    return {
        "model": model,
        "training_metadata": metadata,
        "feature_count": X.shape[1],
        "training_examples": X.shape[0],
        "label_distribution": {
            "class_0": int(
                np.sum(y == 0)
            ),
            "class_1": int(
                np.sum(y == 1)
            ),
        },
    }


def rank_jobs_ltr(
    model: PairwiseLTR,
    candidate: Mapping,
    jobs: list[Mapping],
) -> list[dict]:
    """
    Rank jobs for a candidate using the trained LTR model.
    """

    ranked = []

    for job in jobs:

        score = model.score(
            candidate,
            job,
        )

        probability = model.predict_proba(
            candidate,
            job,
        )

        ranked.append(
            {
                "job_id": job["job_id"],
                "score": float(
                    score
                ),
                "probability": float(
                    probability
                ),
            }
        )

    ranked.sort(
        key=lambda x: (
            -x["score"],
            x["job_id"],
        )
    )

    for position, row in enumerate(
        ranked,
        start=1,
    ):
        row["position"] = position

    return ranked


def save_model(
    model: PairwiseLTR,
    path: str | Path,
) -> None:
    """
    Persist trained LTR model.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        path,
    )


def load_model(
    path: str | Path,
) -> PairwiseLTR:
    """
    Load persisted LTR model.
    """

    return joblib.load(
        path
    )