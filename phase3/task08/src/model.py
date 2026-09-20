from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_VERSION = "task08-logistic-regression-v1"


def build_model() -> Pipeline:
    """
    Build a transparent probability model.

    Logistic regression is deliberately used because it is:
    - probabilistic
    - lightweight
    - reproducible
    - explainable
    - suitable for a first production baseline
    """

    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def train_model(
    train_data: pd.DataFrame,
    feature_columns: list[str],
) -> Pipeline:
    if train_data.empty:
        raise ValueError("Training dataset is empty.")

    if train_data["churn_label"].nunique() < 2:
        raise ValueError(
            "Training data contains only one class. "
            "Both churn=0 and churn=1 are required."
        )

    model = build_model()

    model.fit(
        train_data[feature_columns],
        train_data["churn_label"].astype(int),
    )

    return model


def save_model(
    model: Pipeline,
    path: str | Path,
    feature_columns: list[str],
    metadata: dict | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "feature_columns": feature_columns,
        "model_version": MODEL_VERSION,
        "metadata": metadata or {},
    }

    joblib.dump(
        artifact,
        path,
    )


def load_model(
    path: str | Path,
) -> dict:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {path}"
        )

    artifact = joblib.load(path)

    required_keys = {
        "model",
        "feature_columns",
        "model_version",
    }

    missing = required_keys - set(artifact.keys())

    if missing:
        raise ValueError(
            "Model artifact is incomplete. Missing: "
            + ", ".join(sorted(missing))
        )

    return artifact


def predict_risk(
    artifact: dict,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    missing = set(feature_columns) - set(dataframe.columns)

    if missing:
        raise ValueError(
            "Prediction data is missing feature columns: "
            + ", ".join(sorted(missing))
        )

    probabilities = model.predict_proba(
        dataframe[feature_columns]
    )[:, 1]

    result = dataframe.copy()

    result["churn_probability"] = probabilities
    result["model_prediction"] = (
        probabilities >= 0.5
    ).astype(int)

    return result