from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# MODEL FEATURE CONTRACT
# ============================================================

FEATURES_V1 = [
    "engagement_score",
    "events_1d",
    "events_7d",
    "events_14d",
    "days_since_last_event",
    "hiring_relevance",
]


FEATURES_V2 = [
    "engagement_score",
    "events_1d",
    "events_7d",
    "events_14d",
    "days_since_last_event",
    "hiring_relevance",
    "engagement_velocity",
    "activity_intensity_7d",
]


# ============================================================
# MODEL SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class ModelSpec:
    version: str
    features: tuple[str, ...]
    regularization_c: float
    random_state: int = 42


MODEL_SPECS = {
    "model-v1": ModelSpec(
        version="model-v1",
        features=tuple(FEATURES_V1),
        regularization_c=1.0,
        random_state=42,
    ),
    "model-v2": ModelSpec(
        version="model-v2",
        features=tuple(FEATURES_V2),
        regularization_c=0.35,
        random_state=42,
    ),
}


# ============================================================
# MODEL CONSTRUCTION
# ============================================================

def build_model(version: str) -> Pipeline:
    """
    Build a reproducible model variant.
    """

    if version not in MODEL_SPECS:
        raise ValueError(
            f"Unknown model version: {version}"
        )

    spec = MODEL_SPECS[version]

    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=spec.regularization_c,
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=spec.random_state,
                ),
            ),
        ]
    )


# ============================================================
# TRAINING
# ============================================================

def train_model(
    frame: pd.DataFrame,
    version: str,
    target_column: str = "outcome_label",
) -> Pipeline:
    """
    Train a model variant.

    Important:
    The caller must provide a temporally separated training set.
    Future outcome information must never be included in features.
    """

    if version not in MODEL_SPECS:
        raise ValueError(
            f"Unknown model version: {version}"
        )

    spec = MODEL_SPECS[version]

    missing_features = (
        set(spec.features) - set(frame.columns)
    )

    if missing_features:
        raise ValueError(
            f"{version} requires missing features: "
            f"{sorted(missing_features)}"
        )

    if target_column not in frame.columns:
        raise ValueError(
            f"Missing target column: {target_column}"
        )

    X = frame.loc[:, spec.features].copy()
    y = frame[target_column].astype(int)

    if y.nunique() < 2:
        raise ValueError(
            f"{version} training target must contain "
            "both classes 0 and 1."
        )

    model = build_model(version)

    model.fit(X, y)

    return model


# ============================================================
# PREDICTION
# ============================================================

def predict_probability(
    model: Pipeline,
    frame: pd.DataFrame,
    version: str,
) -> np.ndarray:
    """
    Return positive-class probability for one model variant.
    """

    if version not in MODEL_SPECS:
        raise ValueError(
            f"Unknown model version: {version}"
        )

    spec = MODEL_SPECS[version]

    missing_features = (
        set(spec.features) - set(frame.columns)
    )

    if missing_features:
        raise ValueError(
            f"{version} prediction requires missing features: "
            f"{sorted(missing_features)}"
        )

    X = frame.loc[:, spec.features]

    return model.predict_proba(X)[:, 1]


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    model: Pipeline,
    frame: pd.DataFrame,
    version: str,
    target_column: str = "outcome_label",
) -> dict[str, Any]:
    """
    Evaluate Average Precision on a held-out dataset.
    """

    probabilities = predict_probability(
        model,
        frame,
        version,
    )

    labels = (
        frame[target_column]
        .astype(int)
        .to_numpy()
    )

    if len(np.unique(labels)) < 2:
        average_precision = 0.0
    else:
        average_precision = float(
            average_precision_score(
                labels,
                probabilities,
            )
        )

    return {
        "model_version": version,
        "average_precision": average_precision,
        "rows": int(len(frame)),
        "positive_rate": float(labels.mean()),
    }


# ============================================================
# PERSISTENCE
# ============================================================

def save_model(
    model: Pipeline,
    path: str | Path,
) -> None:
    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        output_path,
    )


def load_model(
    path: str | Path,
) -> Pipeline:
    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {model_path}"
        )

    return joblib.load(model_path)
